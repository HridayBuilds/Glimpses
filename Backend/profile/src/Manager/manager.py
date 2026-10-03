import os
import uuid

from DAO.dao import (
    create_user,
    clear_current_selfie,
    copy_object,
    delete_object,
    detect_face_count,
    generate_presigned_get_url,
    generate_presigned_put_url,
    get_user,
    invoke_selfie_match_dispatcher,
    set_current_selfie,
    selfie_exists,
    update_display_name,
)

REQUIRED_FACE_COUNT = 1


def _selfie_key(user_id):
    return f"selfies/user/{user_id}/selfie.jpg"


def _candidate_key(user_id, upload_id):
    try:
        if str(uuid.UUID(upload_id)) != upload_id:
            raise ValueError
    except (TypeError, ValueError, AttributeError):
        raise ValueError("Invalid selfie upload ID") from None
    return f"selfies/pending/user/{user_id}/{upload_id}.jpg"


def get_profile(payload):
    user_id = payload["userID"]
    user = get_user(user_id)
    if user is None:
        create_user(user_id, payload["email"], payload["name"])
        user = get_user(user_id)

    bucket = os.environ["PHOTOS_BUCKET"]
    key = user.get("selfieKey") or _selfie_key(user_id)
    result = {
        "userID": user["userID"],
        "displayName": user["displayName"],
        "email": user["email"],
    }
    if selfie_exists(bucket, key):
        result["selfieUrl"] = generate_presigned_get_url(bucket, key)
    return result


def update_profile(payload):
    user_id = payload["userID"]
    update_display_name(user_id, payload["displayName"])
    return {"userID": user_id}


def mint_selfie_upload_url(payload):
    bucket = os.environ["PHOTOS_BUCKET"]
    upload_id = str(uuid.uuid4())
    key = _candidate_key(payload["userID"], upload_id)
    return {"uploadUrl": generate_presigned_put_url(bucket, key), "uploadId": upload_id}


def confirm_selfie(payload):
    bucket = os.environ["PHOTOS_BUCKET"]
    user_id = payload["userID"]
    upload_id = payload["uploadId"]
    candidate_key = _candidate_key(user_id, upload_id)
    face_count = detect_face_count(bucket, candidate_key)
    if face_count != REQUIRED_FACE_COUNT:
        delete_object(bucket, candidate_key)
        raise ValueError(f"Selfie must contain exactly one face, found {face_count}")
    previous = get_user(user_id) or {}
    if not previous:
        create_user(user_id, payload.get("email", ""), payload.get("name", ""))
    current_key = f"selfies/user/{user_id}/{upload_id}.jpg"
    copy_object(bucket, candidate_key, current_key)
    set_current_selfie(user_id, current_key, upload_id)
    invoke_selfie_match_dispatcher(user_id, upload_id)
    delete_object(bucket, candidate_key)
    old_key = previous.get("selfieKey") or _selfie_key(user_id)
    if old_key != current_key and selfie_exists(bucket, old_key):
        delete_object(bucket, old_key)
    return {"confirmed": True}


def delete_selfie(payload):
    bucket = os.environ["PHOTOS_BUCKET"]
    user_id = payload["userID"]
    user = get_user(user_id) or {}
    key = user.get("selfieKey") or _selfie_key(user_id)
    clear_current_selfie(user_id)
    delete_object(bucket, key)
    return {"deleted": True}
