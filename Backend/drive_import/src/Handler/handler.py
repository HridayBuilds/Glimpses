from aws_lambda_powertools.event_handler import APIGatewayRestResolver, CORSConfig, Response
from aws_lambda_powertools.event_handler.exceptions import BadRequestError, ForbiddenError
import json

from Manager import manager

app = APIGatewayRestResolver(cors=CORSConfig(allow_origin="*"))


@app.post("/events/<event_id>/drive-import")
def start_import(event_id):
    try:
        body = app.current_event.json_body
        if not isinstance(body, dict):
            raise ValueError("Paste a public Google Drive folder link.")
        user_id = app.current_event.request_context.authorizer.claims["sub"]
        result = manager.start_import(event_id, user_id, body)
    except (ValueError, TypeError) as error:
        raise BadRequestError(str(error)) from None
    except PermissionError as error:
        raise ForbiddenError(str(error)) from None
    return Response(status_code=202, content_type="application/json", body=json.dumps(result))
