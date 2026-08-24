import json
import os

import boto3

PHOTOS_GSI = "eventID-uploadedAtFilename-index"
BATCH_GET_LIMIT = 100  # BatchGetItem's own per-call key limit


# Built lazily, not at import time — a module-level client/resource would bind to
# whatever AWS mocking/config is (or isn't) active at first import, which can be before
# a test's own mock context has started (the same db_api moto lesson).
def _photos_table():
    return boto3.resource("dynamodb").Table(os.environ["PHOTOS_TABLE_NAME"])


# Read-only — gallery never writes Photos. CascadeDelete owns the actual row deletion
# (T-07 discipline: permissions derived from actual AWS calls only).
def _events_table():
    return boto3.resource("dynamodb").Table(os.environ["EVENTS_TABLE_NAME"])


def _event_attendees_table():
    return boto3.resource("dynamodb").Table(os.environ["EVENT_ATTENDEES_TABLE_NAME"])


def _s3():
    return boto3.client("s3")


def _lambda_client():
    return boto3.client("lambda")


def get_photo_by_id(photo_id):
    response = _photos_table().get_item(Key={"photoID": photo_id})
    return response.get("Item")


def query_photos_page(event_id, exclusive_start_key, limit):
    kwargs = {
        "IndexName": PHOTOS_GSI,
        "KeyConditionExpression": "eventID = :eventID",
        "ExpressionAttributeValues": {":eventID": event_id},
        "ScanIndexForward": False,  # P-57: newest-first
        "Limit": limit,
    }
    if exclusive_start_key is not None:
        kwargs["ExclusiveStartKey"] = exclusive_start_key
    response = _photos_table().query(**kwargs)
    return response["Items"], response.get("LastEvaluatedKey")


def batch_get_photos(photo_ids):
    if not photo_ids:
        return []
    table_name = os.environ["PHOTOS_TABLE_NAME"]
    dynamodb = boto3.resource("dynamodb")
    items = []
    for offset in range(0, len(photo_ids), BATCH_GET_LIMIT):
        batch = photo_ids[offset : offset + BATCH_GET_LIMIT]
        keys = [{"photoID": photo_id} for photo_id in batch]
        response = dynamodb.batch_get_item(RequestItems={table_name: {"Keys": keys}})
        items.extend(response["Responses"][table_name])
    return items


def get_event(event_id):
    response = _events_table().get_item(Key={"eventID": event_id})
    return response.get("Item")


# Own row only, never Query/Scan across other attendees (P-16/P-17 mine=true resolution).
def get_attendee(user_id, event_id):
    response = _event_attendees_table().get_item(Key={"userID": user_id, "eventID": event_id})
    return response.get("Item")


def generate_presigned_url(bucket, key, expires_in=3600):
    return _s3().generate_presigned_url("get_object", Params={"Bucket": bucket, "Key": key}, ExpiresIn=expires_in)


# CascadeDelete isn't built yet — CASCADE_DELETE_FUNCTION_NAME is unset until its
# Terraform module lands, same no-op-until-built pattern events' delete_event already uses.
def invoke_cascade_delete(event_id, photo_ids):
    function_name = os.environ.get("CASCADE_DELETE_FUNCTION_NAME")
    if not function_name:
        return
    _lambda_client().invoke(
        FunctionName=function_name,
        InvocationType="Event",
        Payload=json.dumps({"action": "delete_photos", "eventID": event_id, "photoIDs": photo_ids}).encode("utf-8"),
    )
