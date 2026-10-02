import os
from datetime import datetime, timedelta, timezone

import boto3
from botocore.exceptions import ClientError


def _table(name):
    return boto3.resource("dynamodb").Table(os.environ[name])


def get_user(user_id):
    return _table("USERS_TABLE_NAME").get_item(Key={"userID": user_id}, ConsistentRead=True).get("Item")


def get_event(event_id):
    return _table("EVENTS_TABLE_NAME").get_item(Key={"eventID": event_id}, ConsistentRead=True).get("Item")


def list_admitted_user_ids(event_id):
    table = _table("EVENT_ATTENDEES_TABLE_NAME")
    kwargs = {
        "IndexName": "eventID-status-index",
        "KeyConditionExpression": "eventID = :event AND #s = :status",
        "ExpressionAttributeNames": {"#s": "status"},
        "ExpressionAttributeValues": {":event": event_id, ":status": "ATTENDEE"},
    }
    while True:
        response = table.query(**kwargs)
        for item in response["Items"]:
            yield item["userID"]
        if "LastEvaluatedKey" not in response:
            return
        kwargs["ExclusiveStartKey"] = response["LastEvaluatedKey"]


def claim_notification(notification_id):
    now = int(datetime.now(timezone.utc).timestamp())
    try:
        _table("NOTIFICATIONS_TABLE_NAME").put_item(
            Item={
                "notificationID": notification_id,
                "status": "PENDING",
                "leaseUntil": now + 300,
                "expiresAt": int((datetime.now(timezone.utc) + timedelta(days=90)).timestamp()),
            },
            ConditionExpression="attribute_not_exists(notificationID)",
        )
        return True
    except ClientError as error:
        if error.response["Error"]["Code"] != "ConditionalCheckFailedException":
            raise
    try:
        _table("NOTIFICATIONS_TABLE_NAME").update_item(
            Key={"notificationID": notification_id},
            UpdateExpression="SET leaseUntil = :lease",
            ConditionExpression="#s = :pending AND leaseUntil < :now",
            ExpressionAttributeNames={"#s": "status"},
            ExpressionAttributeValues={":pending": "PENDING", ":now": now, ":lease": now + 300},
        )
        return True
    except ClientError as error:
        if error.response["Error"]["Code"] == "ConditionalCheckFailedException":
            return False
        raise


def release_notification(notification_id):
    _table("NOTIFICATIONS_TABLE_NAME").delete_item(Key={"notificationID": notification_id})


def mark_sent(notification_id):
    _table("NOTIFICATIONS_TABLE_NAME").update_item(
        Key={"notificationID": notification_id},
        UpdateExpression="SET #s = :sent, sentAt = :now",
        ExpressionAttributeNames={"#s": "status"},
        ExpressionAttributeValues={":sent": "SENT", ":now": datetime.now(timezone.utc).isoformat()},
    )


def send_email(recipient, subject, html_body, text_body):
    boto3.client("sesv2").send_email(
        FromEmailAddress=os.environ["SES_SENDER_EMAIL"],
        Destination={"ToAddresses": [recipient]},
        Content={"Simple": {
            "Subject": {"Data": subject, "Charset": "UTF-8"},
            "Body": {
                "Html": {"Data": html_body, "Charset": "UTF-8"},
                "Text": {"Data": text_body, "Charset": "UTF-8"},
            },
        }},
    )
