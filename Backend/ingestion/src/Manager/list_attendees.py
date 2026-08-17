from DAO.dao import list_admitted_attendees


def handle_list_attendees(payload):
    event_id = payload["eventID"]
    return {"eventID": event_id, "attendeeIDs": list_admitted_attendees(event_id)}
