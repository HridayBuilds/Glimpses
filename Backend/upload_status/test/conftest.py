import os

os.environ.setdefault("AWS_DEFAULT_REGION", "ap-south-1")
os.environ.setdefault("JOBS_TABLE_NAME", "glimpses-jobs-test")
os.environ.setdefault("PHOTOS_BUCKET", "glimpses-photos-test-bucket")
os.environ.setdefault("EVENTS_TABLE_NAME", "glimpses-events-test")
