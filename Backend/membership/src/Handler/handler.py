from aws_lambda_powertools.event_handler import APIGatewayRestResolver, CORSConfig

from Manager import manager

app = APIGatewayRestResolver(cors=CORSConfig(allow_origin="*"))


def _caller_id():
    return app.current_event.request_context.authorizer.claims["sub"]


@app.post("/events/join")
def join_event():
    access_code = app.current_event.json_body["accessCode"]
    return manager.join_event({"accessCode": access_code, "userID": _caller_id()})


@app.post("/events/<event_id>/leave")
def leave_event(event_id: str):
    return manager.leave_event({"eventID": event_id, "userID": _caller_id()})


@app.get("/events/<event_id>/info")
def get_event_info(event_id: str):
    return manager.get_event_info({"eventID": event_id, "callerID": _caller_id()})


@app.get("/events/<event_id>/attendees")
def list_attendees(event_id: str):
    status = app.current_event.get_query_string_value("status")
    return manager.list_attendees({"eventID": event_id, "organizerID": _caller_id(), "status": status})


@app.post("/events/<event_id>/attendees/<user_id>/admit")
def admit_attendee(event_id: str, user_id: str):
    return manager.admit_attendee({"eventID": event_id, "userID": user_id, "organizerID": _caller_id()})


@app.post("/events/<event_id>/attendees/<user_id>/deny")
def deny_attendee(event_id: str, user_id: str):
    return manager.deny_attendee({"eventID": event_id, "userID": user_id, "organizerID": _caller_id()})


@app.post("/events/<event_id>/attendees/<user_id>/eject")
def eject_attendee(event_id: str, user_id: str):
    return manager.eject_attendee({"eventID": event_id, "userID": user_id, "organizerID": _caller_id()})
