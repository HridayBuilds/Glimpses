import os

from DAO.dao import get_event, index_faces, put_face


def handle_index_one_photo(payload):
    event_id = payload["eventID"]
    photo_id = payload["photoID"]
    s3_key = payload["s3Key"]

    event = get_event(event_id)
    collection_id = event["rekognitionCollectionID"]
    bucket = os.environ["PHOTOS_BUCKET"]

    try:
        face_records = index_faces(collection_id, bucket, s3_key)
    except Exception:
        return {"photoID": photo_id, "status": "FAILED", "faceCount": 0}

    for record in face_records:
        put_face({
            "rekognitionFaceID": record["Face"]["FaceId"],
            "eventID": event_id,
            "photoID": photo_id,
        })
    return {"photoID": photo_id, "status": "SUCCEEDED", "faceCount": len(face_records)}
