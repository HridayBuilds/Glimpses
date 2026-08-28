import json
import os

import boto3

PHOTOS_GSI = "eventID-uploadedAtFilename-index"
BATCH_GET_LIMIT = 100


def _downloads_table():
    return boto3.resource("dynamodb").Table(os.environ["DOWNLOADS_TABLE_NAME"])


def _photos_table():
    return boto3.resource("dynamodb").Table(os.environ["PHOTOS_TABLE_NAME"])


def _s3():
    return boto3.client("s3")


def _lambda_client():
    return boto3.client("lambda")


def create_download(item: dict) -> None:
    _downloads_table().put_item(Item=item)


def get_download(download_id: str) -> dict | None:
    response = _downloads_table().get_item(Key={"downloadId": download_id})
    return response.get("Item")


def update_download_status(download_id: str, updates: dict) -> None:
    expression_parts = []
    expression_names = {}
    expression_values = {}
    for i, (key, value) in enumerate(updates.items()):
        name_placeholder = f"#n{i}"
        value_placeholder = f":v{i}"
        expression_parts.append(f"{name_placeholder} = {value_placeholder}")
        expression_names[name_placeholder] = key
        expression_values[value_placeholder] = value

    _downloads_table().update_item(
        Key={"downloadId": download_id},
        UpdateExpression="SET " + ", ".join(expression_parts),
        ExpressionAttributeNames=expression_names,
        ExpressionAttributeValues=expression_values,
    )


def list_photo_keys(event_id: str, photo_ids: list[str] | None) -> list[str]:
    if photo_ids:
        return _batch_get_photo_keys(photo_ids)
    return _query_all_photo_keys(event_id)


def _batch_get_photo_keys(photo_ids: list[str]) -> list[str]:
    dynamodb = boto3.resource("dynamodb")
    table_name = _photos_table().name
    keys = [{"photoID": photo_id} for photo_id in photo_ids]

    items = []
    for i in range(0, len(keys), BATCH_GET_LIMIT):
        batch = keys[i : i + BATCH_GET_LIMIT]
        response = dynamodb.batch_get_item(RequestItems={table_name: {"Keys": batch}})
        items.extend(response["Responses"][table_name])
    return [item["s3Key"] for item in items]


def _query_all_photo_keys(event_id: str) -> list[str]:
    table = _photos_table()
    kwargs = {
        "IndexName": PHOTOS_GSI,
        "KeyConditionExpression": "eventID = :eventID",
        "ExpressionAttributeValues": {":eventID": event_id},
    }

    items = []
    while True:
        response = table.query(**kwargs)
        items.extend(response["Items"])
        if "LastEvaluatedKey" not in response:
            break
        kwargs["ExclusiveStartKey"] = response["LastEvaluatedKey"]
    return [item["s3Key"] for item in items]


def get_object_stream(bucket: str, key: str):
    return _s3().get_object(Bucket=bucket, Key=key)["Body"]


def create_multipart_upload(bucket: str, key: str) -> str:
    return _s3().create_multipart_upload(Bucket=bucket, Key=key)["UploadId"]


def upload_part(bucket: str, key: str, upload_id: str, part_number: int, body: bytes) -> str:
    return _s3().upload_part(
        Bucket=bucket, Key=key, UploadId=upload_id, PartNumber=part_number, Body=body
    )["ETag"]


def complete_multipart_upload(bucket: str, key: str, upload_id: str, parts: list[dict]) -> None:
    _s3().complete_multipart_upload(
        Bucket=bucket, Key=key, UploadId=upload_id, MultipartUpload={"Parts": parts}
    )


def abort_multipart_upload(bucket: str, key: str, upload_id: str) -> None:
    _s3().abort_multipart_upload(Bucket=bucket, Key=key, UploadId=upload_id)


def generate_presigned_url(bucket: str, key: str, expires_in: int = 900) -> str:
    return _s3().generate_presigned_url("get_object", Params={"Bucket": bucket, "Key": key}, ExpiresIn=expires_in)


def invoke_self_async(function_name: str, payload: dict) -> None:
    _lambda_client().invoke(
        FunctionName=function_name,
        InvocationType="Event",
        Payload=json.dumps(payload).encode("utf-8"),
    )
