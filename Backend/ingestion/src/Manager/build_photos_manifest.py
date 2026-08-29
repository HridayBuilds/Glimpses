import json
import os

from Converter.map_results import count_result_items, parse_result_file, parse_result_manifest
from DAO.dao import get_object, put_object


def handle_build_photos_manifest(payload):
    event_id = payload["eventID"]
    job_id = payload["jobId"]

    results_bucket = payload["processResultsBucket"]
    manifest_bytes = get_object(results_bucket, payload["processResultsManifestKey"])
    succeeded_files, failed_files = parse_result_manifest(manifest_bytes)

    outputs = []
    for file_ref in succeeded_files:
        outputs.extend(parse_result_file(get_object(results_bucket, file_ref["Key"])))
    failed_count = sum(count_result_items(get_object(results_bucket, file_ref["Key"])) for file_ref in failed_files)

    succeeded = [
        {"photoID": output["photoID"], "eventID": output["eventID"], "s3Key": output["s3Key"]}
        for output in outputs
        if output.get("status") == "SUCCEEDED"
    ]
    failed_count += sum(1 for output in outputs if output.get("status") == "FAILED")

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
