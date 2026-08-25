import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import boto3
from moto import mock_aws

from routeHandler import lambda_handler


class _FakeLambdaContext:
    function_name = "db_api"
    memory_limit_in_mb = 128
    invoked_function_arn = "arn:aws:lambda:ap-south-1:000000000000:function:db_api"
    aws_request_id = "test-request-id"


def _create_jobs_table(dynamodb):
    dynamodb.create_table(
        TableName="glimpses-jobs-test",
        KeySchema=[{"AttributeName": "jobId", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "jobId", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )


@mock_aws
def test_create_then_mark_success_round_trip():
    dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
    _create_jobs_table(dynamodb)
    table = dynamodb.Table("glimpses-jobs-test")

    create_result = lambda_handler(
        {
            "action": "create",
            "jobId": "job_1",
            "eventID": "evt_1",
            "uploaderID": "user_1",
            "startedAt": "2026-08-15T10:00:00Z",
        },
        _FakeLambdaContext(),
    )
    assert create_result == {"jobId": "job_1"}

    item = table.get_item(Key={"jobId": "job_1"})["Item"]
    assert item["status"] == "CREATED"
    assert item["eventUploaderKey"] == "evt_1#user_1"
    assert item["succeededCount"] == 0
    assert item["failedCount"] == 0

    update_result = lambda_handler(
        {
            "action": "mark_success",
            "jobId": "job_1",
            "succeededCount": 594,
            "failedCount": 6,
        },
        _FakeLambdaContext(),
    )
    assert update_result == {"jobId": "job_1"}

    item = table.get_item(Key={"jobId": "job_1"})["Item"]
    assert item["status"] == "SUCCESS"
    assert item["succeededCount"] == 594
    assert item["failedCount"] == 6
    assert item["eventUploaderKey"] == "evt_1#user_1"
