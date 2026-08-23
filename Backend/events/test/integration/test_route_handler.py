import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import boto3  # noqa: E402
from moto import mock_aws  # noqa: E402

import Manager.manager as manager  # noqa: E402
from routeHandler import lambda_handler  # noqa: E402


class _FakeLambdaContext:
    function_name = "events"
    memory_limit_in_mb = 256
    invoked_function_arn = "arn:aws:lambda:ap-south-1:000000000000:function:events"
    aws_request_id = "test-request-id"


# Mirrors the real AWS_PROXY envelope API Gateway sends — a Lambda proxy integration
# does no request/response transformation itself, so the handler must be exercised
# against this exact shape, not a hand-shortened dict.
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

    s3 = boto3.client("s3", region_name="ap-south-1")
    s3.create_bucket(
        Bucket=os.environ["PHOTOS_BUCKET"], CreateBucketConfiguration={"LocationConstraint": "ap-south-1"}
    )

    # moto has no Rekognition create_collection/delete_collection support — monkeypatched
    # the same way profile's tests capture detect_face_count instead of exercising it.
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
    assert json.loads(stats_response["body"]) == {"photoCount": 0, "storageBytes": 0}

    archive_response = lambda_handler(
        _api_event(
            "POST", f"/events/{event_id}/archive", claims={"sub": "user_1"}, path_parameters={"event_id": event_id}
        ),
        _FakeLambdaContext(),
    )
    assert archive_response["statusCode"] == 200
    assert events_table.get_item(Key={"eventID": event_id})["Item"]["status"] == "ARCHIVED"


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
