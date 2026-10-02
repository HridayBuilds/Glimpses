from aws_lambda_powertools import Logger

from Handler.handler import app
from Manager.manager import handle_step

logger = Logger()


@logger.inject_lambda_context(log_event=False)
def lambda_handler(event, context):
    if "httpMethod" in event:
        return app.resolve(event, context)
    return handle_step(event, context)
