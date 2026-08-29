import json
import os
from datetime import datetime, timezone

import boto3
from botocore.exceptions import ClientError

BATCH_GET_LIMIT = 100


def _dynamodb():
    return boto3.resource("dynamodb")


def _photos_table():
    return _dynamodb().Table(os.environ["PHOTOS_TABLE_NAME"])


def _events_table():
    return _dynamodb().Table(os.environ["EVENTS_TABLE_NAME"])


def _faces_table():
    return _dynamodb().Table(os.environ["FACES_TABLE_NAME"])


def _event_attendees_table():
    return _dynamodb().Table(os.environ["EVENT_ATTENDEES_TABLE_NAME"])


def _users_table():
    return _dynamodb().Table(os.environ["USERS_TABLE_NAME"])


def _s3():
    return boto3.client("s3")


def _rekognition():
    return boto3.client("rekognition")


def _lambda_client():
    return boto3.client("lambda")


def get_object(bucket, key):
    return _s3().get_object(Bucket=bucket, Key=key)["Body"].read()


def put_object(bucket, key, body, content_type=None):
    kwargs = {"Bucket": bucket, "Key": key, "Body": body}
    if content_type is not None:
        kwargs["ContentType"] = content_type
    _s3().put_object(**kwargs)


def delete_object(bucket, key):
    _s3().delete_object(Bucket=bucket, Key=key)


def selfie_exists(bucket, key):
    try:
        _s3().head_object(Bucket=bucket, Key=key)
        return True
    except ClientError as error:
        # Role has no s3:ListBucket, so a missing key comes back as 403, not 404.
        if error.response["Error"]["Code"] in ("404", "NoSuchKey", "403"):
            return False
        raise


def index_faces(collection_id, bucket, key):
    response = _rekognition().index_faces(
        CollectionId=collection_id,
        Image={"S3Object": {"Bucket": bucket, "Name": key}},
    )
    return response["FaceRecords"]


def search_faces_by_image(collection_id, bucket, key, threshold):
    response = _rekognition().search_faces_by_image(
        CollectionId=collection_id,
        Image={"S3Object": {"Bucket": bucket, "Name": key}},
        FaceMatchThreshold=threshold,
    )
    return response["FaceMatches"]


def get_event(event_id):
    response = _events_table().get_item(Key={"eventID": event_id})
    return response.get("Item")


def increment_event_counters(event_id, photo_count_delta=0, size_bytes_delta=0):
    _events_table().update_item(
        Key={"eventID": event_id},
        UpdateExpression="ADD photoCount :p, storageBytes :s SET lastUploadAt = :t",
        ExpressionAttributeValues={
            ":p": photo_count_delta,
            ":s": size_bytes_delta,
            ":t": datetime.now(timezone.utc).isoformat(),
        },
    )


def get_user(user_id):
    response = _users_table().get_item(Key={"userID": user_id})
    return response.get("Item")


def put_photo_if_absent(item):
    try:
        _photos_table().put_item(Item=item, ConditionExpression="attribute_not_exists(photoID)")
        return True
    except ClientError as error:
        if error.response["Error"]["Code"] == "ConditionalCheckFailedException":
            return False
        raise


def put_face(item):
    _faces_table().put_item(Item=item)


def get_faces(face_ids):
    if not face_ids:
        return []
    table_name = os.environ["FACES_TABLE_NAME"]
    dynamodb = _dynamodb()
    items = []
    for offset in range(0, len(face_ids), BATCH_GET_LIMIT):
        batch = face_ids[offset : offset + BATCH_GET_LIMIT]
        keys = [{"rekognitionFaceID": face_id} for face_id in batch]
        response = dynamodb.batch_get_item(RequestItems={table_name: {"Keys": keys}})
        items.extend(response["Responses"][table_name])
    return items


def list_admitted_attendees(event_id):
    response = _event_attendees_table().query(
        IndexName="eventID-status-index",
        KeyConditionExpression="eventID = :e AND #s = :s",
        ExpressionAttributeNames={"#s": "status"},
        ExpressionAttributeValues={":e": event_id, ":s": "ATTENDEE"},
    )
    return [item["userID"] for item in response["Items"]]


def add_matched_photo_ids(user_id, event_id, photo_ids):
    if not photo_ids:
        return
    _event_attendees_table().update_item(
        Key={"userID": user_id, "eventID": event_id},
        UpdateExpression="ADD matchedPhotoIDs :p",
        ExpressionAttributeValues={":p": set(photo_ids)},
    )


def invoke_heic_converter(bucket, key):
    function_name = os.environ["HEIC_CONVERTER_FUNCTION_NAME"]
    response = _lambda_client().invoke(
        FunctionName=function_name,
        InvocationType="RequestResponse",
        Payload=json.dumps({"bucket": bucket, "key": key}).encode("utf-8"),
    )
    result = json.loads(response["Payload"].read())
    return result["key"]
