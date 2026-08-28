import io
import os
import random
import uuid
from datetime import datetime, timedelta, timezone

import qrcode

from DAO.dao import (
    access_code_exists,
    batch_get_events,
    count_attendees,
    create_collection,
    delete_collection,
    get_event,
    invoke_cascade_delete,
    list_attendee_rows_for_user,
    list_events_for_organizer,
    list_stale_active_events,
    put_attendee,
    put_event,
    put_object,
    update_event,
)

ACCESS_CODE_ALPHABET = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"
ACCESS_CODE_LENGTH = 6
ACCESS_CODE_MAX_ATTEMPTS = 10

DEFAULT_JOIN_POLICY = "OPEN"
DEFAULT_CONTRIBUTION_POLICY = "ATTENDEES_CAN_ADD"
SIMILARITY_THRESHOLD = 80

ARCHIVE_AFTER_DAYS = 30
DELETE_AFTER_ARCHIVE_DAYS = 30

EDITABLE_FIELDS = ("name", "description", "joinPolicy", "contributionPolicy")
MEMBER_ATTENDEE_STATUSES = ("PENDING", "ATTENDEE")


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _generate_unique_access_code():
    for _ in range(ACCESS_CODE_MAX_ATTEMPTS):
        code = "".join(random.choices(ACCESS_CODE_ALPHABET, k=ACCESS_CODE_LENGTH))
        if not access_code_exists(code):
            return code
    raise RuntimeError("Could not generate a unique access code")


def _get_owned_event(event_id, organizer_id):
    event = get_event(event_id)
    if event is None:
        raise ValueError(f"Unknown eventID: {event_id}")
    if event["organizerID"] != organizer_id:
        raise ValueError("Not this event's organizer")
    return event


def _public_event(event):
    return {
        "eventID": event["eventID"],
        "name": event["name"],
        "description": event.get("description", ""),
        "status": event["status"],
        "joinPolicy": event["joinPolicy"],
        "contributionPolicy": event["contributionPolicy"],
        "accessCode": event["accessCode"],
        "createdAt": event["createdAt"],
    }


def _generate_and_store_qrcode(event_id, access_code):
    join_url = f"https://{os.environ['FRONTEND_DOMAIN']}/j/{access_code}"
    image = qrcode.make(join_url)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    put_object(
        os.environ["PHOTOS_BUCKET"],
        f"qrcodes/event/{event_id}/qrcode.png",
        buffer.getvalue(),
        content_type="image/png",
        content_disposition='attachment; filename="qrcode.png"',
    )


def create_event(payload):
    if not payload.get("name"):
        raise ValueError("name is required")

    event_id = str(uuid.uuid4())
    collection_id = f"glimpses-event-{event_id}"
    create_collection(collection_id)

    access_code = _generate_unique_access_code()
    created_at = _now_iso()

    item = {
        "eventID": event_id,
        "organizerID": payload["organizerID"],
        "name": payload["name"],
        "description": payload.get("description") or "",
        "status": "ACTIVE",
        "joinPolicy": DEFAULT_JOIN_POLICY,
        "contributionPolicy": DEFAULT_CONTRIBUTION_POLICY,
        "similarityThreshold": SIMILARITY_THRESHOLD,
        "accessCode": access_code,
        "rekognitionCollectionID": collection_id,
        "createdAt": created_at,
        "lastUploadAt": created_at,
        "photoCount": 0,
        "storageBytes": 0,
    }
    put_event(item)
    put_attendee({"userID": payload["organizerID"], "eventID": event_id, "status": "ATTENDEE"})
    _generate_and_store_qrcode(event_id, access_code)

    return _public_event(item)


def list_events(payload):
    events = list_events_for_organizer(payload["organizerID"])
    return [_public_event(event) for event in events]


def list_my_events(payload):
    rows = list_attendee_rows_for_user(payload["userID"])
    attendee_status_by_event_id = {
        row["eventID"]: row["status"] for row in rows if row["status"] in MEMBER_ATTENDEE_STATUSES
    }
    events = batch_get_events(list(attendee_status_by_event_id))
    return [
        {**_public_event(event), "attendeeStatus": attendee_status_by_event_id[event["eventID"]]}
        for event in events
        # Organizers get their own auto-created ATTENDEE row (see create_event) so
        # matching works; that row shouldn't make self-organized events also show
        # up in "events I joined" - "events I organize" already covers those.
        if event["organizerID"] != payload["userID"]
    ]


def get_event_detail(payload):
    event = _get_owned_event(payload["eventID"], payload["organizerID"])
    return _public_event(event)


def update_event_detail(payload):
    event = _get_owned_event(payload["eventID"], payload["organizerID"])
    if event["status"] != "ACTIVE":
        raise ValueError("Only ACTIVE events can be edited")

    fields = {name: payload[name] for name in EDITABLE_FIELDS if payload.get(name) is not None}
    update_event(payload["eventID"], fields)
    return {"eventID": payload["eventID"]}


def delete_event(payload):
    _get_owned_event(payload["eventID"], payload["organizerID"])
    invoke_cascade_delete(payload["eventID"])
    return {"deleted": True}


def _archive(event):
    if event["status"] != "ACTIVE":
        return
    delete_collection(event["rekognitionCollectionID"])
    archived_at = _now_iso()
    delete_at = int((datetime.now(timezone.utc) + timedelta(days=DELETE_AFTER_ARCHIVE_DAYS)).timestamp())
    update_event(event["eventID"], {"status": "ARCHIVED", "archivedAt": archived_at, "deleteAt": delete_at})


def archive_event(payload):
    event = _get_owned_event(payload["eventID"], payload["organizerID"])
    _archive(event)
    return {"archived": True}


def get_stats(payload):
    event = _get_owned_event(payload["eventID"], payload["organizerID"])
    return {
        "photoCount": int(event.get("photoCount", 0)),
        "storageBytes": int(event.get("storageBytes", 0)),
        "attendeeCount": count_attendees(event["eventID"], "ATTENDEE", exclude_user_id=event["organizerID"]),
    }


def get_qrcode_url(payload):
    event = _get_owned_event(payload["eventID"], payload["organizerID"])
    return {"qrcodeUrl": f"https://{os.environ['CLOUDFRONT_DOMAIN']}/qrcodes/event/{event['eventID']}/qrcode.png"}


def run_archive_sweep():
    cutoff = (datetime.now(timezone.utc) - timedelta(days=ARCHIVE_AFTER_DAYS)).isoformat()
    archived_event_ids = []
    for event in list_stale_active_events(cutoff):
        _archive(event)
        archived_event_ids.append(event["eventID"])
    return {"archivedEventIDs": archived_event_ids}
