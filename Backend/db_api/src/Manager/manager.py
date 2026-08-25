from DAO.dao import create_job, update_job_status

_STATUS_BY_ACTION = {
    "mark_extracting": "EXTRACTING",
    "mark_indexing": "INDEXING",
    "mark_matching": "MATCHING",
    "mark_success": "SUCCESS",
    "mark_failed": "FAILED",
}


def handle_action(action, payload):
    if action == "create":
        return _create(payload)
    if action in _STATUS_BY_ACTION:
        return _update_status(action, payload)
    raise ValueError(f"Unknown action: {action}")


def _create(payload):
    item = {
        "jobId": payload["jobId"],
        "eventID": payload["eventID"],
        "uploaderID": payload["uploaderID"],
        "status": "CREATED",
        "startedAt": payload["startedAt"],
        "eventUploaderKey": f"{payload['eventID']}#{payload['uploaderID']}",
        "succeededCount": 0,
        "failedCount": 0,
    }
    create_job(item)
    return {"jobId": item["jobId"]}


def _update_status(action, payload):
    updates = {"status": _STATUS_BY_ACTION[action]}
    if "succeededCount" in payload:
        updates["succeededCount"] = payload["succeededCount"]
    if "failedCount" in payload:
        updates["failedCount"] = payload["failedCount"]
    update_job_status(payload["jobId"], updates)
    return {"jobId": payload["jobId"]}
