from boto3.dynamodb.types import TypeDeserializer

from Manager.delete_event import delete_event_cascade


def handle_stream_records(records):
    deserializer = TypeDeserializer()
    results = []
    for record in records:
        deleted_event = {
            name: deserializer.deserialize(value)
            for name, value in record["dynamodb"]["OldImage"].items()
        }
        results.append(delete_event_cascade(deleted_event["eventID"], deleted_event=deleted_event))
    return results
