import os

os.environ.setdefault("AWS_DEFAULT_REGION", "ap-south-1")
os.environ.setdefault("USERS_TABLE_NAME", "glimpses-users-test")
os.environ.setdefault("PHOTOS_BUCKET", "glimpses-photos-test-bucket")
os.environ.setdefault("SELFIE_MATCH_DISPATCHER_FUNCTION_NAME", "glimpses-selfie-match-dispatcher-test")
