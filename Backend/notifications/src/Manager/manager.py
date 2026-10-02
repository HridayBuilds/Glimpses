import os
from datetime import datetime, timezone
from urllib.parse import quote

from boto3.dynamodb.types import TypeDeserializer

from DAO.dao import (
    claim_notification,
    get_event,
    get_user,
    list_admitted_user_ids,
    mark_sent,
    release_notification,
    send_email,
)
from Manager.templates import render_email


def _send(kind, user_id, event_id, event_name, unique_id, details=None):
    user = get_user(user_id)
    if not user or not user.get("email") or user.get("emailNotificationsEnabled", True) is False:
        return False
    base_url = os.environ["FRONTEND_URL"].rstrip("/")
    event_url = f"{base_url}/app/events/{quote(event_id, safe='')}"
    subject, html_body, text_body = render_email(
        kind, user.get("displayName"), event_name, event_url, details or {}
    )
    notification_id = f"{kind}:{event_id}:{user_id}:{unique_id}"
    if not claim_notification(notification_id):
        return False
    try:
        send_email(user["email"], subject, html_body, text_body)
    except Exception:
        release_notification(notification_id)
        raise
    mark_sent(notification_id)
    return True


def _image(record, field):
    image = record.get("dynamodb", {}).get(field) or {}
    decoder = TypeDeserializer()
    return {key: decoder.deserialize(value) for key, value in image.items()}


def _handle_attendee_record(record, old, new):
    if not new:
        return 0
    event = get_event(new["eventID"])
    if not event:
        return 0
    event_id = new["eventID"]
    user_id = new["userID"]
    old_status = old.get("status")
    new_status = new.get("status")
    sent = 0
    if new_status == "PENDING" and old_status != "PENDING":
        requester = get_user(user_id) or {}
        sent += _send("join_request", event["organizerID"], event_id, event["name"], user_id, {
            "requesterName": requester.get("displayName")
        })
    elif old_status == "PENDING" and new_status in ("ATTENDEE", "BLOCKED"):
        kind = "approved" if new_status == "ATTENDEE" else "declined"
        sent += _send(kind, user_id, event_id, event["name"], record["eventID"])

    old_photos = set(old.get("matchedPhotoIDs", []))
    new_photos = set(new.get("matchedPhotoIDs", []))
    if new_status == "ATTENDEE" and new_photos - old_photos:
        day = datetime.now(timezone.utc).date().isoformat()
        sent += _send("photos_ready", user_id, event_id, event["name"], day, {
            "photoCount": len(new_photos)
        })
    return sent


def _handle_job_record(record, old, new):
    status = new.get("status")
    if status not in ("SUCCESS", "FAILED") or old.get("status") == status:
        return 0
    event = get_event(new["eventID"])
    if not event:
        return 0
    kind = "upload_success" if status == "SUCCESS" else "upload_failed"
    return int(_send(kind, new["uploaderID"], new["eventID"], event["name"], new["jobId"], {
        "succeededCount": int(new.get("succeededCount", 0))
    }))


def _handle_event_record(record, old, new):
    if old.get("status") != "ACTIVE" or new.get("status") != "ARCHIVED":
        return 0
    event_id = new["eventID"]
    return sum(
        _send("archived", user_id, event_id, new["name"], new["archivedAt"])
        for user_id in list_admitted_user_ids(event_id)
    )


def handle_notification_event(event):
    if "Records" in event:
        sent = 0
        for record in event["Records"]:
            old, new = _image(record, "OldImage"), _image(record, "NewImage")
            if "jobId" in new:
                sent += _handle_job_record(record, old, new)
            elif "userID" in new and "eventID" in new:
                sent += _handle_attendee_record(record, old, new)
            elif "eventID" in new:
                sent += _handle_event_record(record, old, new)
        return {"sentCount": sent}
    if event.get("kind") == "deleted":
        return {"sentCount": sum(
            _send("deleted", user_id, event["eventID"], event["eventName"], event["deletedAt"])
            for user_id in event["userIDs"]
        )}
    raise ValueError("Unknown notification event")
