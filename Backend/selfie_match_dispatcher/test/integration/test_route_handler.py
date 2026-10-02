import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import boto3
from moto import mock_aws

import Manager.manager as manager
from routeHandler import lambda_handler


class _FakeContext:
    function_name = "selfie-match-dispatcher"
    memory_limit_in_mb = 256
    invoked_function_arn = "arn:aws:lambda:ap-south-1:000000000000:function:selfie-match-dispatcher"
    aws_request_id = "test-request-id"


@mock_aws
def test_dispatch_reads_memberships_and_schedules_only_admitted(monkeypatch):
    dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
    dynamodb.create_table(
        TableName=os.environ["USERS_TABLE_NAME"],
        KeySchema=[{"AttributeName": "userID", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "userID", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )
    dynamodb.create_table(
        TableName=os.environ["EVENT_ATTENDEES_TABLE_NAME"],
        KeySchema=[{"AttributeName": "userID", "KeyType": "HASH"}, {"AttributeName": "eventID", "KeyType": "RANGE"}],
        AttributeDefinitions=[{"AttributeName": "userID", "AttributeType": "S"}, {"AttributeName": "eventID", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )
    dynamodb.Table(os.environ["USERS_TABLE_NAME"]).put_item(Item={"userID": "u1", "selfieVersion": "v1"})
    table = dynamodb.Table(os.environ["EVENT_ATTENDEES_TABLE_NAME"])
    table.put_item(Item={"userID": "u1", "eventID": "e1", "status": "ATTENDEE"})
    table.put_item(Item={"userID": "u1", "eventID": "e2", "status": "PENDING"})
    calls = []
    monkeypatch.setattr(manager, "invoke_ingestion", lambda function, payload: calls.append(payload))

    assert lambda_handler({"userID": "u1", "selfieVersion": "v1"}, _FakeContext()) == {
        "userID": "u1", "scheduledCount": 1,
    }
    assert calls == [{"step": "match_attendees", "eventID": "e1", "userID": "u1", "selfieVersion": "v1"}]
