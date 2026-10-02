import json
import os

import boto3


def get_user(user_id):
    response = boto3.resource("dynamodb").Table(os.environ["USERS_TABLE_NAME"]).get_item(
        Key={"userID": user_id}, ConsistentRead=True
    )
    return response.get("Item")


def list_attendee_rows_for_user(user_id):
    table = boto3.resource("dynamodb").Table(os.environ["EVENT_ATTENDEES_TABLE_NAME"])
    kwargs = {
        "KeyConditionExpression": "userID = :userID",
        "ExpressionAttributeValues": {":userID": user_id},
        "ConsistentRead": True,
    }
    while True:
        response = table.query(**kwargs)
        yield from response["Items"]
        if "LastEvaluatedKey" not in response:
            return
        kwargs["ExclusiveStartKey"] = response["LastEvaluatedKey"]


def invoke_ingestion(function_name, payload):
    boto3.client("lambda").invoke(
        FunctionName=function_name,
        InvocationType="Event",
        Payload=json.dumps(payload).encode("utf-8"),
    )
