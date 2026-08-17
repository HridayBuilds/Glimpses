import json
import os
import uuid
from datetime import datetime, timezone

from Converter.dedup import compute_content_hash
from Converter.format_sniffer import sniff_format
from Converter.thumbnail import make_thumbnail, normalize_to_jpeg
from Converter.zip_extractor import extract_entries
from DAO.dao import (
    delete_object,
    get_object,
    get_user,
    increment_event_counters,
    invoke_heic_converter,
    is_duplicate,
    put_object,
    put_photo,
)


def handle_extract(payload):
    bucket = payload["bucket"]
    key = payload["key"]
    event_id, user_id, job_id = _parse_upload_key(key)

    zip_bytes = get_object(bucket, key)
    uploader = get_user(user_id) or {}
    uploader_display_name = uploader.get("displayName")
    uploader_email = uploader.get("email")
    uploaded_at = datetime.now(timezone.utc).isoformat()

    succeeded = []
    failed_count = 0

    for filename, entry_bytes in extract_entries(zip_bytes):
        try:
            photo = _extract_one(
                event_id, user_id, filename, entry_bytes, uploaded_at,
                uploader_display_name, uploader_email,
            )
        except Exception:
            failed_count += 1
            continue
        if photo is not None:  # None means a duplicate — deliberately not counted as success or failure (P-38)
            succeeded.append(photo)

    # T-02: the Distributed Map reads this list via an S3 ItemReader, never as a JSON
    # array passed between states — at up to 1,000 photos/event (P-93) that array
    # could approach Step Functions' 256KB state-transfer limit.
    manifest_key = f"uploads/event/{event_id}/user/{user_id}/job/{job_id}/manifest.json"
    put_object(bucket, manifest_key, json.dumps(succeeded).encode("utf-8"), content_type="application/json")

    return {
        "eventID": event_id,
        "jobId": job_id,
        "manifestBucket": bucket,
        "manifestKey": manifest_key,
        "extractFailedCount": failed_count,
    }


def _parse_upload_key(key):
    # uploads/event/{eventID}/user/{userId}/job/{jobId}/original.zip (T-09)
    parts = key.split("/")
    return parts[2], parts[4], parts[6]


def _extract_one(event_id, user_id, filename, entry_bytes, uploaded_at, uploader_display_name, uploader_email):
    fmt = sniff_format(entry_bytes)
    if fmt is None:
        raise ValueError(f"Unrecognized image format: {filename}")

    content_hash = compute_content_hash(entry_bytes)
    if is_duplicate(event_id, content_hash):
        return None

    photo_id = str(uuid.uuid4())
    photos_bucket = os.environ["PHOTOS_BUCKET"]
    photo_key = f"photos/event/{event_id}/{photo_id}.jpg"

    if fmt == "heic":
        staging_key = f"photos/event/{event_id}/{photo_id}.heic"
        put_object(photos_bucket, staging_key, entry_bytes)
        converted_key = invoke_heic_converter(photos_bucket, staging_key)
        jpeg_bytes = get_object(photos_bucket, converted_key)
        delete_object(photos_bucket, staging_key)  # P-35: original HEIC discarded after conversion
    else:
        jpeg_bytes = entry_bytes if fmt == "jpeg" else normalize_to_jpeg(entry_bytes)
        put_object(photos_bucket, photo_key, jpeg_bytes, content_type="image/jpeg")

    thumbnail_key = f"thumbnails/event/{event_id}/{photo_id}.jpg"
    put_object(photos_bucket, thumbnail_key, make_thumbnail(jpeg_bytes), content_type="image/jpeg")

    put_photo({
        "photoID": photo_id,
        "eventID": event_id,
        "uploaderID": user_id,
        "uploaderDisplayName": uploader_display_name,
        "uploaderEmail": uploader_email,
        "uploadedAtFilename": f"{uploaded_at}#{filename}",
        "uploadedAt": uploaded_at,
        "filename": filename,
        "contentHash": content_hash,
        "sizeBytes": len(jpeg_bytes),
        "s3Key": photo_key,
        "thumbnailKey": thumbnail_key,
    })
    increment_event_counters(event_id, photo_count_delta=1, size_bytes_delta=len(jpeg_bytes))
    return {"photoID": photo_id, "eventID": event_id, "s3Key": photo_key}
