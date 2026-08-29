import base64
import json
import os
from datetime import datetime, timedelta, timezone

from DAO.dao import (
    batch_get_photos,
    generate_presigned_url,
    get_attendee,
    get_event,
    get_photo_by_id,
    invoke_cascade_delete,
    query_photos_page,
    sign_cloudfront_url,
)

PAGE_SIZE = 50
SIGNED_URL_EXPIRY_MINUTES = 45


def _public_photo(photo):
    cloudfront_domain = os.environ["CLOUDFRONT_DOMAIN"]
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=SIGNED_URL_EXPIRY_MINUTES)
    return {
        "photoID": photo["photoID"],
        "eventID": photo["eventID"],
        "uploaderID": photo["uploaderID"],
        "uploaderDisplayName": photo.get("uploaderDisplayName"),
        "uploaderEmail": photo.get("uploaderEmail"),
        "filename": photo["filename"],
        "uploadedAt": photo["uploadedAt"],
        "sizeBytes": int(photo.get("sizeBytes", 0)),
        "photoUrl": sign_cloudfront_url(f"https://{cloudfront_domain}/{photo['s3Key']}", expires_at),
        "thumbnailUrl": sign_cloudfront_url(f"https://{cloudfront_domain}/{photo['thumbnailKey']}", expires_at),
    }


def _get_owned_photo(event_id, photo_id):
    photo = get_photo_by_id(photo_id)
    if photo is None or photo["eventID"] != event_id:
        raise ValueError(f"Unknown photoID: {photo_id}")
    return photo


def _encode_cursor(exclusive_start_key):
    return base64.b64encode(json.dumps(exclusive_start_key).encode()).decode()


def _decode_cursor(cursor):
    return json.loads(base64.b64decode(cursor.encode()).decode())


def _list_event_photos(event_id, cursor):
    exclusive_start_key = _decode_cursor(cursor) if cursor else None
    items, last_evaluated_key = query_photos_page(event_id, exclusive_start_key, PAGE_SIZE)
    return {
        "photos": [_public_photo(item) for item in items],
        "cursor": _encode_cursor(last_evaluated_key) if last_evaluated_key else None,
    }


def _list_mine_photos(event_id, caller_id):
    attendee = get_attendee(caller_id, event_id)
    matched_ids = list(attendee["matchedPhotoIDs"]) if attendee and attendee.get("matchedPhotoIDs") else []
    photos = batch_get_photos(matched_ids)
    photos.sort(key=lambda photo: photo["uploadedAtFilename"], reverse=True)
    return {"photos": [_public_photo(photo) for photo in photos], "cursor": None}


def list_photos(payload):
    if payload.get("mine"):
        return _list_mine_photos(payload["eventID"], payload["callerID"])
    return _list_event_photos(payload["eventID"], payload.get("cursor"))


def get_photo(payload):
    photo = _get_owned_photo(payload["eventID"], payload["photoID"])
    return _public_photo(photo)


def get_download_urls(payload):
    bucket = os.environ["PHOTOS_BUCKET"]
    photos = batch_get_photos(payload["photoIDs"])
    return {
        "downloadUrls": [
            {"photoID": photo["photoID"], "downloadUrl": generate_presigned_url(bucket, photo["s3Key"])}
            for photo in photos
            if photo["eventID"] == payload["eventID"]
        ]
    }


def _get_active_event(event_id):
    event = get_event(event_id)
    if event is None:
        raise ValueError(f"Unknown eventID: {event_id}")
    if event["status"] != "ACTIVE":
        raise ValueError("Event is archived and permanently read-only")
    return event


def _is_authorized_to_delete(photo, caller_id, event):
    return photo["uploaderID"] == caller_id or event["organizerID"] == caller_id


def delete_photo(payload):
    photo = _get_owned_photo(payload["eventID"], payload["photoID"])
    event = _get_active_event(payload["eventID"])
    if not _is_authorized_to_delete(photo, payload["callerID"], event):
        raise ValueError("Not authorized to delete this photo")
    invoke_cascade_delete(payload["eventID"], [payload["photoID"]])
    return {"deleted": True}


def bulk_delete_photos(payload):
    event = _get_active_event(payload["eventID"])
    photos = batch_get_photos(payload["photoIDs"])
    authorized_ids = [
        photo["photoID"]
        for photo in photos
        if photo["eventID"] == payload["eventID"] and _is_authorized_to_delete(photo, payload["callerID"], event)
    ]
    if authorized_ids:
        invoke_cascade_delete(payload["eventID"], authorized_ids)
    return {"deletedPhotoIDs": authorized_ids}
