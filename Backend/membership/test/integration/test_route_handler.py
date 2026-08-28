import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import boto3
from moto import mock_aws

from routeHandler import lambda_handler


class _FakeLambdaContext:
    function_name = "membership"
    memory_limit_in_mb = 256
    invoked_function_arn = "arn:aws:lambda:ap-south-1:000000000000:function:membership"
    aws_request_id = "test-request-id"


def _api_event(http_method, path, body=None, claims=None, path_parameters=None, query_string_parameters=None):
    return {
        "resource": path,
        "path": path,
        "httpMethod": http_method,
        "headers": {"Content-Type": "application/json"},
        "multiValueHeaders": {},
        "queryStringParameters": query_string_parameters,
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


def _create_events_table(dynamodb):
    dynamodb.create_table(
        TableName=os.environ["EVENTS_TABLE_NAME"],
        KeySchema=[{"AttributeName": "eventID", "KeyType": "HASH"}],
        AttributeDefinitions=[
            {"AttributeName": "eventID", "AttributeType": "S"},
            {"AttributeName": "accessCode", "AttributeType": "S"},
        ],
        GlobalSecondaryIndexes=[
            {
                "IndexName": "accessCode-index",
                "KeySchema": [{"AttributeName": "accessCode", "KeyType": "HASH"}],
                "Projection": {"ProjectionType": "ALL"},
            }
        ],
        BillingMode="PAY_PER_REQUEST",
    )


def _create_users_table(dynamodb):
    dynamodb.create_table(
        TableName=os.environ["USERS_TABLE_NAME"],
        KeySchema=[{"AttributeName": "userID", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "userID", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )


def _put_event(dynamodb, **overrides):
    item = {
        "eventID": "evt_1",
        "organizerID": "user_1",
        "status": "ACTIVE",
        "joinPolicy": "OPEN",
        "accessCode": "AB23CD",
    }
    item.update(overrides)
    dynamodb.Table(os.environ["EVENTS_TABLE_NAME"]).put_item(Item=item)
    return item


def _put_user(dynamodb, **overrides):
    item = {"userID": "user_2", "displayName": "Meera", "email": "meera@example.com"}
    item.update(overrides)
    dynamodb.Table(os.environ["USERS_TABLE_NAME"]).put_item(Item=item)
    return item


@mock_aws
def test_join_open_event_admits_directly():
    dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
    _create_event_attendees_table(dynamodb)
    _create_events_table(dynamodb)
    _create_users_table(dynamodb)
    _put_event(dynamodb, joinPolicy="OPEN")

    response = lambda_handler(
        _api_event("POST", "/events/join", body={"accessCode": "AB23CD"}, claims={"sub": "user_2"}),
        _FakeLambdaContext(),
    )

    assert response["statusCode"] == 200
    assert json.loads(response["body"]) == {"eventID": "evt_1", "status": "ATTENDEE"}

    attendees_table = dynamodb.Table(os.environ["EVENT_ATTENDEES_TABLE_NAME"])
    item = attendees_table.get_item(Key={"userID": "user_2", "eventID": "evt_1"})["Item"]
    assert item["status"] == "ATTENDEE"


@mock_aws
def test_join_rejects_organizer_joining_own_event():
    dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
    _create_event_attendees_table(dynamodb)
    _create_events_table(dynamodb)
    _create_users_table(dynamodb)
    _put_event(dynamodb, joinPolicy="OPEN")

    try:
        lambda_handler(
            _api_event("POST", "/events/join", body={"accessCode": "AB23CD"}, claims={"sub": "user_1"}),
            _FakeLambdaContext(),
        )
        assert False, "expected ValueError"
    except ValueError:
        pass


@mock_aws
def test_join_approval_required_event_parks_in_lobby_then_organizer_admits():
    dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
    _create_event_attendees_table(dynamodb)
    _create_events_table(dynamodb)
    _create_users_table(dynamodb)
    _put_event(dynamodb, joinPolicy="APPROVAL_REQUIRED")
    _put_user(dynamodb)

    join_response = lambda_handler(
        _api_event("POST", "/events/join", body={"accessCode": "AB23CD"}, claims={"sub": "user_2"}),
        _FakeLambdaContext(),
    )
    assert json.loads(join_response["body"])["status"] == "PENDING"

    lobby_response = lambda_handler(
        _api_event(
            "GET",
            "/events/evt_1/attendees",
            claims={"sub": "user_1"},
            path_parameters={"event_id": "evt_1"},
            query_string_parameters={"status": "PENDING"},
        ),
        _FakeLambdaContext(),
    )
    lobby = json.loads(lobby_response["body"])
    assert lobby == {"attendees": [{"userID": "user_2", "status": "PENDING", "displayName": "Meera", "email": "meera@example.com"}]}

    admit_response = lambda_handler(
        _api_event(
            "POST",
            "/events/evt_1/attendees/user_2/admit",
            claims={"sub": "user_1"},
            path_parameters={"event_id": "evt_1", "user_id": "user_2"},
        ),
        _FakeLambdaContext(),
    )
    assert json.loads(admit_response["body"]) == {"userID": "user_2", "status": "ATTENDEE"}

    attendees_table = dynamodb.Table(os.environ["EVENT_ATTENDEES_TABLE_NAME"])
    item = attendees_table.get_item(Key={"userID": "user_2", "eventID": "evt_1"})["Item"]
    assert item["status"] == "ATTENDEE"


@mock_aws
def test_get_event_info_gates_fields_by_membership_status():
    dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
    _create_event_attendees_table(dynamodb)
    _create_events_table(dynamodb)
    _create_users_table(dynamodb)
    _put_event(
        dynamodb,
        joinPolicy="APPROVAL_REQUIRED",
        name="Priya's Trip",
        description="A weekend away",
        contributionPolicy="ATTENDEES_CAN_ADD",
        accessCode="AB23CD",
        createdAt="2026-08-01T00:00:00+00:00",
    )

    lambda_handler(
        _api_event("POST", "/events/join", body={"accessCode": "AB23CD"}, claims={"sub": "user_2"}),
        _FakeLambdaContext(),
    )

    pending_response = lambda_handler(
        _api_event("GET", "/events/evt_1/info", claims={"sub": "user_2"}, path_parameters={"event_id": "evt_1"}),
        _FakeLambdaContext(),
    )
    assert pending_response["statusCode"] == 200
    pending_body = json.loads(pending_response["body"])
    assert pending_body == {
        "eventID": "evt_1",
        "name": "Priya's Trip",
        "description": "A weekend away",
        "createdAt": "2026-08-01T00:00:00+00:00",
    }

    lambda_handler(
        _api_event(
            "POST",
            "/events/evt_1/attendees/user_2/admit",
            claims={"sub": "user_1"},
            path_parameters={"event_id": "evt_1", "user_id": "user_2"},
        ),
        _FakeLambdaContext(),
    )

    attendee_response = lambda_handler(
        _api_event("GET", "/events/evt_1/info", claims={"sub": "user_2"}, path_parameters={"event_id": "evt_1"}),
        _FakeLambdaContext(),
    )
    attendee_body = json.loads(attendee_response["body"])
    assert attendee_body["accessCode"] == "AB23CD"
    assert attendee_body["qrcodeUrl"].endswith("/qrcodes/event/evt_1/qrcode.png")

    try:
        lambda_handler(
            _api_event("GET", "/events/evt_1/info", claims={"sub": "user_3"}, path_parameters={"event_id": "evt_1"}),
            _FakeLambdaContext(),
        )
        assert False, "expected ValueError"
    except ValueError:
        pass


@mock_aws
def test_deny_blocks_rejoin():
    dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
    _create_event_attendees_table(dynamodb)
    _create_events_table(dynamodb)
    _create_users_table(dynamodb)
    _put_event(dynamodb, joinPolicy="APPROVAL_REQUIRED")

    lambda_handler(
        _api_event("POST", "/events/join", body={"accessCode": "AB23CD"}, claims={"sub": "user_2"}),
        _FakeLambdaContext(),
    )
    deny_response = lambda_handler(
        _api_event(
            "POST",
            "/events/evt_1/attendees/user_2/deny",
            claims={"sub": "user_1"},
            path_parameters={"event_id": "evt_1", "user_id": "user_2"},
        ),
        _FakeLambdaContext(),
    )
    assert json.loads(deny_response["body"]) == {"userID": "user_2", "status": "BLOCKED"}

    try:
        lambda_handler(
            _api_event("POST", "/events/join", body={"accessCode": "AB23CD"}, claims={"sub": "user_2"}),
            _FakeLambdaContext(),
        )
        assert False, "expected ValueError"
    except ValueError:
        pass


@mock_aws
def test_leave_then_rejoin_round_trip():
    dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
    _create_event_attendees_table(dynamodb)
    _create_events_table(dynamodb)
    _create_users_table(dynamodb)
    _put_event(dynamodb, joinPolicy="OPEN")

    lambda_handler(
        _api_event("POST", "/events/join", body={"accessCode": "AB23CD"}, claims={"sub": "user_2"}),
        _FakeLambdaContext(),
    )
    leave_response = lambda_handler(
        _api_event("POST", "/events/evt_1/leave", claims={"sub": "user_2"}, path_parameters={"event_id": "evt_1"}),
        _FakeLambdaContext(),
    )
    assert json.loads(leave_response["body"]) == {"eventID": "evt_1", "status": "LEFT"}

    rejoin_response = lambda_handler(
        _api_event("POST", "/events/join", body={"accessCode": "AB23CD"}, claims={"sub": "user_2"}),
        _FakeLambdaContext(),
    )
    assert json.loads(rejoin_response["body"]) == {"eventID": "evt_1", "status": "ATTENDEE"}


@mock_aws
def test_leave_rejects_organizer_leaving_own_event():
    dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
    _create_event_attendees_table(dynamodb)
    _create_events_table(dynamodb)
    _create_users_table(dynamodb)
    _put_event(dynamodb)

    try:
        lambda_handler(
            _api_event(
                "POST", "/events/evt_1/leave", claims={"sub": "user_1"}, path_parameters={"event_id": "evt_1"}
            ),
            _FakeLambdaContext(),
        )
        assert False, "expected ValueError"
    except ValueError:
        pass


@mock_aws
def test_eject_removes_admitted_attendee():
    dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
    _create_event_attendees_table(dynamodb)
    _create_events_table(dynamodb)
    _create_users_table(dynamodb)
    _put_event(dynamodb, joinPolicy="OPEN")

    lambda_handler(
        _api_event("POST", "/events/join", body={"accessCode": "AB23CD"}, claims={"sub": "user_2"}),
        _FakeLambdaContext(),
    )
    eject_response = lambda_handler(
        _api_event(
            "POST",
            "/events/evt_1/attendees/user_2/eject",
            claims={"sub": "user_1"},
            path_parameters={"event_id": "evt_1", "user_id": "user_2"},
        ),
        _FakeLambdaContext(),
    )
    assert json.loads(eject_response["body"]) == {"userID": "user_2", "status": "BLOCKED"}

    attendees_table = dynamodb.Table(os.environ["EVENT_ATTENDEES_TABLE_NAME"])
    item = attendees_table.get_item(Key={"userID": "user_2", "eventID": "evt_1"})["Item"]
    assert item["status"] == "BLOCKED"


@mock_aws
def test_attendees_list_rejects_non_organizer():
    dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
    _create_event_attendees_table(dynamodb)
    _create_events_table(dynamodb)
    _create_users_table(dynamodb)
    _put_event(dynamodb)

    try:
        lambda_handler(
            _api_event(
                "GET",
                "/events/evt_1/attendees",
                claims={"sub": "someone_else"},
                path_parameters={"event_id": "evt_1"},
                query_string_parameters={"status": "ATTENDEE"},
            ),
            _FakeLambdaContext(),
        )
        assert False, "expected ValueError"
    except ValueError:
        pass
