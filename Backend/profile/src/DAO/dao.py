import os
import json

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


def _lambda_client():
    return boto3.client("lambda")


def get_user(user_id):
    response = _users_table().get_item(Key={"userID": user_id}, ConsistentRead=True)
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


def set_email_notifications_enabled(user_id, enabled):
    _users_table().update_item(
        Key={"userID": user_id},
        UpdateExpression="SET emailNotificationsEnabled = :enabled",
        ExpressionAttributeValues={":enabled": enabled},
        ConditionExpression="attribute_exists(userID)",
    )


def set_current_selfie(user_id, key, version):
    _users_table().update_item(
        Key={"userID": user_id},
        UpdateExpression="SET selfieKey = :key, selfieVersion = :version",
        ExpressionAttributeValues={":key": key, ":version": version},
        ConditionExpression="attribute_exists(userID)",
    )


def clear_current_selfie(user_id):
    _users_table().update_item(
        Key={"userID": user_id},
        UpdateExpression="REMOVE selfieKey, selfieVersion",
        ConditionExpression="attribute_exists(userID)",
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


def copy_object(bucket, source_key, target_key):
    _s3().copy_object(
        Bucket=bucket,
        CopySource={"Bucket": bucket, "Key": source_key},
        Key=target_key,
        MetadataDirective="REPLACE",
        ContentType="image/jpeg",
        CacheControl=SELFIE_CACHE_CONTROL,
    )


def invoke_selfie_match_dispatcher(user_id, version):
    _lambda_client().invoke(
        FunctionName=os.environ["SELFIE_MATCH_DISPATCHER_FUNCTION_NAME"],
        InvocationType="Event",
        Payload=json.dumps({"userID": user_id, "selfieVersion": version}).encode("utf-8"),
    )


def detect_face_count(bucket, key):
    response = _rekognition().detect_faces(Image={"S3Object": {"Bucket": bucket, "Name": key}})
    return len(response["FaceDetails"])
