import json
import os

import boto3
from botocore.exceptions import ClientError

PART_BYTES = 8 * 1024 * 1024


def table(name):
    return boto3.resource("dynamodb").Table(os.environ[name])


def get_item(name, key):
    return table(name).get_item(Key=key, ConsistentRead=True).get("Item")


def create_job(item):
    _invoke_db({"action": "create_drive", **item})


def update_job(job_id, values):
    actions = {"DOWNLOADING": "drive_downloading", "EXTRACTING": "drive_processing", "FAILED": "drive_failed"}
    action = actions[values["status"]] if "status" in values else "drive_progress"
    _invoke_db({"action": action, "jobId": job_id, "updates": values})


def _invoke_db(payload):
    response = boto3.client("lambda").invoke(FunctionName=os.environ["DB_API_FUNCTION_NAME"],
                                            Payload=json.dumps(payload).encode())
    with response["Payload"] as body:
        body.read()
    if response.get("FunctionError"):
        raise RuntimeError("Could not update the import job.")


def start_execution(job_id, payload):
    try:
        boto3.client("stepfunctions").start_execution(
            stateMachineArn=os.environ["DRIVE_STATE_MACHINE_ARN"], name=job_id,
            input=json.dumps(payload, sort_keys=True),
        )
    except ClientError as error:
        if error.response["Error"]["Code"] != "ExecutionAlreadyExists":
            raise


def put_json(key, value):
    boto3.client("s3").put_object(Bucket=os.environ["PHOTOS_BUCKET"], Key=key,
                                Body=json.dumps(value).encode(), ContentType="application/json")


def get_json(key):
    response = boto3.client("s3").get_object(Bucket=os.environ["PHOTOS_BUCKET"], Key=key)
    with response["Body"] as body:
        return json.load(body)


def upload_chunks(key, chunks, context=None, expected_size=None, content_type="application/octet-stream"):
    client = boto3.client("s3")
    kwargs = {"Bucket": os.environ["PHOTOS_BUCKET"], "Key": key}
    upload_id = client.create_multipart_upload(**kwargs, ContentType=content_type)["UploadId"]
    parts, buffer, total = [], bytearray(), 0
    try:
        def flush(data):
            number = len(parts) + 1
            result = client.upload_part(**kwargs, UploadId=upload_id, PartNumber=number, Body=data)
            parts.append({"PartNumber": number, "ETag": result["ETag"]})

        for chunk in chunks:
            if context and context.get_remaining_time_in_millis() < 15000:
                raise TimeoutError("This download exceeded its execution time. Try importing the file separately later.")
            total += len(chunk)
            buffer.extend(chunk)
            while len(buffer) >= PART_BYTES:
                flush(bytes(buffer[:PART_BYTES]))
                del buffer[:PART_BYTES]
        if expected_size is not None and total != expected_size:
            raise IOError("The file changed or its download was incomplete. Please try again.")
        if buffer or not parts:
            flush(bytes(buffer))
        client.complete_multipart_upload(**kwargs, UploadId=upload_id, MultipartUpload={"Parts": parts})
        return total
    except Exception:
        client.abort_multipart_upload(**kwargs, UploadId=upload_id)
        raise
