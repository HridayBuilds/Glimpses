import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import boto3
from moto import mock_aws

import Manager.manager as manager
from routeHandler import lambda_handler


class _FakeLambdaContext:
    function_name = "profile"
    memory_limit_in_mb = 128
    invoked_function_arn = "arn:aws:lambda:ap-south-1:000000000000:function:profile"
    aws_request_id = "test-request-id"


def _api_event(http_method, path, body=None, claims=None):
    return {
        "resource": path,
        "path": path,
        "httpMethod": http_method,
        "headers": {"Content-Type": "application/json"},
        "multiValueHeaders": {},
        "queryStringParameters": None,
        "multiValueQueryStringParameters": None,
        "pathParameters": None,
        "stageVariables": None,
        "requestContext": {
            "authorizer": {"claims": claims or {}},
            "resourcePath": path,
            "httpMethod": http_method,
            "path": path,
            "stage": "test",
        },
        "body": json.dumps(body) if body is not None else None,
        "isBase64Encoded": False,
    }


def _create_users_table(dynamodb):
    dynamodb.create_table(
        TableName=os.environ["USERS_TABLE_NAME"],
        KeySchema=[{"AttributeName": "userID", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "userID", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )


@mock_aws
def test_get_then_put_profile_round_trip():
    dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
    _create_users_table(dynamodb)
    users_table = dynamodb.Table(os.environ["USERS_TABLE_NAME"])
    users_table.put_item(Item={"userID": "user_1", "displayName": "Meera", "email": "meera@example.com"})

    s3 = boto3.client("s3", region_name="ap-south-1")
    s3.create_bucket(
        Bucket=os.environ["PHOTOS_BUCKET"], CreateBucketConfiguration={"LocationConstraint": "ap-south-1"}
    )

    get_response = lambda_handler(_api_event("GET", "/profile", claims={"sub": "user_1"}), _FakeLambdaContext())
    assert get_response["statusCode"] == 200
    get_result = json.loads(get_response["body"])
    assert get_result == {"userID": "user_1", "displayName": "Meera", "email": "meera@example.com"}
    assert "selfieUrl" not in get_result

    put_response = lambda_handler(
        _api_event("PUT", "/profile", body={"displayName": "Meera Nair"}, claims={"sub": "user_1"}),
        _FakeLambdaContext(),
    )
    assert put_response["statusCode"] == 200

    updated_row = users_table.get_item(Key={"userID": "user_1"})["Item"]
    assert updated_row["displayName"] == "Meera Nair"


@mock_aws
def test_get_profile_creates_user_on_first_call():
    dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
    _create_users_table(dynamodb)
    users_table = dynamodb.Table(os.environ["USERS_TABLE_NAME"])

    s3 = boto3.client("s3", region_name="ap-south-1")
    s3.create_bucket(
        Bucket=os.environ["PHOTOS_BUCKET"], CreateBucketConfiguration={"LocationConstraint": "ap-south-1"}
    )

    claims = {"sub": "user_new", "email": "meera@example.com", "name": "Meera"}
    get_response = lambda_handler(_api_event("GET", "/profile", claims=claims), _FakeLambdaContext())

    assert get_response["statusCode"] == 200
    assert json.loads(get_response["body"]) == {
        "userID": "user_new",
        "displayName": "Meera",
        "email": "meera@example.com",
    }
    assert users_table.get_item(Key={"userID": "user_new"})["Item"]["email"] == "meera@example.com"


@mock_aws
def test_selfie_mint_confirm_then_get_returns_selfie_url(monkeypatch):
    dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
    _create_users_table(dynamodb)
    dynamodb.Table(os.environ["USERS_TABLE_NAME"]).put_item(
        Item={"userID": "user_1", "displayName": "Meera", "email": "meera@example.com"}
    )

    bucket = os.environ["PHOTOS_BUCKET"]
    s3 = boto3.client("s3", region_name="ap-south-1")
    s3.create_bucket(Bucket=bucket, CreateBucketConfiguration={"LocationConstraint": "ap-south-1"})

    mint_response = lambda_handler(
        _api_event("PUT", "/profile/selfie", claims={"sub": "user_1"}), _FakeLambdaContext()
    )
    assert mint_response["statusCode"] == 200
    assert "uploadUrl" in json.loads(mint_response["body"])

    s3.put_object(Bucket=bucket, Key="selfies/user/user_1/selfie.jpg", Body=b"selfie-bytes")

    monkeypatch.setattr(manager, "detect_face_count", lambda bucket, key: 1)

    confirm_response = lambda_handler(
        _api_event("POST", "/profile/selfie/confirm", claims={"sub": "user_1"}), _FakeLambdaContext()
    )
    assert confirm_response["statusCode"] == 200
    assert json.loads(confirm_response["body"]) == {"confirmed": True}

    get_response = lambda_handler(_api_event("GET", "/profile", claims={"sub": "user_1"}), _FakeLambdaContext())
    get_result = json.loads(get_response["body"])
    assert "selfies/user/user_1/selfie.jpg" in get_result["selfieUrl"]


@mock_aws
def test_confirm_selfie_rejects_and_deletes_when_not_exactly_one_face(monkeypatch):
    dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
    _create_users_table(dynamodb)
    dynamodb.Table(os.environ["USERS_TABLE_NAME"]).put_item(
        Item={"userID": "user_1", "displayName": "Meera", "email": "meera@example.com"}
    )

    bucket = os.environ["PHOTOS_BUCKET"]
    s3 = boto3.client("s3", region_name="ap-south-1")
    s3.create_bucket(Bucket=bucket, CreateBucketConfiguration={"LocationConstraint": "ap-south-1"})
    key = "selfies/user/user_1/selfie.jpg"
    s3.put_object(Bucket=bucket, Key=key, Body=b"selfie-bytes")

    monkeypatch.setattr(manager, "detect_face_count", lambda bucket, key: 0)

    try:
        lambda_handler(_api_event("POST", "/profile/selfie/confirm", claims={"sub": "user_1"}), _FakeLambdaContext())
        assert False, "expected ValueError"
    except ValueError:
        pass

    listed = s3.list_objects_v2(Bucket=bucket, Prefix=key)
    assert listed.get("KeyCount", 0) == 0


@mock_aws
def test_delete_selfie_removes_object():
    dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
    _create_users_table(dynamodb)
    dynamodb.Table(os.environ["USERS_TABLE_NAME"]).put_item(
        Item={"userID": "user_1", "displayName": "Meera", "email": "meera@example.com"}
    )

    bucket = os.environ["PHOTOS_BUCKET"]
    s3 = boto3.client("s3", region_name="ap-south-1")
    s3.create_bucket(Bucket=bucket, CreateBucketConfiguration={"LocationConstraint": "ap-south-1"})
    key = "selfies/user/user_1/selfie.jpg"
    s3.put_object(Bucket=bucket, Key=key, Body=b"selfie-bytes")

    delete_response = lambda_handler(
        _api_event("DELETE", "/profile/selfie", claims={"sub": "user_1"}), _FakeLambdaContext()
    )
    assert delete_response["statusCode"] == 200

    listed = s3.list_objects_v2(Bucket=bucket, Prefix=key)
    assert listed.get("KeyCount", 0) == 0
