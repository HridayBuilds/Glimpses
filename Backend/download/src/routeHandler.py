from aws_lambda_powertools import Logger

from Handler.handler import app, handle_internal_action

logger = Logger()


@logger.inject_lambda_context(log_event=True)
def lambda_handler(event, context):
    if "action" in event:
        return handle_internal_action(event)
    return app.resolve(event, context)
