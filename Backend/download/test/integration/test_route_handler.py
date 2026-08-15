import io
import os
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import boto3  # noqa: E402
from moto import mock_aws  # noqa: E402

import Manager.manager as manager  # noqa: E402
from routeHandler import lambda_handler  # noqa: E402


class _FakeLambdaContext:
    function_name = "download"
    memory_limit_in_mb = 128
    invoked_function_arn = "arn:aws:lambda:ap-south-1:000000000000:function:download"
    aws_request_id = "test-request-id"


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


@mock_aws
def test_kickoff_then_build_then_status_full_round_trip(monkeypatch):
    dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
    _create_downloads_table(dynamodb)
    _create_photos_table(dynamodb)
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

    # The real self-invoke (a fire-and-forget Lambda call) isn't exercised here — instead,
    # the "build" payload it would send is captured, then fed straight back into
    # lambda_handler, exactly as the real async invocation would run it.
    captured_build_payload = {}
    monkeypatch.setattr(
        manager,
        "invoke_self_async",
        lambda function_name, payload: captured_build_payload.update(payload),
    )

    kickoff_result = lambda_handler(
        {"action": "kickoff", "eventID": "evt_1", "requesterID": "user_1"}, _FakeLambdaContext()
    )
    download_id = kickoff_result["downloadId"]
    assert captured_build_payload == {
        "action": "build",
        "downloadId": download_id,
        "eventID": "evt_1",
        "photoIds": None,
    }

    pending_row = downloads_table.get_item(Key={"downloadId": download_id})["Item"]
    assert pending_row["status"] == "PENDING"

    build_result = lambda_handler(captured_build_payload, _FakeLambdaContext())
    assert build_result == {"downloadId": download_id, "status": "READY"}

    ready_row = downloads_table.get_item(Key={"downloadId": download_id})["Item"]
    assert ready_row["status"] == "READY"
    zip_key = ready_row["s3Key"]
    assert zip_key == f"downloads/event/evt_1/{download_id}.zip"

    zip_bytes = s3.get_object(Bucket=bucket, Key=zip_key)["Body"].read()
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
        assert sorted(archive.namelist()) == ["p1.jpg", "p2.jpg"]
        assert archive.read("p1.jpg") == b"photo-1-bytes"
        assert archive.read("p2.jpg") == b"photo-2-bytes"

    status_result = lambda_handler(
        {"action": "status", "downloadId": download_id}, _FakeLambdaContext()
    )
    assert status_result["status"] == "READY"
    assert zip_key in status_result["downloadUrl"]
