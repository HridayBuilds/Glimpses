import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import boto3
from moto import mock_aws

import Manager.manager as manager
from routeHandler import lambda_handler


class _FakeLambdaContext:
    function_name = "events"
    memory_limit_in_mb = 256
    invoked_function_arn = "arn:aws:lambda:ap-south-1:000000000000:function:events"
    aws_request_id = "test-request-id"


def _api_event(http_method, path, body=None, claims=None, path_parameters=None):
    return {
        "resource": path,
        "path": path,
        "httpMethod": http_method,
        "headers": {"Content-Type": "application/json"},
        "multiValueHeaders": {},
        "queryStringParameters": None,
        "multiValueQueryStringParameters": None,
        "pathParameters": path_parameters,
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


def _create_events_table(dynamodb):
    dynamodb.create_table(
        TableName=os.environ["EVENTS_TABLE_NAME"],
        KeySchema=[{"AttributeName": "eventID", "KeyType": "HASH"}],
        AttributeDefinitions=[
            {"AttributeName": "eventID", "AttributeType": "S"},
            {"AttributeName": "organizerID", "AttributeType": "S"},
            {"AttributeName": "status", "AttributeType": "S"},
            {"AttributeName": "accessCode", "AttributeType": "S"},
            {"AttributeName": "lastUploadAt", "AttributeType": "S"},
        ],
        GlobalSecondaryIndexes=[
            {
                "IndexName": "organizerID-status-index",
                "KeySchema": [
                    {"AttributeName": "organizerID", "KeyType": "HASH"},
                    {"AttributeName": "status", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
            },
            {
                "IndexName": "accessCode-index",
                "KeySchema": [{"AttributeName": "accessCode", "KeyType": "HASH"}],
                "Projection": {"ProjectionType": "ALL"},
            },
            {
                "IndexName": "status-lastUploadAt-index",
                "KeySchema": [
                    {"AttributeName": "status", "KeyType": "HASH"},
                    {"AttributeName": "lastUploadAt", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
            },
        ],
        BillingMode="PAY_PER_REQUEST",
    )


@mock_aws
def test_create_list_get_update_and_archive_round_trip(monkeypatch):
    dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
    _create_events_table(dynamodb)
    _create_event_attendees_table(dynamodb)

    s3 = boto3.client("s3", region_name="ap-south-1")
    s3.create_bucket(
        Bucket=os.environ["PHOTOS_BUCKET"], CreateBucketConfiguration={"LocationConstraint": "ap-south-1"}
    )

    monkeypatch.setattr(manager, "create_collection", lambda collection_id: None)
    monkeypatch.setattr(manager, "delete_collection", lambda collection_id: None)

    create_response = lambda_handler(
        _api_event("POST", "/events", body={"name": "Priya's Trip"}, claims={"sub": "user_1"}),
        _FakeLambdaContext(),
    )
    assert create_response["statusCode"] == 200
    created = json.loads(create_response["body"])
    event_id = created["eventID"]
    assert created["status"] == "ACTIVE"

    qrcode_object = s3.get_object(Bucket=os.environ["PHOTOS_BUCKET"], Key=f"qrcodes/event/{event_id}/qrcode.png")
    assert qrcode_object["ContentDisposition"] == 'attachment; filename="qrcode.png"'

    list_response = lambda_handler(_api_event("GET", "/events", claims={"sub": "user_1"}), _FakeLambdaContext())
    assert [item["eventID"] for item in json.loads(list_response["body"])] == [event_id]

    get_response = lambda_handler(
        _api_event("GET", f"/events/{event_id}", claims={"sub": "user_1"}, path_parameters={"event_id": event_id}),
        _FakeLambdaContext(),
    )
    assert json.loads(get_response["body"])["name"] == "Priya's Trip"

    update_response = lambda_handler(
        _api_event(
            "PUT",
            f"/events/{event_id}",
            body={"name": "Priya's Goa Trip"},
            claims={"sub": "user_1"},
            path_parameters={"event_id": event_id},
        ),
        _FakeLambdaContext(),
    )
    assert update_response["statusCode"] == 200

    events_table = dynamodb.Table(os.environ["EVENTS_TABLE_NAME"])
    assert events_table.get_item(Key={"eventID": event_id})["Item"]["name"] == "Priya's Goa Trip"

    stats_response = lambda_handler(
        _api_event("GET", f"/events/{event_id}/stats", claims={"sub": "user_1"}, path_parameters={"event_id": event_id}),
        _FakeLambdaContext(),
    )
    assert json.loads(stats_response["body"]) == {"photoCount": 0, "storageBytes": 0, "attendeeCount": 0}

    archive_response = lambda_handler(
        _api_event(
            "POST", f"/events/{event_id}/archive", claims={"sub": "user_1"}, path_parameters={"event_id": event_id}
        ),
        _FakeLambdaContext(),
    )
    assert archive_response["statusCode"] == 200
    assert events_table.get_item(Key={"eventID": event_id})["Item"]["status"] == "ARCHIVED"


def _create_event_attendees_table(dynamodb):
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
def test_create_event_enrolls_organizer_as_attendee_but_excludes_them_from_stats(monkeypatch):
    dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
    _create_events_table(dynamodb)
    _create_event_attendees_table(dynamodb)

    s3 = boto3.client("s3", region_name="ap-south-1")
    s3.create_bucket(
        Bucket=os.environ["PHOTOS_BUCKET"], CreateBucketConfiguration={"LocationConstraint": "ap-south-1"}
    )
    monkeypatch.setattr(manager, "create_collection", lambda collection_id: None)

    create_response = lambda_handler(
        _api_event("POST", "/events", body={"name": "Priya's Trip"}, claims={"sub": "organizer_1"}),
        _FakeLambdaContext(),
    )
    event_id = json.loads(create_response["body"])["eventID"]

    attendees_table = dynamodb.Table(os.environ["EVENT_ATTENDEES_TABLE_NAME"])
    organizer_row = attendees_table.get_item(Key={"userID": "organizer_1", "eventID": event_id})["Item"]
    assert organizer_row["status"] == "ATTENDEE"

    stats_response = lambda_handler(
        _api_event(
            "GET", f"/events/{event_id}/stats", claims={"sub": "organizer_1"}, path_parameters={"event_id": event_id}
        ),
        _FakeLambdaContext(),
    )
    assert json.loads(stats_response["body"])["attendeeCount"] == 0

    attendees_table.put_item(Item={"userID": "guest_1", "eventID": event_id, "status": "ATTENDEE"})

    stats_response = lambda_handler(
        _api_event(
            "GET", f"/events/{event_id}/stats", claims={"sub": "organizer_1"}, path_parameters={"event_id": event_id}
        ),
        _FakeLambdaContext(),
    )
    assert json.loads(stats_response["body"])["attendeeCount"] == 1


@mock_aws
def test_list_my_events_returns_only_pending_and_attendee_rows():
    dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
    _create_events_table(dynamodb)
    _create_event_attendees_table(dynamodb)

    def _full_event(event_id, name):
        return {
            "eventID": event_id,
            "organizerID": "organizer_1",
            "name": name,
            "description": "",
            "status": "ACTIVE",
            "joinPolicy": "OPEN",
            "contributionPolicy": "ATTENDEES_CAN_ADD",
            "accessCode": f"CODE{event_id}",
            "createdAt": "2026-08-01T00:00:00+00:00",
        }

    events_table = dynamodb.Table(os.environ["EVENTS_TABLE_NAME"])
    events_table.put_item(Item=_full_event("evt_1", "Priya's Trip"))
    events_table.put_item(Item=_full_event("evt_2", "Rohan's Party"))
    events_table.put_item(Item=_full_event("evt_3", "Old Trip"))

    attendees_table = dynamodb.Table(os.environ["EVENT_ATTENDEES_TABLE_NAME"])
    attendees_table.put_item(Item={"userID": "user_2", "eventID": "evt_1", "status": "ATTENDEE"})
    attendees_table.put_item(Item={"userID": "user_2", "eventID": "evt_2", "status": "PENDING"})
    attendees_table.put_item(Item={"userID": "user_2", "eventID": "evt_3", "status": "LEFT"})

    response = lambda_handler(
        _api_event("GET", "/events/my-events", claims={"sub": "user_2"}), _FakeLambdaContext()
    )

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert {(item["eventID"], item["attendeeStatus"]) for item in body} == {
        ("evt_1", "ATTENDEE"),
        ("evt_2", "PENDING"),
    }


@mock_aws
def test_get_event_detail_rejects_non_organizer():
    dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
    _create_events_table(dynamodb)
    dynamodb.Table(os.environ["EVENTS_TABLE_NAME"]).put_item(
        Item={
            "eventID": "evt_1",
            "organizerID": "user_1",
            "name": "Priya's Trip",
            "status": "ACTIVE",
            "joinPolicy": "OPEN",
            "contributionPolicy": "ATTENDEES_CAN_ADD",
            "accessCode": "AB23CD",
            "createdAt": "2026-08-01T00:00:00+00:00",
        }
    )

    try:
        lambda_handler(
            _api_event("GET", "/events/evt_1", claims={"sub": "someone_else"}, path_parameters={"event_id": "evt_1"}),
            _FakeLambdaContext(),
        )
        assert False, "expected ValueError"
    except ValueError:
        pass


@mock_aws
def test_internal_run_archive_sweep_action_archives_stale_events(monkeypatch):
    dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
    _create_events_table(dynamodb)
    events_table = dynamodb.Table(os.environ["EVENTS_TABLE_NAME"])

    monkeypatch.setattr(manager, "delete_collection", lambda collection_id: None)

    stale_last_upload = (datetime.now(timezone.utc) - timedelta(days=31)).isoformat()
    fresh_last_upload = datetime.now(timezone.utc).isoformat()
    events_table.put_item(
        Item={
            "eventID": "evt_stale",
            "organizerID": "user_1",
            "name": "Old Trip",
            "status": "ACTIVE",
            "joinPolicy": "OPEN",
            "contributionPolicy": "ATTENDEES_CAN_ADD",
            "accessCode": "AB23CD",
            "rekognitionCollectionID": "glimpses-event-evt_stale",
            "createdAt": stale_last_upload,
            "lastUploadAt": stale_last_upload,
        }
    )
    events_table.put_item(
        Item={
            "eventID": "evt_fresh",
            "organizerID": "user_1",
            "name": "New Trip",
            "status": "ACTIVE",
            "joinPolicy": "OPEN",
            "contributionPolicy": "ATTENDEES_CAN_ADD",
            "accessCode": "CD45EF",
            "rekognitionCollectionID": "glimpses-event-evt_fresh",
            "createdAt": fresh_last_upload,
            "lastUploadAt": fresh_last_upload,
        }
    )

    result = lambda_handler({"action": "run_archive_sweep"}, _FakeLambdaContext())

    assert result == {"archivedEventIDs": ["evt_stale"]}
    assert events_table.get_item(Key={"eventID": "evt_stale"})["Item"]["status"] == "ARCHIVED"
    assert events_table.get_item(Key={"eventID": "evt_fresh"})["Item"]["status"] == "ACTIVE"
