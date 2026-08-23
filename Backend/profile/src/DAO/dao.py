import os

import boto3
from botocore.exceptions import ClientError

# T-09: paired with the object's Cache-Control metadata (set below via the presigned PUT's
# signed params) so the browser's cache doesn't go stale before the signature would.
SELFIE_CACHE_CONTROL = "private, max-age=86400"
GET_EXPIRES_IN = 86400
PUT_EXPIRES_IN = 3600


# Built lazily, not at import time — a module-level client/resource would bind to
# whatever AWS mocking/config is (or isn't) active at first import, which can be before
# a test's own mock context has started.
def _dynamodb():
    return boto3.resource("dynamodb")


def _users_table():
    return _dynamodb().Table(os.environ["USERS_TABLE_NAME"])


def _s3():
    return boto3.client("s3")


def _rekognition():
    return boto3.client("rekognition")


def get_user(user_id):
    response = _users_table().get_item(Key={"userID": user_id})
    return response.get("Item")


def update_display_name(user_id, display_name):
    _users_table().update_item(
        Key={"userID": user_id},
        UpdateExpression="SET displayName = :d",
        ExpressionAttributeValues={":d": display_name},
    )


def generate_presigned_put_url(bucket, key):
    return _s3().generate_presigned_url(
        "put_object",
        Params={
            "Bucket": bucket,
            "Key": key,
            "ContentType": "image/jpeg",
            "CacheControl": SELFIE_CACHE_CONTROL,
        },
        ExpiresIn=PUT_EXPIRES_IN,
    )


def generate_presigned_get_url(bucket, key):
    return _s3().generate_presigned_url(
        "get_object", Params={"Bucket": bucket, "Key": key}, ExpiresIn=GET_EXPIRES_IN
    )


def selfie_exists(bucket, key):
    try:
        _s3().head_object(Bucket=bucket, Key=key)
        return True
    except ClientError as error:
        if error.response["Error"]["Code"] in ("404", "NoSuchKey"):
            return False
        raise


def delete_object(bucket, key):
    _s3().delete_object(Bucket=bucket, Key=key)


# S3Object reference, not inline Bytes — avoids the 5MB inline-payload limit and matches
# ingestion's own index_faces/search_faces_by_image calls. Requires s3:GetObject on the
# key, same as those two calls do.
def detect_face_count(bucket, key):
    response = _rekognition().detect_faces(Image={"S3Object": {"Bucket": bucket, "Name": key}})
    return len(response["FaceDetails"])
