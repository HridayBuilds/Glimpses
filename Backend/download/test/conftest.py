import os

os.environ.setdefault("AWS_DEFAULT_REGION", "ap-south-1")
os.environ.setdefault("DOWNLOADS_TABLE_NAME", "glimpses-downloads-test")
os.environ.setdefault("PHOTOS_TABLE_NAME", "glimpses-photos-test")
os.environ.setdefault("PHOTOS_BUCKET", "glimpses-photos-test-bucket")
os.environ.setdefault("FUNCTION_NAME", "download")
