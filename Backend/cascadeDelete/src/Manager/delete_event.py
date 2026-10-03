import os

from DAO.dao import (
    batch_delete_attendees,
    batch_delete_faces,
    batch_delete_photos,
    delete_collection,
    delete_event_row,
    delete_s3_objects,
    get_event,
    query_attendees_by_event,
    query_faces_by_event,
    query_photos_by_event,
)


def delete_event_cascade(event_id, deleted_event=None):
    # DynamoDB TTL removes the Events row before delivering its OLD_IMAGE stream
    # record. Manual deletion still reads the live row and removes it last.
    event = deleted_event if deleted_event is not None else get_event(event_id)
    if event is None:
        return {"eventID": event_id, "deleted": False}

    delete_collection(event["rekognitionCollectionID"])

    faces = query_faces_by_event(event_id)
    if faces:
        batch_delete_faces([face["rekognitionFaceID"] for face in faces])

    photos = query_photos_by_event(event_id)
    s3_keys = [key for photo in photos for key in (photo["s3Key"], photo["thumbnailKey"])]
    delete_s3_objects(os.environ["PHOTOS_BUCKET"], s3_keys)
    if photos:
        batch_delete_photos([photo["photoID"] for photo in photos])

    attendees = query_attendees_by_event(event_id)
    if attendees:
        batch_delete_attendees(event_id, [attendee["userID"] for attendee in attendees])

    if deleted_event is None:
        delete_event_row(event_id)
    return {"eventID": event_id, "deleted": True}
