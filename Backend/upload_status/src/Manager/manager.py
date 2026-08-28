import uuid

from DAO.dao import generate_presigned_put_url, get_event, get_job, query_latest_job

UPLOAD_KEY_TEMPLATE = "uploads/event/{eventID}/user/{userID}/job/{jobId}/original.zip"


def mint_upload_url(payload):
    event = get_event(payload["eventID"])
    if event is None:
        raise ValueError(f"Unknown eventID: {payload['eventID']}")
    if event["status"] != "ACTIVE":
        raise ValueError("Only ACTIVE events can accept new photos")
    is_organizer = event["organizerID"] == payload["userID"]
    if event["contributionPolicy"] == "ORGANIZER_ONLY" and not is_organizer:
        raise ValueError("Only the organizer can add photos to this event")

    job_id = str(uuid.uuid4())
    key = UPLOAD_KEY_TEMPLATE.format(eventID=payload["eventID"], userID=payload["userID"], jobId=job_id)
    return {"jobId": job_id, "uploadUrl": generate_presigned_put_url(key)}


def get_job_status(payload):
    job = get_job(payload["jobId"])
    if job is None or job["eventID"] != payload["eventID"] or job["uploaderID"] != payload["userID"]:
        raise ValueError(f"Unknown jobId: {payload['jobId']}")
    return _job_response(job)


def get_latest_job(payload):
    job = query_latest_job(payload["eventID"], payload["userID"])
    if job is None:
        raise ValueError("No jobs found")
    return _job_response(job)


def _job_response(job):
    return {
        "jobId": job["jobId"],
        "status": job["status"],
        "startedAt": job["startedAt"],
        "succeededCount": int(job.get("succeededCount", 0)),
        "failedCount": int(job.get("failedCount", 0)),
    }
