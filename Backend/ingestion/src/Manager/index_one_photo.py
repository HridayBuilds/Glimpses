import os

from DAO.dao import get_event, index_faces, put_face


def handle_index_one_photo(payload):
    event_id = payload["eventID"]
    photo_id = payload["photoID"]
    s3_key = payload["s3Key"]

    event = get_event(event_id)
    collection_id = event["rekognitionCollectionID"]
    bucket = os.environ["PHOTOS_BUCKET"]

    # Caught here, not left to raise: a failed Task inside the Distributed Map would
    # abort that item without a countable result. Finalize reads `status` off every
    # item in indexResults to compute the batch's succeeded/failed counts (P-56).
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
