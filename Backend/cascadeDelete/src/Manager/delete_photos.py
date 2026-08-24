import os

from DAO.dao import (
    batch_delete_faces,
    decrement_event_counters,
    delete_faces_from_collection,
    delete_photo_row,
    delete_s3_objects,
    get_event,
    get_photo,
    query_faces_by_event_and_photo,
)


# P-44/P-52: single/bulk-photo cascade. gallery already authorized the caller and picked
# the photoIDs — this only ever runs the cascade itself. EventAttendees is untouched:
# CascadeDelete does not scrub matchedPhotoIDs on photo delete (already-locked ruling —
# a stale id is filtered out for free at read time, since BatchGetItem against Photos
# simply returns nothing for a missing id).
#
# A missing Photos row is a successful no-op, not an error — same double-delete race
# delete_event_cascade tolerates.
def delete_photos_cascade(event_id, photo_ids):
    event = get_event(event_id)
    collection_id = event["rekognitionCollectionID"] if event else None

    deleted_photo_ids = []
    s3_keys = []
    photo_count_delta = 0
    size_bytes_delta = 0

    for photo_id in photo_ids:
        photo = get_photo(photo_id)
        if photo is None:
            continue

        faces = query_faces_by_event_and_photo(event_id, photo_id)
        face_ids = [face["rekognitionFaceID"] for face in faces]
        if face_ids and collection_id:
            delete_faces_from_collection(collection_id, face_ids)
        if face_ids:
            batch_delete_faces(face_ids)

        s3_keys.append(photo["s3Key"])
        s3_keys.append(photo["thumbnailKey"])
        delete_photo_row(photo_id)

        deleted_photo_ids.append(photo_id)
        photo_count_delta -= 1
        size_bytes_delta -= int(photo.get("sizeBytes", 0))

    delete_s3_objects(os.environ["PHOTOS_BUCKET"], s3_keys)
    if deleted_photo_ids:
        decrement_event_counters(event_id, photo_count_delta, size_bytes_delta)

    return {"eventID": event_id, "deletedPhotoIDs": deleted_photo_ids}
