import os

os.environ.setdefault("AWS_DEFAULT_REGION", "ap-south-1")
os.environ.setdefault("USERS_TABLE_NAME", "glimpses-users-test")
os.environ.setdefault("EVENTS_TABLE_NAME", "glimpses-events-test")
os.environ.setdefault("EVENT_ATTENDEES_TABLE_NAME", "glimpses-event-attendees-test")
os.environ.setdefault("NOTIFICATIONS_TABLE_NAME", "glimpses-notifications-test")
os.environ.setdefault("SES_SENDER_EMAIL", "sender@example.com")
os.environ.setdefault("FRONTEND_URL", "https://app.example.com")
