import os
import uuid

from Converter.dedup import compute_content_hash
from Converter.format_sniffer import sniff_format
from Converter.thumbnail import make_thumbnail, normalize_to_jpeg
from DAO.dao import (
    delete_object,
    get_object,
    increment_event_counters,
    invoke_heic_converter,
    put_object,
    put_photo_if_absent,
)


def handle_process_one_photo(payload):
    event_id = payload["eventID"]
    user_id = payload["userID"]
    filename = payload["filename"]
    raw_key = payload["rawKey"]
    uploaded_at = payload["uploadedAt"]
    uploader_display_name = payload.get("uploaderDisplayName")
    uploader_email = payload.get("uploaderEmail")

    bucket = os.environ["PHOTOS_BUCKET"]
    try:
        entry_bytes = get_object(bucket, raw_key)

        fmt = sniff_format(entry_bytes)
        if fmt is None:
            raise ValueError(f"Unrecognized image format: {filename}")

        content_hash = compute_content_hash(entry_bytes)
        photo_id = str(uuid.uuid5(uuid.NAMESPACE_OID, f"{event_id}:{content_hash}"))
        photo_key = f"photos/event/{event_id}/{photo_id}.jpg"

        if fmt == "heic":
            staging_key = f"photos/event/{event_id}/{photo_id}.heic"
            put_object(bucket, staging_key, entry_bytes)
            converted_key = invoke_heic_converter(bucket, staging_key)
            jpeg_bytes = get_object(bucket, converted_key)
            delete_object(bucket, staging_key)
        else:
            jpeg_bytes = entry_bytes if fmt == "jpeg" else normalize_to_jpeg(entry_bytes)
            put_object(bucket, photo_key, jpeg_bytes, content_type="image/jpeg")

        thumbnail_key = f"thumbnails/event/{event_id}/{photo_id}.jpg"
        put_object(bucket, thumbnail_key, make_thumbnail(jpeg_bytes), content_type="image/jpeg")

        saved = put_photo_if_absent({
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
        if not saved:
            return {"filename": filename, "status": "DUPLICATE"}

        increment_event_counters(event_id, photo_count_delta=1, size_bytes_delta=len(jpeg_bytes))
        return {"filename": filename, "status": "SUCCEEDED", "photoID": photo_id, "eventID": event_id, "s3Key": photo_key}
    except Exception:
        return {"filename": filename, "status": "FAILED"}
