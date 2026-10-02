import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import boto3
from moto import mock_aws

import Manager.manager as manager


@mock_aws
def test_delivery_is_deduplicated_and_respects_preference(monkeypatch):
    dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
    for env_name, key in (("USERS_TABLE_NAME", "userID"), ("NOTIFICATIONS_TABLE_NAME", "notificationID")):
        dynamodb.create_table(
            TableName=os.environ[env_name],
            KeySchema=[{"AttributeName": key, "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": key, "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )
    users = dynamodb.Table(os.environ["USERS_TABLE_NAME"])
    users.put_item(Item={"userID": "u1", "displayName": "Meera", "email": "meera@example.com"})
    sent = []
    monkeypatch.setattr(manager, "send_email", lambda *args: sent.append(args))
    assert manager._send("approved", "u1", "e1", "Spring Party", "r1") is True
    assert manager._send("approved", "u1", "e1", "Spring Party", "r1") is False
    assert len(sent) == 1

    users.update_item(
        Key={"userID": "u1"}, UpdateExpression="SET emailNotificationsEnabled = :disabled",
        ExpressionAttributeValues={":disabled": False},
    )
    assert manager._send("archived", "u1", "e1", "Spring Party", "r2") is False
    assert len(sent) == 1


@mock_aws
def test_failed_send_releases_claim_for_retry(monkeypatch):
    dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
    for env_name, key in (("USERS_TABLE_NAME", "userID"), ("NOTIFICATIONS_TABLE_NAME", "notificationID")):
        dynamodb.create_table(
            TableName=os.environ[env_name],
            KeySchema=[{"AttributeName": key, "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": key, "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )
    dynamodb.Table(os.environ["USERS_TABLE_NAME"]).put_item(
        Item={"userID": "u1", "displayName": "Meera", "email": "meera@example.com"}
    )
    calls = []

    def fail_once(*args):
        calls.append(args)
        if len(calls) == 1:
            raise RuntimeError("SES unavailable")

    monkeypatch.setattr(manager, "send_email", fail_once)
    try:
        manager._send("approved", "u1", "e1", "Spring Party", "r1")
        assert False, "expected send failure"
    except RuntimeError:
        pass
    assert manager._send("approved", "u1", "e1", "Spring Party", "r1") is True
    assert len(calls) == 2
