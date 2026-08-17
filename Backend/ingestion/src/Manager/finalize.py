def handle_finalize(payload):
    extract_failed = payload.get("extractFailedCount", 0)
    index_results = payload.get("indexResults", [])
    index_failed = sum(1 for result in index_results if result.get("status") == "FAILED")

    succeeded_count = len(index_results) - index_failed
    failed_count = extract_failed + index_failed

    if succeeded_count == 0:
        status = "FAILED"
    elif failed_count > 0:
        status = "PARTIAL"
    else:
        status = "SUCCEEDED"

    return {
        "jobId": payload["jobId"],
        "eventID": payload["eventID"],
        "status": status,
        "succeededCount": succeeded_count,
        "failedCount": failed_count,
    }
