from Manager.manager import handle_action
from Manager.ttl_delete import handle_stream_records


def handle(event):
    if "Records" in event:
        return handle_stream_records(event["Records"])
    return handle_action(event)
