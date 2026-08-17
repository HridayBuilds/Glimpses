from Manager.match_attendees import resolve_and_store_matches


def handle_stream_records(records):
    results = []
    for record in records:
        keys = record["dynamodb"]["Keys"]
        user_id = keys["userID"]["S"]
        event_id = keys["eventID"]["S"]
        results.append(resolve_and_store_matches(event_id, user_id))
    return results
