from aws_lambda_powertools import Logger

from Handler.handler import app

logger = Logger()


@logger.inject_lambda_context(log_event=True)
def lambda_handler(event, context):
    return app.resolve(event, context)
