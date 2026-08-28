import os

from DAO.dao import (
    batch_delete_faces,
    batch_delete_photos,
    decrement_event_counters,
    delete_faces_from_collection,
    delete_s3_objects,
    get_event,
    get_photo,
    query_faces_by_event,
)


def delete_photos_cascade(event_id, photo_ids):
    event = get_event(event_id)
    collection_id = event["rekognitionCollectionID"] if event else None

    photos = [(photo_id, get_photo(photo_id)) for photo_id in photo_ids]
    deleted_photo_ids = [photo_id for photo_id, photo in photos if photo is not None]

    faces = query_faces_by_event(event_id)
    deleted_photo_id_set = set(deleted_photo_ids)
    face_ids = [face["rekognitionFaceID"] for face in faces if face["photoID"] in deleted_photo_id_set]
    if face_ids and collection_id:
        delete_faces_from_collection(collection_id, face_ids)
    if face_ids:
        batch_delete_faces(face_ids)

    s3_keys = []
    photo_count_delta = 0
    size_bytes_delta = 0
    for photo_id, photo in photos:
        if photo is None:
            continue
        s3_keys.append(photo["s3Key"])
        s3_keys.append(photo["thumbnailKey"])
        photo_count_delta -= 1
        size_bytes_delta -= int(photo.get("sizeBytes", 0))

    if deleted_photo_ids:
        batch_delete_photos(deleted_photo_ids)
    delete_s3_objects(os.environ["PHOTOS_BUCKET"], s3_keys)
    if deleted_photo_ids:
        decrement_event_counters(event_id, photo_count_delta, size_bytes_delta)

    return {"eventID": event_id, "deletedPhotoIDs": deleted_photo_ids}
