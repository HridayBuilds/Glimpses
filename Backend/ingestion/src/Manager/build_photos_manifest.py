import json
import os

from DAO.dao import put_object


def handle_build_photos_manifest(payload):
    event_id = payload["eventID"]
    job_id = payload["jobId"]
    process_results = payload.get("processResults", [])

    succeeded = [
        {"photoID": result["photoID"], "eventID": result["eventID"], "s3Key": result["s3Key"]}
        for result in process_results
        if result.get("status") == "SUCCEEDED"
    ]
    failed_count = sum(1 for result in process_results if result.get("status") == "FAILED")

    bucket = os.environ["PHOTOS_BUCKET"]
    manifest_key = f"uploads/event/{event_id}/job/{job_id}/photos-manifest.json"
    put_object(bucket, manifest_key, json.dumps(succeeded).encode("utf-8"), content_type="application/json")

    return {
        "eventID": event_id,
        "jobId": job_id,
        "manifestBucket": bucket,
        "manifestKey": manifest_key,
        "processFailedCount": failed_count,
    }
