from Manager.manager import convert_and_store


def handle(event):
    bucket = event["bucket"]
    key = event["key"]
    new_key = convert_and_store(bucket, key)
    return {"bucket": bucket, "key": new_key}
