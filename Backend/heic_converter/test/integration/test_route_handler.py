import io
import sys
from pathlib import Path

import boto3
import pillow_heif
from moto import mock_aws
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from routeHandler import lambda_handler


class _FakeLambdaContext:
    function_name = "heic_converter"
    memory_limit_in_mb = 128
    invoked_function_arn = "arn:aws:lambda:ap-south-1:000000000000:function:heic_converter"
    aws_request_id = "test-request-id"


def _make_heic_bytes():
    source = Image.new("RGB", (8, 8), color=(0, 255, 0))
    heif_file = pillow_heif.from_pillow(source)
    buffer = io.BytesIO()
    heif_file.save(buffer, quality=90)
    return buffer.getvalue()


@mock_aws
def test_lambda_handler_converts_heic_and_writes_jpeg_to_s3():
    bucket = "glimpses-test-bucket"
    key = "events/evt_1/photo.heic"

    s3 = boto3.client("s3", region_name="ap-south-1")
    s3.create_bucket(
        Bucket=bucket,
        CreateBucketConfiguration={"LocationConstraint": "ap-south-1"},
    )
    s3.put_object(Bucket=bucket, Key=key, Body=_make_heic_bytes())

    result = lambda_handler({"bucket": bucket, "key": key}, _FakeLambdaContext())

    assert result == {"bucket": bucket, "key": "events/evt_1/photo.jpg"}

    stored = s3.get_object(Bucket=bucket, Key="events/evt_1/photo.jpg")
    jpeg_bytes = stored["Body"].read()
    image = Image.open(io.BytesIO(jpeg_bytes))
    assert image.format == "JPEG"
    assert image.size == (8, 8)
