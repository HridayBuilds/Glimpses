import os

from DAO.dao import get_user, invoke_ingestion, list_attendee_rows_for_user


def dispatch(payload):
    user_id = payload["userID"]
    version = payload["selfieVersion"]
    user = get_user(user_id)
    if not user or user.get("selfieVersion") != version:
        return {"userID": user_id, "scheduledCount": 0, "stale": True}

    scheduled = 0
    for attendee in list_attendee_rows_for_user(user_id):
        if attendee["status"] != "ATTENDEE":
            continue
        invoke_ingestion(
            os.environ["INGESTION_FUNCTION_NAME"],
            {"step": "match_attendees", "eventID": attendee["eventID"], "userID": user_id, "selfieVersion": version},
        )
        scheduled += 1
    return {"userID": user_id, "scheduledCount": scheduled}
