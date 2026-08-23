from DAO.dao import (
    get_attendee,
    get_event,
    get_users,
    list_attendees_by_status,
    put_attendee,
    update_attendee_status,
)

# P-10/P-26: OPEN admits straight to ATTENDEE, APPROVAL_REQUIRED parks at PENDING.
OPEN_JOIN_POLICY = "OPEN"

STATUS_PENDING = "PENDING"
STATUS_ATTENDEE = "ATTENDEE"
STATUS_LEFT = "LEFT"
STATUS_BLOCKED = "BLOCKED"

ACTIVE_EVENT_STATUS = "ACTIVE"


def _get_event_or_raise(event_id):
    event = get_event(event_id)
    if event is None:
        raise ValueError(f"Unknown eventID: {event_id}")
    return event


def _require_organizer(event_id, organizer_id):
    event = _get_event_or_raise(event_id)
    if event["organizerID"] != organizer_id:
        raise ValueError("Not this event's organizer")
    return event


# P-26/P-10: OPEN admits straight in, APPROVAL_REQUIRED parks in the lobby.
def join_event(payload):
    event = _get_event_or_raise(payload["eventID"])
    if event["status"] != ACTIVE_EVENT_STATUS:
        raise ValueError("Event is not active")

    target_status = STATUS_ATTENDEE if event["joinPolicy"] == OPEN_JOIN_POLICY else STATUS_PENDING

    existing = get_attendee(payload["userID"], payload["eventID"])
    if existing is not None:
        # P-29: eject/deny both land on BLOCKED, and that blocks rejoining with the code.
        if existing["status"] == STATUS_BLOCKED:
            raise ValueError("Blocked from this event")
        update_attendee_status(payload["userID"], payload["eventID"], target_status)
    else:
        # matchedPhotoIDs is deliberately omitted here — ingestion's ADD to it auto-creates
        # the String Set on first match, and DynamoDB rejects an empty set on PutItem.
        put_attendee({"userID": payload["userID"], "eventID": payload["eventID"], "status": target_status})

    return {"eventID": payload["eventID"], "status": target_status}


# P-46: self-service, ATTENDEE -> LEFT. Contributed photos and matchedPhotoIDs stay put.
def leave_event(payload):
    existing = get_attendee(payload["userID"], payload["eventID"])
    if existing is None or existing["status"] != STATUS_ATTENDEE:
        raise ValueError("Not an admitted attendee of this event")
    update_attendee_status(payload["userID"], payload["eventID"], STATUS_LEFT)
    return {"eventID": payload["eventID"], "status": STATUS_LEFT}


# P-82/P-83: organizer-only lobby (status=PENDING) / roster (status=ATTENDEE) screens,
# shown with display name and email — read live from Users, never snapshotted (P-84).
def list_attendees(payload):
    _require_organizer(payload["eventID"], payload["organizerID"])

    attendees = list_attendees_by_status(payload["eventID"], payload["status"])
    users_by_id = {user["userID"]: user for user in get_users([a["userID"] for a in attendees])}

    return {
        "attendees": [
            {
                "userID": attendee["userID"],
                "status": attendee["status"],
                "displayName": users_by_id.get(attendee["userID"], {}).get("displayName"),
                "email": users_by_id.get(attendee["userID"], {}).get("email"),
            }
            for attendee in attendees
        ]
    }


# P-10: PENDING -> ATTENDEE.
def admit_attendee(payload):
    _require_organizer(payload["eventID"], payload["organizerID"])
    attendee = get_attendee(payload["userID"], payload["eventID"])
    if attendee is None or attendee["status"] != STATUS_PENDING:
        raise ValueError("Not a pending request")
    update_attendee_status(payload["userID"], payload["eventID"], STATUS_ATTENDEE)
    return {"userID": payload["userID"], "status": STATUS_ATTENDEE}


# P-29: PENDING -> BLOCKED, same blocklist eject uses.
def deny_attendee(payload):
    _require_organizer(payload["eventID"], payload["organizerID"])
    attendee = get_attendee(payload["userID"], payload["eventID"])
    if attendee is None or attendee["status"] != STATUS_PENDING:
        raise ValueError("Not a pending request")
    update_attendee_status(payload["userID"], payload["eventID"], STATUS_BLOCKED)
    return {"userID": payload["userID"], "status": STATUS_BLOCKED}


# P-29: ATTENDEE -> BLOCKED, one blocklist serves eject and deny alike.
def eject_attendee(payload):
    _require_organizer(payload["eventID"], payload["organizerID"])
    attendee = get_attendee(payload["userID"], payload["eventID"])
    if attendee is None or attendee["status"] != STATUS_ATTENDEE:
        raise ValueError("Not an admitted attendee of this event")
    update_attendee_status(payload["userID"], payload["eventID"], STATUS_BLOCKED)
    return {"userID": payload["userID"], "status": STATUS_BLOCKED}
