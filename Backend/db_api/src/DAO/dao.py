import os

import boto3


# Built lazily, not at import time — a module-level client would bind to whatever AWS
# mocking/config is (or isn't) active at first import, which can be before a test's own
# mock context has started.
def _table():
    return boto3.resource("dynamodb").Table(os.environ["JOBS_TABLE_NAME"])


def create_job(item: dict) -> None:
    _table().put_item(Item=item)


# "status" (and others) are DynamoDB reserved words, so every attribute goes through
# ExpressionAttributeNames unconditionally rather than special-casing which ones need it.
def update_job_status(job_id: str, updates: dict) -> None:
    expression_parts = []
    expression_names = {}
    expression_values = {}
    for i, (key, value) in enumerate(updates.items()):
        name_placeholder = f"#n{i}"
        value_placeholder = f":v{i}"
        expression_parts.append(f"{name_placeholder} = {value_placeholder}")
        expression_names[name_placeholder] = key
        expression_values[value_placeholder] = value

    _table().update_item(
        Key={"jobId": job_id},
        UpdateExpression="SET " + ", ".join(expression_parts),
        ExpressionAttributeNames=expression_names,
        ExpressionAttributeValues=expression_values,
    )
