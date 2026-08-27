import json
from datetime import datetime, timezone

from DAO.dao import get_object, get_user, put_object
from Converter.zip_extractor import extract_entries


def handle_stage(payload):
    bucket = payload["bucket"]
    key = payload["key"]
    event_id, user_id, job_id = _parse_upload_key(key)

    zip_bytes = get_object(bucket, key)
    uploader = get_user(user_id) or {}
    uploader_display_name = uploader.get("displayName")
    uploader_email = uploader.get("email")
    uploaded_at = datetime.now(timezone.utc).isoformat()

    staged = []
    for index, (filename, entry_bytes) in enumerate(extract_entries(zip_bytes)):
        raw_key = f"uploads/event/{event_id}/user/{user_id}/job/{job_id}/raw/{index}"
        put_object(bucket, raw_key, entry_bytes)
        staged.append({
            "eventID": event_id,
            "userID": user_id,
            "filename": filename,
            "rawKey": raw_key,
            "uploadedAt": uploaded_at,
            "uploaderDisplayName": uploader_display_name,
            "uploaderEmail": uploader_email,
        })

    manifest_key = f"uploads/event/{event_id}/user/{user_id}/job/{job_id}/staged-manifest.json"
    put_object(bucket, manifest_key, json.dumps(staged).encode("utf-8"), content_type="application/json")

    return {
        "eventID": event_id,
        "jobId": job_id,
        "stagedManifestBucket": bucket,
        "stagedManifestKey": manifest_key,
    }


def _parse_upload_key(key):
    parts = key.split("/")
    return parts[2], parts[4], parts[6]
