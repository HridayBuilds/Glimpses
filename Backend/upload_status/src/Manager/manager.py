import uuid

from DAO.dao import generate_presigned_put_url, get_job, query_latest_job

# uploads/event/{eventID}/user/{userId}/job/{jobId}/original.zip (T-09) — the jobId
# minted here is what InitializeJob later parses back out of this same key.
UPLOAD_KEY_TEMPLATE = "uploads/event/{eventID}/user/{userID}/job/{jobId}/original.zip"


def mint_upload_url(payload):
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
    # DynamoDB returns numbers as Decimal, which the JSON encoder can't serialize —
    # cast back to int for the response body.
    return {
        "jobId": job["jobId"],
        "status": job["status"],
        "startedAt": job["startedAt"],
        "succeededCount": int(job.get("succeededCount", 0)),
        "failedCount": int(job.get("failedCount", 0)),
    }
