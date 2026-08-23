from aws_lambda_powertools.event_handler import APIGatewayRestResolver

from Manager import manager

app = APIGatewayRestResolver()


@app.post("/events/<event_id>/photos/download")
def kickoff(event_id: str):
    requester_id = app.current_event.request_context.authorizer.claims["sub"]
    body = app.current_event.json_body or {}
    return manager.kickoff(
        {"eventID": event_id, "requesterID": requester_id, "photoIds": body.get("photoIds")}
    )


@app.get("/events/<event_id>/downloads/<download_id>/status")
def status(event_id: str, download_id: str):
    return manager.status({"downloadId": download_id})


# "build" is never reached through app.resolve() — it's the payload kickoff's own
# self-invoke (a raw lambda:InvokeFunction call, InvocationType=Event) sends itself,
# which never passes through API Gateway at all.
def handle_internal_action(event):
    return manager.build(event)
