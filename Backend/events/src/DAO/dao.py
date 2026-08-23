import json
import os

import boto3

ACTIVE_STATUS = "ACTIVE"


# Built lazily, not at import time — a module-level client/resource would bind to
# whatever AWS mocking/config is (or isn't) active at first import, which can be before
# a test's own mock context has started.
def _dynamodb():
    return boto3.resource("dynamodb")


def _events_table():
    return _dynamodb().Table(os.environ["EVENTS_TABLE_NAME"])


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


def access_code_exists(access_code):
    response = _events_table().query(
        IndexName="accessCode-index",
        KeyConditionExpression="accessCode = :c",
        ExpressionAttributeValues={":c": access_code},
    )
    return response["Count"] > 0


# P-77/P-78 archive sweep: every still-ACTIVE event whose lastUploadAt is 30+ days old.
def list_stale_active_events(cutoff_iso):
    response = _events_table().query(
        IndexName="status-lastUploadAt-index",
        KeyConditionExpression="#s = :s AND lastUploadAt <= :cutoff",
        ExpressionAttributeNames={"#s": "status"},
        ExpressionAttributeValues={":s": ACTIVE_STATUS, ":cutoff": cutoff_iso},
    )
    return response["Items"]


# T-05: one Rekognition collection per event, created/deleted by application code —
# Terraform has no visibility into a per-event runtime resource.
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


# CascadeDelete (P-34) isn't built yet — CASCADE_DELETE_FUNCTION_NAME is unset until its
# Terraform module lands, per the build order set 2026-08-23. No-op until then.
def invoke_cascade_delete(event_id):
    function_name = os.environ.get("CASCADE_DELETE_FUNCTION_NAME")
    if not function_name:
        return
    _lambda_client().invoke(
        FunctionName=function_name,
        InvocationType="Event",
        Payload=json.dumps({"action": "delete_event", "eventID": event_id}).encode("utf-8"),
    )
