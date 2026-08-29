import io
import json
import os
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import boto3
from moto import mock_aws
from PIL import Image

import Manager.index_one_photo as index_one_photo
import Manager.match_attendees as match_attendees
from routeHandler import lambda_handler


class _FakeLambdaContext:
    function_name = "ingestion"
    memory_limit_in_mb = 512
    invoked_function_arn = "arn:aws:lambda:ap-south-1:000000000000:function:ingestion"
    aws_request_id = "test-request-id"


def _make_jpeg_bytes():
    buffer = io.BytesIO()
    Image.new("RGB", (100, 100), color="red").save(buffer, format="JPEG")
    return buffer.getvalue()


_JPEG_BYTES = _make_jpeg_bytes()


def _create_tables(dynamodb):
    dynamodb.create_table(
        TableName=os.environ["PHOTOS_TABLE_NAME"],
        KeySchema=[{"AttributeName": "photoID", "KeyType": "HASH"}],
        AttributeDefinitions=[
            {"AttributeName": "photoID", "AttributeType": "S"},
            {"AttributeName": "eventID", "AttributeType": "S"},
            {"AttributeName": "contentHash", "AttributeType": "S"},
        ],
        GlobalSecondaryIndexes=[
            {
                "IndexName": "eventID-contentHash-index",
                "KeySchema": [
                    {"AttributeName": "eventID", "KeyType": "HASH"},
                    {"AttributeName": "contentHash", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
            }
        ],
        BillingMode="PAY_PER_REQUEST",
    )
    dynamodb.create_table(
        TableName=os.environ["EVENTS_TABLE_NAME"],
        KeySchema=[{"AttributeName": "eventID", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "eventID", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )
    dynamodb.create_table(
        TableName=os.environ["FACES_TABLE_NAME"],
        KeySchema=[{"AttributeName": "rekognitionFaceID", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "rekognitionFaceID", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )
    dynamodb.create_table(
        TableName=os.environ["EVENT_ATTENDEES_TABLE_NAME"],
        KeySchema=[
            {"AttributeName": "userID", "KeyType": "HASH"},
            {"AttributeName": "eventID", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "userID", "AttributeType": "S"},
            {"AttributeName": "eventID", "AttributeType": "S"},
        ],
        BillingMode="PAY_PER_REQUEST",
    )
    dynamodb.create_table(
        TableName=os.environ["USERS_TABLE_NAME"],
        KeySchema=[{"AttributeName": "userID", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "userID", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )


def _zip_bytes(entries):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for filename, data in entries.items():
            archive.writestr(filename, data)
    return buffer.getvalue()


@mock_aws
def test_stage_then_process_then_index_then_finalize_full_round_trip(monkeypatch):
    dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
    _create_tables(dynamodb)
    events_table = dynamodb.Table(os.environ["EVENTS_TABLE_NAME"])
    users_table = dynamodb.Table(os.environ["USERS_TABLE_NAME"])
    faces_table = dynamodb.Table(os.environ["FACES_TABLE_NAME"])

    s3 = boto3.client("s3", region_name="ap-south-1")
    bucket = os.environ["PHOTOS_BUCKET"]
    s3.create_bucket(Bucket=bucket, CreateBucketConfiguration={"LocationConstraint": "ap-south-1"})

    events_table.put_item(Item={"eventID": "evt_1", "rekognitionCollectionID": "evt_1-collection"})
    users_table.put_item(Item={"userID": "user_1", "displayName": "Meera", "email": "meera@example.com"})

    upload_key = "uploads/event/evt_1/user/user_1/job/job_1/original.zip"
    s3.put_object(Bucket=bucket, Key=upload_key, Body=_zip_bytes({"a.jpg": _JPEG_BYTES}))

    stage_result = lambda_handler({"step": "stage", "bucket": bucket, "key": upload_key}, _FakeLambdaContext())
    staged_manifest = json.loads(s3.get_object(Bucket=bucket, Key=stage_result["stagedManifestKey"])["Body"].read())
    assert len(staged_manifest) == 1
    staged_entry = staged_manifest[0]

    process_result = lambda_handler(
        {"step": "process_one_photo", **staged_entry},
        _FakeLambdaContext(),
    )
    assert process_result["status"] == "SUCCEEDED"

    process_results_manifest_key = "results/process-photos/manifest.json"
    process_results_file_key = "results/process-photos/succeeded-0.json"
    s3.put_object(
        Bucket=bucket,
        Key=process_results_file_key,
        Body=json.dumps([{"Output": json.dumps(process_result)}]).encode("utf-8"),
    )
    s3.put_object(
        Bucket=bucket,
        Key=process_results_manifest_key,
        Body=json.dumps({"ResultFiles": {"SUCCEEDED": [{"Key": process_results_file_key}], "FAILED": []}}).encode("utf-8"),
    )

    manifest_result = lambda_handler(
        {
            "step": "build_photos_manifest",
            "jobId": stage_result["jobId"],
            "eventID": stage_result["eventID"],
            "processResultsBucket": bucket,
            "processResultsManifestKey": process_results_manifest_key,
        },
        _FakeLambdaContext(),
    )
    assert manifest_result["processFailedCount"] == 0
    manifest = json.loads(s3.get_object(Bucket=bucket, Key=manifest_result["manifestKey"])["Body"].read())
    assert len(manifest) == 1
    photo = manifest[0]

    photo_key = photo["s3Key"]
    assert s3.get_object(Bucket=bucket, Key=photo_key)["Body"].read() == _JPEG_BYTES
    thumbnail_key = f"thumbnails/event/evt_1/{photo['photoID']}.jpg"
    assert s3.get_object(Bucket=bucket, Key=thumbnail_key)

    updated_event = events_table.get_item(Key={"eventID": "evt_1"})["Item"]
    assert updated_event["photoCount"] == 1
    assert "lastUploadAt" in updated_event

    monkeypatch.setattr(
        index_one_photo,
        "index_faces",
        lambda collection_id, bucket, key: [{"Face": {"FaceId": "face-1"}}],
    )

    index_result = lambda_handler(
        {"step": "index_one_photo", "eventID": "evt_1", "photoID": photo["photoID"], "s3Key": photo_key},
        _FakeLambdaContext(),
    )
    assert index_result == {"photoID": photo["photoID"], "status": "SUCCEEDED", "faceCount": 1}
    assert faces_table.get_item(Key={"rekognitionFaceID": "face-1"})["Item"]["photoID"] == photo["photoID"]

    index_results_manifest_key = "results/index-photos/manifest.json"
    index_results_file_key = "results/index-photos/succeeded-0.json"
    s3.put_object(
        Bucket=bucket,
        Key=index_results_file_key,
        Body=json.dumps([{"Output": json.dumps(index_result)}]).encode("utf-8"),
    )
    s3.put_object(
        Bucket=bucket,
        Key=index_results_manifest_key,
        Body=json.dumps({"ResultFiles": {"SUCCEEDED": [{"Key": index_results_file_key}], "FAILED": []}}).encode("utf-8"),
    )

    finalize_result = lambda_handler(
        {
            "step": "finalize",
            "jobId": "job_1",
            "eventID": "evt_1",
            "processFailedCount": manifest_result["processFailedCount"],
            "indexResultsBucket": bucket,
            "indexResultsManifestKey": index_results_manifest_key,
        },
        _FakeLambdaContext(),
    )
    assert finalize_result == {
        "jobId": "job_1",
        "eventID": "evt_1",
        "succeededCount": 1,
        "failedCount": 0,
    }


@mock_aws
def test_event_attendees_stream_record_triggers_match_attendees(monkeypatch):
    dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
    _create_tables(dynamodb)
    events_table = dynamodb.Table(os.environ["EVENTS_TABLE_NAME"])
    event_attendees_table = dynamodb.Table(os.environ["EVENT_ATTENDEES_TABLE_NAME"])
    faces_table = dynamodb.Table(os.environ["FACES_TABLE_NAME"])

    s3 = boto3.client("s3", region_name="ap-south-1")
    bucket = os.environ["PHOTOS_BUCKET"]
    s3.create_bucket(Bucket=bucket, CreateBucketConfiguration={"LocationConstraint": "ap-south-1"})
    s3.put_object(Bucket=bucket, Key="selfies/user/user_1/selfie.jpg", Body=_JPEG_BYTES)

    events_table.put_item(Item={"eventID": "evt_1", "rekognitionCollectionID": "evt_1-collection"})
    event_attendees_table.put_item(Item={"userID": "user_1", "eventID": "evt_1", "status": "ATTENDEE"})
    faces_table.put_item(Item={"rekognitionFaceID": "face-1", "eventID": "evt_1", "photoID": "photo_1"})

    monkeypatch.setattr(
        match_attendees,
        "search_faces_by_image",
        lambda collection_id, bucket, key, threshold: [{"Face": {"FaceId": "face-1"}}],
    )

    event = {
        "Records": [
            {"dynamodb": {"Keys": {"userID": {"S": "user_1"}, "eventID": {"S": "evt_1"}}}},
        ]
    }
    result = lambda_handler(event, _FakeLambdaContext())
    assert result == [{"eventID": "evt_1", "userID": "user_1", "matchedCount": 1}]

    attendee_row = event_attendees_table.get_item(Key={"userID": "user_1", "eventID": "evt_1"})["Item"]
    assert attendee_row["matchedPhotoIDs"] == {"photo_1"}
