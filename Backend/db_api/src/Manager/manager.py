from DAO.dao import create_drive_job, create_job, update_job_status

_DRIVE_STATUS = {
    "drive_downloading": "DOWNLOADING",
    "drive_processing": "EXTRACTING",
    "drive_failed": "FAILED",
}
_DRIVE_FIELDS = frozenset({"folderName", "totalCount", "downloadedCount", "downloadFailedCount",
                           "skippedCount", "skippedFolders", "duplicateCount", "failedCount",
                           "succeededCount", "errorMessage"})

_STATUS_BY_ACTION = {
    "mark_extracting": "EXTRACTING",
    "mark_indexing": "INDEXING",
    "mark_matching": "MATCHING",
    "mark_success": "SUCCESS",
    "mark_failed": "FAILED",
}


def handle_action(action, payload):
    if action == "create_drive":
        item = {key: payload[key] for key in ("jobId", "eventID", "uploaderID", "startedAt")}
        item.update(eventUploaderKey=f"{item['eventID']}#{item['uploaderID']}", source="GOOGLE_DRIVE",
                    status="CHECKING", succeededCount=0, failedCount=0)
        create_drive_job(item)
        return {"jobId": item["jobId"]}
    if action in _DRIVE_STATUS or action == "drive_progress":
        updates = {key: value for key, value in payload.get("updates", {}).items() if key in _DRIVE_FIELDS}
        if action in _DRIVE_STATUS:
            updates["status"] = _DRIVE_STATUS[action]
        if updates:
            update_job_status(payload["jobId"], updates)
        return {"jobId": payload["jobId"]}
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
