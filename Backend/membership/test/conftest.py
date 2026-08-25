import os

os.environ.setdefault("AWS_DEFAULT_REGION", "ap-south-1")
os.environ.setdefault("EVENT_ATTENDEES_TABLE_NAME", "glimpses-event-attendees-test")
os.environ.setdefault("EVENTS_TABLE_NAME", "glimpses-events-test")
os.environ.setdefault("USERS_TABLE_NAME", "glimpses-users-test")
os.environ.setdefault("CLOUDFRONT_DOMAIN", "d123456.cloudfront.net")
