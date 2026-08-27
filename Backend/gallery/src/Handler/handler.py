from aws_lambda_powertools.event_handler import APIGatewayRestResolver, CORSConfig

from Manager import manager

app = APIGatewayRestResolver(cors=CORSConfig(allow_origin="*"))


def _caller_id():
    return app.current_event.request_context.authorizer.claims["sub"]


@app.get("/events/<event_id>/photos")
def list_photos(event_id: str):
    mine = app.current_event.get_query_string_value("mine") == "true"
    cursor = app.current_event.get_query_string_value("cursor")
    return manager.list_photos({"eventID": event_id, "callerID": _caller_id(), "mine": mine, "cursor": cursor})


@app.get("/events/<event_id>/photos/<photo_id>")
def get_photo(event_id: str, photo_id: str):
    return manager.get_photo({"eventID": event_id, "photoID": photo_id})


@app.post("/events/<event_id>/photos/download-urls")
def get_download_urls(event_id: str):
    body = app.current_event.json_body or {}
    return manager.get_download_urls({"eventID": event_id, "photoIDs": body.get("photoIDs", [])})


@app.delete("/events/<event_id>/photos/<photo_id>")
def delete_photo(event_id: str, photo_id: str):
    return manager.delete_photo({"eventID": event_id, "photoID": photo_id, "callerID": _caller_id()})


@app.post("/events/<event_id>/photos/bulk-delete")
def bulk_delete_photos(event_id: str):
    body = app.current_event.json_body or {}
    return manager.bulk_delete_photos(
        {"eventID": event_id, "photoIDs": body.get("photoIDs", []), "callerID": _caller_id()}
    )
