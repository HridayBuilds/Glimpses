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


# P-34: whole-event teardown — Events, Photos, Faces, and (2026-08-24 ruling)
# EventAttendees rows all go. Shared by both invocation shapes: events' delete endpoint
# (organizer-triggered) and the Events TTL Stream (automatic 60-day delete, P-77).
#
# A missing Events row is treated as a successful no-op, not an error — this is the
# double-delete race between a manual delete and the TTL sweep, or a duplicate async
# invoke, that P-56/P-100's tolerated-failure philosophy already covers elsewhere.
def delete_event_cascade(event_id):
    event = get_event(event_id)
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

    delete_event_row(event_id)
    return {"eventID": event_id, "deleted": True}
