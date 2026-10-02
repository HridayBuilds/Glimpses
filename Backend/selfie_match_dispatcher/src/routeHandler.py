from aws_lambda_powertools import Logger

from Handler.handler import handle

logger = Logger()


@logger.inject_lambda_context(log_event=True)
def lambda_handler(event, context):
    return handle(event)
