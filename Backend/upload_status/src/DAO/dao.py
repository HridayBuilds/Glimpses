import os

import boto3

JOBS_GSI = "eventUploaderKey-startedAt-index"
PUT_EXPIRES_IN = 3600


def _jobs_table():
    return boto3.resource("dynamodb").Table(os.environ["JOBS_TABLE_NAME"])


def _events_table():
    return boto3.resource("dynamodb").Table(os.environ["EVENTS_TABLE_NAME"])


def _s3():
    return boto3.client("s3")


def generate_presigned_put_url(key):
    return _s3().generate_presigned_url(
        "put_object",
        Params={"Bucket": os.environ["PHOTOS_BUCKET"], "Key": key, "ContentType": "application/zip"},
        ExpiresIn=PUT_EXPIRES_IN,
    )


def get_event(event_id):
    response = _events_table().get_item(Key={"eventID": event_id})
    return response.get("Item")


def get_job(job_id):
    response = _jobs_table().get_item(Key={"jobId": job_id})
    return response.get("Item")


def query_latest_job(event_id, user_id):
    response = _jobs_table().query(
        IndexName=JOBS_GSI,
        KeyConditionExpression="eventUploaderKey = :k",
        ExpressionAttributeValues={":k": f"{event_id}#{user_id}"},
        ScanIndexForward=False,
        Limit=1,
    )
    items = response["Items"]
    return items[0] if items else None
