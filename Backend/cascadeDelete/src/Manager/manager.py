from Manager.delete_event import delete_event_cascade
from Manager.delete_photos import delete_photos_cascade


def handle_action(payload):
    action = payload["action"]
    if action == "delete_event":
        return delete_event_cascade(payload["eventID"])
    if action == "delete_photos":
        return delete_photos_cascade(payload["eventID"], payload["photoIDs"])
    raise ValueError(f"Unknown action: {action}")
