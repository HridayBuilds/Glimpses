from aws_lambda_powertools.event_handler import APIGatewayRestResolver, CORSConfig

from Manager import manager

app = APIGatewayRestResolver(cors=CORSConfig(allow_origin="*"))


def _organizer_id():
    return app.current_event.request_context.authorizer.claims["sub"]


@app.post("/events")
def create_event():
    body = app.current_event.json_body or {}
    return manager.create_event(
        {"organizerID": _organizer_id(), "name": body.get("name"), "description": body.get("description")}
    )


@app.get("/events")
def list_events():
    return manager.list_events({"organizerID": _organizer_id()})


@app.get("/events/my-events")
def list_my_events():
    return manager.list_my_events({"userID": _organizer_id()})


@app.get("/events/<event_id>")
def get_event_detail(event_id: str):
    return manager.get_event_detail({"eventID": event_id, "organizerID": _organizer_id()})


@app.put("/events/<event_id>")
def update_event_detail(event_id: str):
    body = app.current_event.json_body or {}
    return manager.update_event_detail(
        {
            "eventID": event_id,
            "organizerID": _organizer_id(),
            "name": body.get("name"),
            "description": body.get("description"),
            "joinPolicy": body.get("joinPolicy"),
            "contributionPolicy": body.get("contributionPolicy"),
        }
    )


@app.delete("/events/<event_id>")
def delete_event(event_id: str):
    return manager.delete_event({"eventID": event_id, "organizerID": _organizer_id()})


@app.post("/events/<event_id>/archive")
def archive_event(event_id: str):
    return manager.archive_event({"eventID": event_id, "organizerID": _organizer_id()})


@app.get("/events/<event_id>/stats")
def get_stats(event_id: str):
    return manager.get_stats({"eventID": event_id, "organizerID": _organizer_id()})


@app.get("/events/<event_id>/qrcode")
def get_qrcode_url(event_id: str):
    return manager.get_qrcode_url({"eventID": event_id, "organizerID": _organizer_id()})


def handle_internal_action(event):
    if event["action"] == "run_archive_sweep":
        return manager.run_archive_sweep()
    raise ValueError(f"Unknown action: {event['action']}")
