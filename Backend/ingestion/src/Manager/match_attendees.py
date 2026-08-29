import os

from DAO.dao import add_matched_photo_ids, get_event, get_faces, search_faces_by_image, selfie_exists


def handle_match_attendees(payload):
    return resolve_and_store_matches(payload["eventID"], payload["userID"])


def resolve_and_store_matches(event_id, user_id):
    bucket = os.environ["PHOTOS_BUCKET"]
    selfie_key = f"selfies/user/{user_id}/selfie.jpg"

    if not selfie_exists(bucket, selfie_key):
        return {"eventID": event_id, "userID": user_id, "matchedCount": 0}

    event = get_event(event_id)
    collection_id = event["rekognitionCollectionID"]

    threshold = float(os.environ["FACE_MATCH_SIMILARITY_THRESHOLD"])
    matches = search_faces_by_image(collection_id, bucket, selfie_key, threshold=threshold)
    face_ids = [match["Face"]["FaceId"] for match in matches]
    faces = get_faces(face_ids)
    photo_ids = {face["photoID"] for face in faces}

    add_matched_photo_ids(user_id, event_id, photo_ids)
    return {"eventID": event_id, "userID": user_id, "matchedCount": len(photo_ids)}
