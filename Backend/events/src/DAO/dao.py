import json
import os

import boto3

ACTIVE_STATUS = "ACTIVE"
BATCH_GET_LIMIT = 100


def _dynamodb():
    return boto3.resource("dynamodb")


def _events_table():
    return _dynamodb().Table(os.environ["EVENTS_TABLE_NAME"])


def _event_attendees_table():
    return _dynamodb().Table(os.environ["EVENT_ATTENDEES_TABLE_NAME"])


def _s3():
    return boto3.client("s3")


def _rekognition():
    return boto3.client("rekognition")


def _lambda_client():
    return boto3.client("lambda")


def get_event(event_id):
    response = _events_table().get_item(Key={"eventID": event_id})
    return response.get("Item")


def put_event(item):
    _events_table().put_item(Item=item)


def update_event(event_id, fields):
    if not fields:
        return
    update_expression = "SET " + ", ".join(f"#{name} = :{name}" for name in fields)
    _events_table().update_item(
        Key={"eventID": event_id},
        UpdateExpression=update_expression,
        ExpressionAttributeNames={f"#{name}": name for name in fields},
        ExpressionAttributeValues={f":{name}": value for name, value in fields.items()},
    )


def list_events_for_organizer(organizer_id):
    response = _events_table().query(
        IndexName="organizerID-status-index",
        KeyConditionExpression="organizerID = :o",
        ExpressionAttributeValues={":o": organizer_id},
    )
    return response["Items"]


def list_attendee_rows_for_user(user_id):
    response = _event_attendees_table().query(
        KeyConditionExpression="userID = :u",
        ExpressionAttributeValues={":u": user_id},
    )
    return response["Items"]


def count_attendees(event_id, status, exclude_user_id=None):
    kwargs = {
        "IndexName": "eventID-status-index",
        "KeyConditionExpression": "eventID = :e AND #s = :s",
        "ExpressionAttributeNames": {"#s": "status"},
        "ExpressionAttributeValues": {":e": event_id, ":s": status},
        "Select": "COUNT",
    }
    if exclude_user_id is not None:
        kwargs["FilterExpression"] = "userID <> :excluded"
        kwargs["ExpressionAttributeValues"][":excluded"] = exclude_user_id
    response = _event_attendees_table().query(**kwargs)
    return response["Count"]


def put_attendee(item):
    _event_attendees_table().put_item(Item=item)


def batch_get_events(event_ids):
    if not event_ids:
        return []
    table_name = os.environ["EVENTS_TABLE_NAME"]
    dynamodb = _dynamodb()
    items = []
    for offset in range(0, len(event_ids), BATCH_GET_LIMIT):
        batch = event_ids[offset : offset + BATCH_GET_LIMIT]
        keys = [{"eventID": event_id} for event_id in batch]
        response = dynamodb.batch_get_item(RequestItems={table_name: {"Keys": keys}})
        items.extend(response["Responses"][table_name])
    return items


def access_code_exists(access_code):
    response = _events_table().query(
        IndexName="accessCode-index",
        KeyConditionExpression="accessCode = :c",
        ExpressionAttributeValues={":c": access_code},
    )
    return response["Count"] > 0


def list_stale_active_events(cutoff_iso):
    response = _events_table().query(
        IndexName="status-lastUploadAt-index",
        KeyConditionExpression="#s = :s AND lastUploadAt <= :cutoff",
        ExpressionAttributeNames={"#s": "status"},
        ExpressionAttributeValues={":s": ACTIVE_STATUS, ":cutoff": cutoff_iso},
    )
    return response["Items"]


def create_collection(collection_id):
    _rekognition().create_collection(CollectionId=collection_id)


def delete_collection(collection_id):
    _rekognition().delete_collection(CollectionId=collection_id)


def put_object(bucket, key, body, content_type=None, content_disposition=None):
    kwargs = {"Bucket": bucket, "Key": key, "Body": body}
    if content_type is not None:
        kwargs["ContentType"] = content_type
    if content_disposition is not None:
        kwargs["ContentDisposition"] = content_disposition
    _s3().put_object(**kwargs)


def invoke_cascade_delete(event_id):
    function_name = os.environ.get("CASCADE_DELETE_FUNCTION_NAME")
    if not function_name:
        return
    _lambda_client().invoke(
        FunctionName=function_name,
        InvocationType="Event",
        Payload=json.dumps({"action": "delete_event", "eventID": event_id}).encode("utf-8"),
    )
