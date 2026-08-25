import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import boto3
from moto import mock_aws

import Manager.delete_event as delete_event
import Manager.delete_photos as delete_photos
from routeHandler import lambda_handler


class _FakeLambdaContext:
    function_name = "cascade-delete"
    memory_limit_in_mb = 256
    invoked_function_arn = "arn:aws:lambda:ap-south-1:000000000000:function:cascade-delete"
    aws_request_id = "test-request-id"


def _create_tables(dynamodb):
    dynamodb.create_table(
        TableName=os.environ["EVENTS_TABLE_NAME"],
        KeySchema=[{"AttributeName": "eventID", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "eventID", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )
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
    dynamodb.create_table(
        TableName=os.environ["FACES_TABLE_NAME"],
        KeySchema=[{"AttributeName": "rekognitionFaceID", "KeyType": "HASH"}],
        AttributeDefinitions=[
            {"AttributeName": "rekognitionFaceID", "AttributeType": "S"},
            {"AttributeName": "eventID", "AttributeType": "S"},
            {"AttributeName": "photoID", "AttributeType": "S"},
        ],
        GlobalSecondaryIndexes=[
            {
                "IndexName": "eventID-photoID-index",
                "KeySchema": [
                    {"AttributeName": "eventID", "KeyType": "HASH"},
                    {"AttributeName": "photoID", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
            }
        ],
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
            {"AttributeName": "status", "AttributeType": "S"},
        ],
        GlobalSecondaryIndexes=[
            {
                "IndexName": "eventID-status-index",
                "KeySchema": [
                    {"AttributeName": "eventID", "KeyType": "HASH"},
                    {"AttributeName": "status", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
            }
        ],
        BillingMode="PAY_PER_REQUEST",
    )


@mock_aws
def test_delete_event_cascades_photos_faces_attendees_and_row(monkeypatch):
    dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
    _create_tables(dynamodb)
    events_table = dynamodb.Table(os.environ["EVENTS_TABLE_NAME"])
    photos_table = dynamodb.Table(os.environ["PHOTOS_TABLE_NAME"])
    faces_table = dynamodb.Table(os.environ["FACES_TABLE_NAME"])
    event_attendees_table = dynamodb.Table(os.environ["EVENT_ATTENDEES_TABLE_NAME"])

    s3 = boto3.client("s3", region_name="ap-south-1")
    bucket = os.environ["PHOTOS_BUCKET"]
    s3.create_bucket(Bucket=bucket, CreateBucketConfiguration={"LocationConstraint": "ap-south-1"})
    s3.put_object(Bucket=bucket, Key="photos/event/evt_1/p1.jpg", Body=b"x")
    s3.put_object(Bucket=bucket, Key="thumbnails/event/evt_1/p1.jpg", Body=b"x")

    events_table.put_item(Item={"eventID": "evt_1", "rekognitionCollectionID": "glimpses-event-evt_1"})
    photos_table.put_item(
        Item={
            "photoID": "p1",
            "eventID": "evt_1",
            "uploadedAtFilename": "2026-08-15T10:00:00Z#a.jpg",
            "s3Key": "photos/event/evt_1/p1.jpg",
            "thumbnailKey": "thumbnails/event/evt_1/p1.jpg",
        }
    )
    faces_table.put_item(Item={"rekognitionFaceID": "face-1", "eventID": "evt_1", "photoID": "p1"})
    event_attendees_table.put_item(Item={"userID": "user_1", "eventID": "evt_1", "status": "ATTENDEE"})

    collection_deletes = []
    monkeypatch.setattr(delete_event, "delete_collection", lambda collection_id: collection_deletes.append(collection_id))

    result = lambda_handler({"action": "delete_event", "eventID": "evt_1"}, _FakeLambdaContext())

    assert result == {"eventID": "evt_1", "deleted": True}
    assert collection_deletes == ["glimpses-event-evt_1"]
    assert "Item" not in events_table.get_item(Key={"eventID": "evt_1"})
    assert "Item" not in photos_table.get_item(Key={"photoID": "p1"})
    assert "Item" not in faces_table.get_item(Key={"rekognitionFaceID": "face-1"})
    assert "Item" not in event_attendees_table.get_item(Key={"userID": "user_1", "eventID": "evt_1"})
    with_keys = s3.list_objects_v2(Bucket=bucket).get("Contents", [])
    assert with_keys == []


@mock_aws
def test_delete_event_is_a_no_op_when_already_gone():
    dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
    _create_tables(dynamodb)

    result = lambda_handler({"action": "delete_event", "eventID": "evt_missing"}, _FakeLambdaContext())

    assert result == {"eventID": "evt_missing", "deleted": False}


@mock_aws
def test_delete_photos_cascades_faces_row_s3_and_decrements_counters(monkeypatch):
    dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
    _create_tables(dynamodb)
    events_table = dynamodb.Table(os.environ["EVENTS_TABLE_NAME"])
    photos_table = dynamodb.Table(os.environ["PHOTOS_TABLE_NAME"])
    faces_table = dynamodb.Table(os.environ["FACES_TABLE_NAME"])

    s3 = boto3.client("s3", region_name="ap-south-1")
    bucket = os.environ["PHOTOS_BUCKET"]
    s3.create_bucket(Bucket=bucket, CreateBucketConfiguration={"LocationConstraint": "ap-south-1"})
    s3.put_object(Bucket=bucket, Key="photos/event/evt_1/p1.jpg", Body=b"x")
    s3.put_object(Bucket=bucket, Key="thumbnails/event/evt_1/p1.jpg", Body=b"x")

    events_table.put_item(Item={"eventID": "evt_1", "rekognitionCollectionID": "glimpses-event-evt_1", "photoCount": 1, "storageBytes": 1234})
    photos_table.put_item(
        Item={
            "photoID": "p1",
            "eventID": "evt_1",
            "uploadedAtFilename": "2026-08-15T10:00:00Z#a.jpg",
            "sizeBytes": 1234,
            "s3Key": "photos/event/evt_1/p1.jpg",
            "thumbnailKey": "thumbnails/event/evt_1/p1.jpg",
        }
    )
    faces_table.put_item(Item={"rekognitionFaceID": "face-1", "eventID": "evt_1", "photoID": "p1"})

    face_deletes = []
    monkeypatch.setattr(
        delete_photos, "delete_faces_from_collection", lambda collection_id, face_ids: face_deletes.append((collection_id, face_ids))
    )

    result = lambda_handler({"action": "delete_photos", "eventID": "evt_1", "photoIDs": ["p1"]}, _FakeLambdaContext())

    assert result == {"eventID": "evt_1", "deletedPhotoIDs": ["p1"]}
    assert face_deletes == [("glimpses-event-evt_1", ["face-1"])]
    assert "Item" not in photos_table.get_item(Key={"photoID": "p1"})
    assert "Item" not in faces_table.get_item(Key={"rekognitionFaceID": "face-1"})
    updated_event = events_table.get_item(Key={"eventID": "evt_1"})["Item"]
    assert updated_event["photoCount"] == 0
    assert updated_event["storageBytes"] == 0
    with_keys = s3.list_objects_v2(Bucket=bucket).get("Contents", [])
    assert with_keys == []


@mock_aws
def test_events_ttl_stream_record_cascades_the_deleted_event(monkeypatch):
    dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
    _create_tables(dynamodb)
    events_table = dynamodb.Table(os.environ["EVENTS_TABLE_NAME"])

    s3 = boto3.client("s3", region_name="ap-south-1")
    bucket = os.environ["PHOTOS_BUCKET"]
    s3.create_bucket(Bucket=bucket, CreateBucketConfiguration={"LocationConstraint": "ap-south-1"})

    events_table.put_item(Item={"eventID": "evt_1", "rekognitionCollectionID": "glimpses-event-evt_1"})
    monkeypatch.setattr(delete_event, "delete_collection", lambda collection_id: None)

    event = {"Records": [{"dynamodb": {"OldImage": {"eventID": {"S": "evt_1"}}}}]}
    result = lambda_handler(event, _FakeLambdaContext())

    assert result == [{"eventID": "evt_1", "deleted": True}]
    assert "Item" not in events_table.get_item(Key={"eventID": "evt_1"})
