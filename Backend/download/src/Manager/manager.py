import os
import uuid
from datetime import datetime, timezone
from stat import S_IFREG

from stream_zip import NO_COMPRESSION_64, stream_zip

from DAO.dao import (
    abort_multipart_upload,
    complete_multipart_upload,
    create_download,
    create_multipart_upload,
    generate_presigned_url,
    get_download,
    get_object_stream,
    invoke_self_async,
    list_photo_keys,
    update_download_status,
    upload_part,
)

# S3 multipart upload's own minimum part size (the final part is exempt).
MIN_PART_SIZE = 5 * 1024 * 1024


# Synchronous: called from POST /events/{eventId}/photos/download. Writes the PENDING
# row and fires the actual zip-build off as a separate async invocation so this call can
# return well inside API Gateway's 29s limit, however long the build itself takes.
def kickoff(payload):
    download_id = str(uuid.uuid4())
    create_download(
        {
            "downloadId": download_id,
            "eventID": payload["eventID"],
            "requesterID": payload["requesterID"],
            "status": "PENDING",
            "createdAt": datetime.now(timezone.utc).isoformat(),
        }
    )
    invoke_self_async(
        os.environ["FUNCTION_NAME"],
        {
            "action": "build",
            "downloadId": download_id,
            "eventID": payload["eventID"],
            "photoIds": payload.get("photoIds"),
        },
    )
    return {"downloadId": download_id}


# Async only, self-invoked by kickoff — never called from API Gateway. Streams each
# photo from the photos bucket into a zip, uploading it to the downloads bucket as an S3
# multipart upload so the full archive is never held in memory or /tmp at once.
def build(payload):
    download_id = payload["downloadId"]
    event_id = payload["eventID"]
    bucket = os.environ["PHOTOS_BUCKET"]  # one bucket, six prefixes (T-09) — photos/ and downloads/ both live here
    zip_key = f"downloads/event/{event_id}/{download_id}.zip"

    try:
        photo_keys = list_photo_keys(event_id, payload.get("photoIds"))
        upload_id = create_multipart_upload(bucket, zip_key)
        try:
            parts = _stream_zip_to_s3(bucket, zip_key, upload_id, photo_keys)
            complete_multipart_upload(bucket, zip_key, upload_id, parts)
        except Exception:
            abort_multipart_upload(bucket, zip_key, upload_id)
            raise
        update_download_status(download_id, {"status": "READY", "s3Key": zip_key})
    except Exception:
        update_download_status(download_id, {"status": "FAILED"})
        raise
    return {"downloadId": download_id, "status": "READY"}


def _stream_zip_to_s3(bucket, zip_key, upload_id, photo_keys):
    member_files = (
        (
            key.rsplit("/", 1)[-1],
            datetime.now(timezone.utc),
            S_IFREG | 0o600,
            NO_COMPRESSION_64,  # STORED, no re-compression — photos are already JPEGs
            get_object_stream(bucket, key).iter_chunks(),
        )
        for key in photo_keys
    )

    parts = []
    buffer = b""
    part_number = 1
    for chunk in stream_zip(member_files):
        buffer += chunk
        while len(buffer) >= MIN_PART_SIZE:
            part_body, buffer = buffer[:MIN_PART_SIZE], buffer[MIN_PART_SIZE:]
            etag = upload_part(bucket, zip_key, upload_id, part_number, part_body)
            parts.append({"ETag": etag, "PartNumber": part_number})
            part_number += 1

    if buffer:  # final part — S3 allows the last part of a multipart upload to be under the minimum
        etag = upload_part(bucket, zip_key, upload_id, part_number, buffer)
        parts.append({"ETag": etag, "PartNumber": part_number})

    return parts


# Synchronous: called from GET /events/{eventId}/downloads/{downloadId}/status.
def status(payload):
    item = get_download(payload["downloadId"])
    if item is None:
        raise ValueError(f"Unknown downloadId: {payload['downloadId']}")

    result = {"status": item["status"]}
    if item["status"] == "READY":
        result["downloadUrl"] = generate_presigned_url(os.environ["PHOTOS_BUCKET"], item["s3Key"])
    return result
