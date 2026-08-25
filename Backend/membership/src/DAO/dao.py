import os

import boto3

BATCH_GET_LIMIT = 100


def _dynamodb():
    return boto3.resource("dynamodb")


def _event_attendees_table():
    return _dynamodb().Table(os.environ["EVENT_ATTENDEES_TABLE_NAME"])


def _events_table():
    return _dynamodb().Table(os.environ["EVENTS_TABLE_NAME"])


def _users_table():
    return _dynamodb().Table(os.environ["USERS_TABLE_NAME"])


def get_event(event_id):
    response = _events_table().get_item(Key={"eventID": event_id})
    return response.get("Item")


def get_event_by_access_code(access_code):
    response = _events_table().query(
        IndexName="accessCode-index",
        KeyConditionExpression="accessCode = :c",
        ExpressionAttributeValues={":c": access_code},
    )
    items = response["Items"]
    return items[0] if items else None


def get_attendee(user_id, event_id):
    response = _event_attendees_table().get_item(Key={"userID": user_id, "eventID": event_id})
    return response.get("Item")


def put_attendee(item):
    _event_attendees_table().put_item(Item=item)


def update_attendee_status(user_id, event_id, status):
    _event_attendees_table().update_item(
        Key={"userID": user_id, "eventID": event_id},
        UpdateExpression="SET #s = :s",
        ExpressionAttributeNames={"#s": "status"},
        ExpressionAttributeValues={":s": status},
    )


def list_attendees_by_status(event_id, status):
    response = _event_attendees_table().query(
        IndexName="eventID-status-index",
        KeyConditionExpression="eventID = :e AND #s = :s",
        ExpressionAttributeNames={"#s": "status"},
        ExpressionAttributeValues={":e": event_id, ":s": status},
    )
    return response["Items"]


def get_users(user_ids):
    if not user_ids:
        return []
    table_name = os.environ["USERS_TABLE_NAME"]
    dynamodb = _dynamodb()
    items = []
    for offset in range(0, len(user_ids), BATCH_GET_LIMIT):
        batch = user_ids[offset : offset + BATCH_GET_LIMIT]
        keys = [{"userID": user_id} for user_id in batch]
        response = dynamodb.batch_get_item(RequestItems={table_name: {"Keys": keys}})
        items.extend(response["Responses"][table_name])
    return items
