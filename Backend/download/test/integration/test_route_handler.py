import io
import json
import os
import sys
import zipfile
from pathlib import Path
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import boto3
from moto import mock_aws

import Manager.manager as manager
from DAO.dao import list_photo_keys
from routeHandler import lambda_handler


class _FakeLambdaContext:
    function_name = "download"
    memory_limit_in_mb = 128
    invoked_function_arn = "arn:aws:lambda:ap-south-1:000000000000:function:download"
    aws_request_id = "test-request-id"


def _api_event(http_method, path, body=None, claims=None):
    return {
        "resource": path,
        "path": path,
        "httpMethod": http_method,
        "headers": {"Content-Type": "application/json"},
        "multiValueHeaders": {},
        "queryStringParameters": None,
        "multiValueQueryStringParameters": None,
        "pathParameters": None,
        "stageVariables": None,
        "requestContext": {
            "authorizer": {"claims": claims or {}},
            "resourcePath": path,
            "httpMethod": http_method,
            "path": path,
            "stage": "test",
        },
        "body": json.dumps(body) if body is not None else None,
        "isBase64Encoded": False,
    }


def _create_downloads_table(dynamodb):
    dynamodb.create_table(
        TableName=os.environ["DOWNLOADS_TABLE_NAME"],
        KeySchema=[{"AttributeName": "downloadId", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "downloadId", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )


def _create_photos_table(dynamodb):
    dynamodb.create_table(
        TableName=os.environ["PHOTOS_TABLE_NAME"],
        KeySchema=[{"AttributeName": "photoID", "KeyType": "HASH"}],
        AttributeDefinitions=[
            {"AttributeName": "photoID", "AttributeType": "S"},
            {"AttributeName": "eventID", "AttributeType": "S"},
            {"AttributeName": "uploadedAtFilename", "AttributeType": "S"},
        ],
        GlobalSecondaryIndexes=[
            {
                "IndexName": "eventID-uploadedAtFilename-index",
                "KeySchema": [
                    {"AttributeName": "eventID", "KeyType": "HASH"},
                    {"AttributeName": "uploadedAtFilename", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
            }
        ],
        BillingMode="PAY_PER_REQUEST",
    )


def _create_attendees_table(dynamodb):
    dynamodb.create_table(
        TableName=os.environ["EVENT_ATTENDEES_TABLE_NAME"],
        KeySchema=[{"AttributeName": "userID", "KeyType": "HASH"}, {"AttributeName": "eventID", "KeyType": "RANGE"}],
        AttributeDefinitions=[{"AttributeName": "userID", "AttributeType": "S"}, {"AttributeName": "eventID", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )


@mock_aws
def test_kickoff_then_build_then_status_full_round_trip(monkeypatch):
    dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
    _create_downloads_table(dynamodb)
    _create_photos_table(dynamodb)
    _create_attendees_table(dynamodb)
    downloads_table = dynamodb.Table(os.environ["DOWNLOADS_TABLE_NAME"])
    photos_table = dynamodb.Table(os.environ["PHOTOS_TABLE_NAME"])

    s3 = boto3.client("s3", region_name="ap-south-1")
    bucket = os.environ["PHOTOS_BUCKET"]
    s3.create_bucket(Bucket=bucket, CreateBucketConfiguration={"LocationConstraint": "ap-south-1"})

    photo_bodies = {
        "photos/event/evt_1/p1.jpg": b"photo-1-bytes",
        "photos/event/evt_1/p2.jpg": b"photo-2-bytes",
    }
    for i, (key, body) in enumerate(photo_bodies.items()):
        s3.put_object(Bucket=bucket, Key=key, Body=body)
        photos_table.put_item(
            Item={
                "photoID": f"p{i + 1}",
                "eventID": "evt_1",
                "s3Key": key,
                "uploadedAtFilename": f"2026-08-15T10:0{i}:00Z#p{i + 1}.jpg",
            }
        )

    captured_build_payload = {}
    monkeypatch.setattr(
        manager,
        "invoke_self_async",
        lambda function_name, payload: captured_build_payload.update(payload),
    )

    kickoff_response = lambda_handler(
        _api_event("POST", "/events/evt_1/photos/download", claims={"sub": "user_1"}),
        _FakeLambdaContext(),
    )
    assert kickoff_response["statusCode"] == 200
    download_id = json.loads(kickoff_response["body"])["downloadId"]
    assert captured_build_payload == {
        "action": "build",
        "downloadId": download_id,
        "eventID": "evt_1",
        "requesterID": "user_1",
        "scope": "all",
        "photoIds": None,
    }

    pending_row = downloads_table.get_item(Key={"downloadId": download_id})["Item"]
    assert pending_row["status"] == "PENDING"

    build_result = lambda_handler(captured_build_payload, _FakeLambdaContext())
    assert build_result == {"downloadId": download_id, "status": "READY"}

    ready_row = downloads_table.get_item(Key={"downloadId": download_id})["Item"]
    assert ready_row["status"] == "READY"
    zip_key = ready_row["s3Key"]
    assert zip_key == f"downloads/event/evt_1/{download_id}/everyone-photos-evt_1.zip"

    zip_bytes = s3.get_object(Bucket=bucket, Key=zip_key)["Body"].read()
    assert s3.get_object(Bucket=bucket, Key=zip_key)["ContentDisposition"] == 'attachment; filename="everyone-photos-evt_1.zip"'
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
        assert sorted(archive.namelist()) == ["p1.jpg", "p2.jpg"]
        assert archive.read("p1.jpg") == b"photo-1-bytes"
        assert archive.read("p2.jpg") == b"photo-2-bytes"

    status_response = lambda_handler(
        _api_event("GET", f"/events/evt_1/downloads/{download_id}/status"), _FakeLambdaContext()
    )
    assert status_response["statusCode"] == 200
    status_result = json.loads(status_response["body"])
    assert status_result["status"] == "READY"
    assert zip_key in status_result["downloadUrl"]
    assert parse_qs(urlparse(status_result["downloadUrl"]).query)["response-content-disposition"] == [
        'attachment; filename="everyone-photos-evt_1.zip"'
    ]


@mock_aws
def test_photos_of_me_download_contains_only_matched_photos(monkeypatch):
    dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
    _create_downloads_table(dynamodb)
    _create_photos_table(dynamodb)
    _create_attendees_table(dynamodb)
    photos_table = dynamodb.Table(os.environ["PHOTOS_TABLE_NAME"])
    attendees_table = dynamodb.Table(os.environ["EVENT_ATTENDEES_TABLE_NAME"])
    attendees_table.put_item(Item={"userID": "user_1", "eventID": "evt_1", "status": "ATTENDEE", "matchedPhotoIDs": {"p1"}})

    s3 = boto3.client("s3", region_name="ap-south-1")
    bucket = os.environ["PHOTOS_BUCKET"]
    s3.create_bucket(Bucket=bucket, CreateBucketConfiguration={"LocationConstraint": "ap-south-1"})
    for photo_id in ("p1", "p2"):
        key = f"photos/event/evt_1/{photo_id}.jpg"
        s3.put_object(Bucket=bucket, Key=key, Body=photo_id.encode())
        photos_table.put_item(Item={"photoID": photo_id, "eventID": "evt_1", "s3Key": key, "uploadedAtFilename": f"2026-08-15T10:00:00Z#{photo_id}.jpg"})

    build_payload = {}
    monkeypatch.setattr(manager, "invoke_self_async", lambda function_name, payload: build_payload.update(payload))
    kickoff = lambda_handler(
        _api_event("POST", "/events/evt_1/photos/download", body={"scope": "mine"}, claims={"sub": "user_1"}),
        _FakeLambdaContext(),
    )
    assert kickoff["statusCode"] == 200
    download_id = json.loads(kickoff["body"])["downloadId"]
    assert build_payload["scope"] == "mine"
    lambda_handler(build_payload, _FakeLambdaContext())

    row = dynamodb.Table(os.environ["DOWNLOADS_TABLE_NAME"]).get_item(Key={"downloadId": download_id})["Item"]
    assert row["filename"] == "photos-of-me-evt_1.zip"
    zip_response = s3.get_object(Bucket=bucket, Key=row["s3Key"])
    assert zip_response["ContentDisposition"] == 'attachment; filename="photos-of-me-evt_1.zip"'
    with zipfile.ZipFile(io.BytesIO(zip_response["Body"].read())) as archive:
        assert archive.namelist() == ["p1.jpg"]


@mock_aws
def test_photo_lookup_batches_large_matched_set_and_rejects_other_event():
    dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
    _create_photos_table(dynamodb)
    _create_attendees_table(dynamodb)
    photos_table = dynamodb.Table(os.environ["PHOTOS_TABLE_NAME"])
    matched_ids = {f"p{i:03d}" for i in range(120)} | {"foreign"}
    dynamodb.Table(os.environ["EVENT_ATTENDEES_TABLE_NAME"]).put_item(
        Item={"userID": "user_1", "eventID": "evt_1", "matchedPhotoIDs": matched_ids}
    )
    for photo_id in matched_ids:
        event_id = "evt_2" if photo_id == "foreign" else "evt_1"
        photos_table.put_item(
            Item={"photoID": photo_id, "eventID": event_id, "s3Key": f"photos/event/{event_id}/{photo_id}.jpg", "uploadedAtFilename": photo_id}
        )

    keys = list_photo_keys("evt_1", None, "mine", "user_1")
    assert len(keys) == 120
    assert "photos/event/evt_2/foreign.jpg" not in keys
