from Manager.delete_event import delete_event_cascade


# P-77: the Events TTL Stream trigger. Terraform's event_source_mapping filter already
# narrows this to genuine TTL expirations (userIdentity.principalId ==
# dynamodb.amazonaws.com) — CascadeDelete's own application deletes never carry that
# field, so this can't re-trigger itself in a loop. Stream view is OLD_IMAGE only
# (T-04's Events table), which is all a REMOVE record needs.
def handle_stream_records(records):
    return [delete_event_cascade(record["dynamodb"]["OldImage"]["eventID"]["S"]) for record in records]
