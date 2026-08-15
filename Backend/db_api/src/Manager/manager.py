from DAO.dao import create_job, update_job_status


def handle_action(action, payload):
    if action == "create":
        return _create(payload)
    if action == "update_status":
        return _update_status(payload)
    raise ValueError(f"Unknown action: {action}")


def _create(payload):
    item = {
        "jobId": payload["jobId"],
        "eventID": payload["eventID"],
        "uploaderID": payload["uploaderID"],
        "status": payload["status"],
        "startedAt": payload["startedAt"],
        "eventUploaderKey": f"{payload['eventID']}#{payload['uploaderID']}",
        "succeededCount": 0,
        "failedCount": 0,
    }
    create_job(item)
    return {"jobId": item["jobId"]}


def _update_status(payload):
    updates = {"status": payload["status"]}
    if "succeededCount" in payload:
        updates["succeededCount"] = payload["succeededCount"]
    if "failedCount" in payload:
        updates["failedCount"] = payload["failedCount"]
    update_job_status(payload["jobId"], updates)
    return {"jobId": payload["jobId"]}
