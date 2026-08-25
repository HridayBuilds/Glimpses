from Manager.delete_event import delete_event_cascade


def handle_stream_records(records):
    return [delete_event_cascade(record["dynamodb"]["OldImage"]["eventID"]["S"]) for record in records]
