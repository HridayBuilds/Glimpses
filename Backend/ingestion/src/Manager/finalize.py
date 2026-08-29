from Converter.map_results import count_result_items, parse_result_file, parse_result_manifest
from DAO.dao import get_object


def handle_finalize(payload):
    process_failed = payload.get("processFailedCount", 0)
    results_bucket = payload["indexResultsBucket"]

    manifest_bytes = get_object(results_bucket, payload["indexResultsManifestKey"])
    succeeded_files, failed_files = parse_result_manifest(manifest_bytes)

    outputs = []
    for file_ref in succeeded_files:
        outputs.extend(parse_result_file(get_object(results_bucket, file_ref["Key"])))
    index_task_failures = sum(count_result_items(get_object(results_bucket, file_ref["Key"])) for file_ref in failed_files)

    index_failed = sum(1 for output in outputs if output.get("status") == "FAILED")
    succeeded_count = len(outputs) - index_failed
    failed_count = process_failed + index_failed + index_task_failures

    return {
        "jobId": payload["jobId"],
        "eventID": payload["eventID"],
        "succeededCount": succeeded_count,
        "failedCount": failed_count,
    }
