import os

import boto3
from botocore.exceptions import ClientError

SELFIE_CACHE_CONTROL = "private, max-age=86400"
GET_EXPIRES_IN = 86400
PUT_EXPIRES_IN = 3600


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


def create_user(user_id, email, display_name):
    try:
        _users_table().put_item(
            Item={"userID": user_id, "email": email, "displayName": display_name},
            ConditionExpression="attribute_not_exists(userID)",
        )
    except ClientError as error:
        if error.response["Error"]["Code"] != "ConditionalCheckFailedException":
            raise


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
        if error.response["Error"]["Code"] in ("404", "NoSuchKey", "403"):
            return False
        raise


def delete_object(bucket, key):
    _s3().delete_object(Bucket=bucket, Key=key)


def detect_face_count(bucket, key):
    response = _rekognition().detect_faces(Image={"S3Object": {"Bucket": bucket, "Name": key}})
    return len(response["FaceDetails"])
