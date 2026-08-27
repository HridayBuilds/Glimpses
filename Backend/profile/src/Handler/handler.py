from aws_lambda_powertools.event_handler import APIGatewayRestResolver, CORSConfig

from Manager import manager

app = APIGatewayRestResolver(cors=CORSConfig(allow_origin="*"))


def _user_id():
    return app.current_event.request_context.authorizer.claims["sub"]


def _claims():
    return app.current_event.request_context.authorizer.claims


@app.get("/profile")
def get_profile():
    claims = _claims()
    return manager.get_profile(
        {"userID": claims["sub"], "email": claims.get("email", ""), "name": claims.get("name", "")}
    )


@app.put("/profile")
def update_profile():
    body = app.current_event.json_body or {}
    return manager.update_profile({"userID": _user_id(), "displayName": body.get("displayName")})


@app.put("/profile/selfie")
def mint_selfie_upload_url():
    return manager.mint_selfie_upload_url({"userID": _user_id()})


@app.post("/profile/selfie/confirm")
def confirm_selfie():
    return manager.confirm_selfie({"userID": _user_id()})


@app.delete("/profile/selfie")
def delete_selfie():
    return manager.delete_selfie({"userID": _user_id()})
