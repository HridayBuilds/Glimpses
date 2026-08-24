import os

os.environ.setdefault("AWS_DEFAULT_REGION", "ap-south-1")
os.environ.setdefault("EVENTS_TABLE_NAME", "glimpses-events-test")
os.environ.setdefault("PHOTOS_TABLE_NAME", "glimpses-photos-test")
os.environ.setdefault("FACES_TABLE_NAME", "glimpses-faces-test")
os.environ.setdefault("EVENT_ATTENDEES_TABLE_NAME", "glimpses-event-attendees-test")
os.environ.setdefault("PHOTOS_BUCKET", "glimpses-photos-test-bucket")
os.environ.setdefault("FUNCTION_NAME", "cascade-delete")
