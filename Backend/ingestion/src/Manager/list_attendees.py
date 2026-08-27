import json
import os

from DAO.dao import list_admitted_attendees, put_object


def handle_list_attendees(payload):
    event_id = payload["eventID"]
    job_id = payload["jobId"]
    attendee_ids = list_admitted_attendees(event_id)

    bucket = os.environ["PHOTOS_BUCKET"]
    manifest_key = f"uploads/event/{event_id}/job/{job_id}/attendees-manifest.json"
    put_object(bucket, manifest_key, json.dumps(attendee_ids).encode("utf-8"), content_type="application/json")

    return {
        "eventID": event_id,
        "attendeesManifestBucket": bucket,
        "attendeesManifestKey": manifest_key,
    }
