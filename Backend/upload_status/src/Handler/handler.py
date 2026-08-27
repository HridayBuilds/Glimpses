from aws_lambda_powertools.event_handler import APIGatewayRestResolver, CORSConfig

from Manager import manager

app = APIGatewayRestResolver(cors=CORSConfig(allow_origin="*"))


def _user_id():
    return app.current_event.request_context.authorizer.claims["sub"]


@app.post("/events/<event_id>/upload-url")
def mint_upload_url(event_id: str):
    return manager.mint_upload_url({"eventID": event_id, "userID": _user_id()})


@app.get("/events/<event_id>/jobs/<job_id>/status")
def get_job_status(event_id: str, job_id: str):
    return manager.get_job_status({"eventID": event_id, "jobId": job_id, "userID": _user_id()})


@app.get("/events/<event_id>/jobs/latest")
def get_latest_job(event_id: str):
    return manager.get_latest_job({"eventID": event_id, "userID": _user_id()})
