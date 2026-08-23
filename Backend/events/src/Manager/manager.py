import io
import os
import random
import uuid
from datetime import datetime, timedelta, timezone

import qrcode

from DAO.dao import (
    access_code_exists,
    create_collection,
    delete_collection,
    get_event,
    invoke_cascade_delete,
    list_events_for_organizer,
    list_stale_active_events,
    put_event,
    put_object,
    update_event,
)

# P-27: 6 alphanumeric characters, excluding lookalikes (0/O, 1/I/l) — roughly a
# billion combinations from a ~32-character alphabet.
ACCESS_CODE_ALPHABET = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"
ACCESS_CODE_LENGTH = 6
ACCESS_CODE_MAX_ATTEMPTS = 10

# P-26: the locked defaults — no configuration questions at event creation (P-24).
DEFAULT_JOIN_POLICY = "OPEN"
DEFAULT_CONTRIBUTION_POLICY = "ATTENDEES_CAN_ADD"
SIMILARITY_THRESHOLD = 80  # P-80: locked, exposed to nobody, a code change only

ARCHIVE_AFTER_DAYS = 30  # P-77
DELETE_AFTER_ARCHIVE_DAYS = 30  # P-77

# P-89/P-24: name/description and the two policy dials are the only editable fields,
# and only while ACTIVE. similarityThreshold is locked (P-80) and never exposed here.
EDITABLE_FIELDS = ("name", "description", "joinPolicy", "contributionPolicy")


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
    # P-30: join links/QR codes use the CloudFront default domain, not a custom one.
    join_url = f"https://{os.environ['CLOUDFRONT_DOMAIN']}/j/{access_code}"
    image = qrcode.make(join_url)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    # ContentDisposition set here, not on read — P-90's "one-click save and share" is a
    # property of the stored object, independent of how its URL is later retrieved.
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
        # Seeded to createdAt so an event that never receives a single photo still has
        # a lastUploadAt value at all (P-77/P-78) — otherwise it would never appear in
        # status-lastUploadAt-index and would never auto-archive.
        "lastUploadAt": created_at,
        "photoCount": 0,
        "storageBytes": 0,
    }
    put_event(item)
    _generate_and_store_qrcode(event_id, access_code)

    return _public_event(item)


def list_events(payload):
    events = list_events_for_organizer(payload["organizerID"])
    return [_public_event(event) for event in events]


def get_event_detail(payload):
    event = _get_owned_event(payload["eventID"], payload["organizerID"])
    return _public_event(event)


def update_event_detail(payload):
    event = _get_owned_event(payload["eventID"], payload["organizerID"])
    if event["status"] != "ACTIVE":  # P-23: ACTIVE is the only state that accepts change
        raise ValueError("Only ACTIVE events can be edited")

    fields = {name: payload[name] for name in EDITABLE_FIELDS if payload.get(name) is not None}
    update_event(payload["eventID"], fields)
    return {"eventID": payload["eventID"]}


def delete_event(payload):
    _get_owned_event(payload["eventID"], payload["organizerID"])
    invoke_cascade_delete(payload["eventID"])  # P-34: cascades photos, faces, match sets
    return {"deleted": True}


def _archive(event):
    if event["status"] != "ACTIVE":
        return
    delete_collection(event["rekognitionCollectionID"])  # P-32: collection deleted, not kept
    archived_at = _now_iso()
    delete_at = int((datetime.now(timezone.utc) + timedelta(days=DELETE_AFTER_ARCHIVE_DAYS)).timestamp())
    update_event(event["eventID"], {"status": "ARCHIVED", "archivedAt": archived_at, "deleteAt": delete_at})


def archive_event(payload):
    event = _get_owned_event(payload["eventID"], payload["organizerID"])
    _archive(event)
    return {"archived": True}


def get_stats(payload):
    # P-85 (rewritten 2026-08-23): photo count and storage only — attendee count dropped.
    event = _get_owned_event(payload["eventID"], payload["organizerID"])
    # DynamoDB returns numeric attributes as Decimal; cast to int since powertools'
    # JSON encoder otherwise stringifies Decimal to avoid float precision loss.
    return {
        "photoCount": int(event.get("photoCount", 0)),
        "storageBytes": int(event.get("storageBytes", 0)),
    }


def get_qrcode_url(payload):
    event = _get_owned_event(payload["eventID"], payload["organizerID"])
    return {"qrcodeUrl": f"https://{os.environ['CLOUDFRONT_DOMAIN']}/qrcodes/event/{event['eventID']}/qrcode.png"}


# P-77/P-78: automatic archive sweep, invoked once a day by an EventBridge Scheduler
# rule — never reached through API Gateway. Manual archive_event above shares this same
# _archive helper.
def run_archive_sweep():
    cutoff = (datetime.now(timezone.utc) - timedelta(days=ARCHIVE_AFTER_DAYS)).isoformat()
    archived_event_ids = []
    for event in list_stale_active_events(cutoff):
        _archive(event)
        archived_event_ids.append(event["eventID"])
    return {"archivedEventIDs": archived_event_ids}
