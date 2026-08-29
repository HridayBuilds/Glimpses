import json
import os

import boto3
from botocore.signers import CloudFrontSigner
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

PHOTOS_GSI = "eventID-uploadedAtFilename-index"
BATCH_GET_LIMIT = 100


def _photos_table():
    return boto3.resource("dynamodb").Table(os.environ["PHOTOS_TABLE_NAME"])


def _events_table():
    return boto3.resource("dynamodb").Table(os.environ["EVENTS_TABLE_NAME"])


def _event_attendees_table():
    return boto3.resource("dynamodb").Table(os.environ["EVENT_ATTENDEES_TABLE_NAME"])


def _s3():
    return boto3.client("s3")


def _lambda_client():
    return boto3.client("lambda")


_private_key_cache = None


def _get_private_key():
    global _private_key_cache
    if _private_key_cache is None:
        _private_key_cache = serialization.load_pem_private_key(
            os.environ["CLOUDFRONT_PRIVATE_KEY"].encode(), password=None
        )
    return _private_key_cache


def sign_cloudfront_url(url, expires_at):
    def _rsa_signer(message):
        return _get_private_key().sign(message, padding.PKCS1v15(), hashes.SHA1())

    signer = CloudFrontSigner(os.environ["CLOUDFRONT_KEY_PAIR_ID"], _rsa_signer)
    return signer.generate_presigned_url(url, date_less_than=expires_at)


def get_photo_by_id(photo_id):
    response = _photos_table().get_item(Key={"photoID": photo_id})
    return response.get("Item")


def query_photos_page(event_id, exclusive_start_key, limit):
    kwargs = {
        "IndexName": PHOTOS_GSI,
        "KeyConditionExpression": "eventID = :eventID",
        "ExpressionAttributeValues": {":eventID": event_id},
        "ScanIndexForward": False,
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


def get_attendee(user_id, event_id):
    response = _event_attendees_table().get_item(Key={"userID": user_id, "eventID": event_id})
    return response.get("Item")


def generate_presigned_url(bucket, key, expires_in=900):
    return _s3().generate_presigned_url("get_object", Params={"Bucket": bucket, "Key": key}, ExpiresIn=expires_in)


def invoke_cascade_delete(event_id, photo_ids):
    function_name = os.environ.get("CASCADE_DELETE_FUNCTION_NAME")
    if not function_name:
        return
    _lambda_client().invoke(
        FunctionName=function_name,
        InvocationType="Event",
        Payload=json.dumps({"action": "delete_photos", "eventID": event_id, "photoIDs": photo_ids}).encode("utf-8"),
    )
