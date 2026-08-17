from Manager.manager import handle_step
from Manager.match_one_attendee import handle_stream_records


def handle(event):
    if "Records" in event:
        return handle_stream_records(event["Records"])
    return handle_step(event["step"], event)
