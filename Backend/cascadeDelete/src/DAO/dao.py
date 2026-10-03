import os

import boto3


def _dynamodb():
    return boto3.resource("dynamodb")


def _events_table():
    return _dynamodb().Table(os.environ["EVENTS_TABLE_NAME"])


def _photos_table():
    return _dynamodb().Table(os.environ["PHOTOS_TABLE_NAME"])


def _faces_table():
    return _dynamodb().Table(os.environ["FACES_TABLE_NAME"])


def _event_attendees_table():
    return _dynamodb().Table(os.environ["EVENT_ATTENDEES_TABLE_NAME"])


def _s3():
    return boto3.client("s3")


def _rekognition():
    return boto3.client("rekognition")


def _query_all(table, **kwargs):
    items = []
    while True:
        response = table.query(**kwargs)
        items.extend(response["Items"])
        if "LastEvaluatedKey" not in response:
            return items
        kwargs["ExclusiveStartKey"] = response["LastEvaluatedKey"]


def get_event(event_id):
    response = _events_table().get_item(Key={"eventID": event_id})
    return response.get("Item")


def delete_event_row(event_id):
    _events_table().delete_item(Key={"eventID": event_id})


def decrement_event_counters(event_id, photo_count_delta, size_bytes_delta):
    _events_table().update_item(
        Key={"eventID": event_id},
        UpdateExpression="ADD photoCount :p, storageBytes :s",
        ExpressionAttributeValues={":p": photo_count_delta, ":s": size_bytes_delta},
    )


def delete_collection(collection_id):
    try:
        _rekognition().delete_collection(CollectionId=collection_id)
    except _rekognition().exceptions.ResourceNotFoundException:
        pass


def delete_faces_from_collection(collection_id, face_ids):
    if not face_ids:
        return
    try:
        _rekognition().delete_faces(CollectionId=collection_id, FaceIds=face_ids)
    except _rekognition().exceptions.ResourceNotFoundException:
        pass


def get_photo(photo_id):
    response = _photos_table().get_item(Key={"photoID": photo_id})
    return response.get("Item")


def delete_photo_row(photo_id):
    _photos_table().delete_item(Key={"photoID": photo_id})


def query_photos_by_event(event_id):
    return _query_all(
        _photos_table(),
        IndexName="eventID-uploadedAtFilename-index",
        KeyConditionExpression="eventID = :e",
        ExpressionAttributeValues={":e": event_id},
    )


def query_faces_by_event(event_id):
    return _query_all(
        _faces_table(),
        IndexName="eventID-photoID-index",
        KeyConditionExpression="eventID = :e",
        ExpressionAttributeValues={":e": event_id},
    )


def query_faces_by_event_and_photo(event_id, photo_id):
    response = _faces_table().query(
        IndexName="eventID-photoID-index",
        KeyConditionExpression="eventID = :e AND photoID = :p",
        ExpressionAttributeValues={":e": event_id, ":p": photo_id},
    )
    return response["Items"]


def batch_delete_faces(rekognition_face_ids):
    with _faces_table().batch_writer() as writer:
        for face_id in rekognition_face_ids:
            writer.delete_item(Key={"rekognitionFaceID": face_id})


def batch_delete_photos(photo_ids):
    with _photos_table().batch_writer() as writer:
        for photo_id in photo_ids:
            writer.delete_item(Key={"photoID": photo_id})


def query_attendees_by_event(event_id):
    return _query_all(
        _event_attendees_table(),
        IndexName="eventID-status-index",
        KeyConditionExpression="eventID = :e",
        ExpressionAttributeValues={":e": event_id},
    )


def batch_delete_attendees(event_id, user_ids):
    with _event_attendees_table().batch_writer() as writer:
        for user_id in user_ids:
            writer.delete_item(Key={"userID": user_id, "eventID": event_id})


def delete_s3_objects(bucket, keys):
    if not keys:
        return
    s3 = _s3()
    limit = 1000
    for offset in range(0, len(keys), limit):
        batch = keys[offset : offset + limit]
        s3.delete_objects(Bucket=bucket, Delete={"Objects": [{"Key": key} for key in batch]})
