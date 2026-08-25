import os

from DAO.dao import (
    create_user,
    delete_object,
    detect_face_count,
    generate_presigned_get_url,
    generate_presigned_put_url,
    get_user,
    selfie_exists,
    update_display_name,
)

REQUIRED_FACE_COUNT = 1


def _selfie_key(user_id):
    return f"selfies/user/{user_id}/selfie.jpg"


def get_profile(payload):
    user_id = payload["userID"]
    user = get_user(user_id)
    if user is None:
        create_user(user_id, payload["email"], payload["name"])
        user = get_user(user_id)

    bucket = os.environ["PHOTOS_BUCKET"]
    key = _selfie_key(user_id)
    result = {"userID": user["userID"], "displayName": user["displayName"], "email": user["email"]}
    if selfie_exists(bucket, key):
        result["selfieUrl"] = generate_presigned_get_url(bucket, key)
    return result


def update_profile(payload):
    user_id = payload["userID"]
    update_display_name(user_id, payload["displayName"])
    return {"userID": user_id}


def mint_selfie_upload_url(payload):
    bucket = os.environ["PHOTOS_BUCKET"]
    key = _selfie_key(payload["userID"])
    return {"uploadUrl": generate_presigned_put_url(bucket, key)}


def confirm_selfie(payload):
    bucket = os.environ["PHOTOS_BUCKET"]
    key = _selfie_key(payload["userID"])
    face_count = detect_face_count(bucket, key)
    if face_count != REQUIRED_FACE_COUNT:
        delete_object(bucket, key)
        raise ValueError(f"Selfie must contain exactly one face, found {face_count}")
    return {"confirmed": True}


def delete_selfie(payload):
    bucket = os.environ["PHOTOS_BUCKET"]
    key = _selfie_key(payload["userID"])
    delete_object(bucket, key)
    return {"deleted": True}
