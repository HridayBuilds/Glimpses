import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import boto3
from moto import mock_aws

from routeHandler import lambda_handler


class _FakeLambdaContext:
    function_name = "upload_status"
    memory_limit_in_mb = 128
    invoked_function_arn = "arn:aws:lambda:ap-south-1:000000000000:function:upload_status"
    aws_request_id = "test-request-id"


def _api_event(http_method, path, claims=None):
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
        "body": None,
        "isBase64Encoded": False,
    }


def _create_jobs_table(dynamodb):
    dynamodb.create_table(
        TableName=os.environ["JOBS_TABLE_NAME"],
        KeySchema=[{"AttributeName": "jobId", "KeyType": "HASH"}],
        AttributeDefinitions=[
            {"AttributeName": "jobId", "AttributeType": "S"},
            {"AttributeName": "eventUploaderKey", "AttributeType": "S"},
            {"AttributeName": "startedAt", "AttributeType": "S"},
        ],
        GlobalSecondaryIndexes=[
            {
                "IndexName": "eventUploaderKey-startedAt-index",
                "KeySchema": [
                    {"AttributeName": "eventUploaderKey", "KeyType": "HASH"},
                    {"AttributeName": "startedAt", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
            }
        ],
        BillingMode="PAY_PER_REQUEST",
    )


def _create_events_table(dynamodb):
    dynamodb.create_table(
        TableName=os.environ["EVENTS_TABLE_NAME"],
        KeySchema=[{"AttributeName": "eventID", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "eventID", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )


@mock_aws
def test_mint_upload_url_returns_job_id_and_signed_url():
    dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
    _create_jobs_table(dynamodb)
    _create_events_table(dynamodb)
    dynamodb.Table(os.environ["EVENTS_TABLE_NAME"]).put_item(
        Item={
            "eventID": "evt_1",
            "organizerID": "organizer_1",
            "status": "ACTIVE",
            "contributionPolicy": "ATTENDEES_CAN_ADD",
        }
    )

    s3 = boto3.client("s3", region_name="ap-south-1")
    s3.create_bucket(
        Bucket=os.environ["PHOTOS_BUCKET"], CreateBucketConfiguration={"LocationConstraint": "ap-south-1"}
    )

    response = lambda_handler(
        _api_event("POST", "/events/evt_1/upload-url", claims={"sub": "user_1"}), _FakeLambdaContext()
    )

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert "jobId" in body
    assert f"uploads/event/evt_1/user/user_1/job/{body['jobId']}/original.zip" in body["uploadUrl"]


@mock_aws
def test_mint_upload_url_rejects_attendee_when_organizer_only():
    dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
    _create_jobs_table(dynamodb)
    _create_events_table(dynamodb)
    dynamodb.Table(os.environ["EVENTS_TABLE_NAME"]).put_item(
        Item={
            "eventID": "evt_1",
            "organizerID": "organizer_1",
            "status": "ACTIVE",
            "contributionPolicy": "ORGANIZER_ONLY",
        }
    )

    try:
        lambda_handler(_api_event("POST", "/events/evt_1/upload-url", claims={"sub": "user_1"}), _FakeLambdaContext())
        assert False, "expected ValueError"
    except ValueError:
        pass


@mock_aws
def test_mint_upload_url_rejects_archived_event():
    dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
    _create_jobs_table(dynamodb)
    _create_events_table(dynamodb)
    dynamodb.Table(os.environ["EVENTS_TABLE_NAME"]).put_item(
        Item={
            "eventID": "evt_1",
            "organizerID": "organizer_1",
            "status": "ARCHIVED",
            "contributionPolicy": "ATTENDEES_CAN_ADD",
        }
    )

    try:
        lambda_handler(
            _api_event("POST", "/events/evt_1/upload-url", claims={"sub": "organizer_1"}), _FakeLambdaContext()
        )
        assert False, "expected ValueError"
    except ValueError:
        pass


@mock_aws
def test_job_status_reflects_row_written_by_db_api():
    dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
    _create_jobs_table(dynamodb)
    jobs_table = dynamodb.Table(os.environ["JOBS_TABLE_NAME"])
    jobs_table.put_item(
        Item={
            "jobId": "job_1",
            "eventID": "evt_1",
            "uploaderID": "user_1",
            "eventUploaderKey": "evt_1#user_1",
            "status": "INDEXING",
            "startedAt": "2026-08-23T00:00:00Z",
            "succeededCount": 0,
            "failedCount": 0,
        }
    )

    response = lambda_handler(
        _api_event("GET", "/events/evt_1/jobs/job_1/status", claims={"sub": "user_1"}), _FakeLambdaContext()
    )

    assert response["statusCode"] == 200
    assert json.loads(response["body"]) == {
        "jobId": "job_1",
        "status": "INDEXING",
        "startedAt": "2026-08-23T00:00:00Z",
        "succeededCount": 0,
        "failedCount": 0,
    }


@mock_aws
def test_job_status_rejects_caller_who_is_not_the_uploader():
    dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
    _create_jobs_table(dynamodb)
    dynamodb.Table(os.environ["JOBS_TABLE_NAME"]).put_item(
        Item={
            "jobId": "job_1",
            "eventID": "evt_1",
            "uploaderID": "user_1",
            "eventUploaderKey": "evt_1#user_1",
            "status": "INDEXING",
            "startedAt": "2026-08-23T00:00:00Z",
            "succeededCount": 0,
            "failedCount": 0,
        }
    )

    try:
        lambda_handler(
            _api_event("GET", "/events/evt_1/jobs/job_1/status", claims={"sub": "user_2"}), _FakeLambdaContext()
        )
        assert False, "expected ValueError"
    except ValueError:
        pass


@mock_aws
def test_latest_job_returns_most_recently_started_job_for_that_uploader():
    dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
    _create_jobs_table(dynamodb)
    jobs_table = dynamodb.Table(os.environ["JOBS_TABLE_NAME"])
    jobs_table.put_item(
        Item={
            "jobId": "job_older",
            "eventID": "evt_1",
            "uploaderID": "user_1",
            "eventUploaderKey": "evt_1#user_1",
            "status": "SUCCESS",
            "startedAt": "2026-08-20T00:00:00Z",
            "succeededCount": 10,
            "failedCount": 0,
        }
    )
    jobs_table.put_item(
        Item={
            "jobId": "job_newer",
            "eventID": "evt_1",
            "uploaderID": "user_1",
            "eventUploaderKey": "evt_1#user_1",
            "status": "EXTRACTING",
            "startedAt": "2026-08-23T00:00:00Z",
            "succeededCount": 0,
            "failedCount": 0,
        }
    )
    jobs_table.put_item(
        Item={
            "jobId": "job_other_uploader",
            "eventID": "evt_1",
            "uploaderID": "user_2",
            "eventUploaderKey": "evt_1#user_2",
            "status": "SUCCESS",
            "startedAt": "2026-08-24T00:00:00Z",
            "succeededCount": 5,
            "failedCount": 0,
        }
    )

    response = lambda_handler(
        _api_event("GET", "/events/evt_1/jobs/latest", claims={"sub": "user_1"}), _FakeLambdaContext()
    )

    assert response["statusCode"] == 200
    assert json.loads(response["body"])["jobId"] == "job_newer"


@mock_aws
def test_latest_job_raises_when_uploader_has_no_jobs_in_event():
    dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
    _create_jobs_table(dynamodb)

    try:
        lambda_handler(_api_event("GET", "/events/evt_1/jobs/latest", claims={"sub": "user_1"}), _FakeLambdaContext())
        assert False, "expected ValueError"
    except ValueError:
        pass
