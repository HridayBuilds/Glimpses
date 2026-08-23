import os

from DAO.dao import (
    delete_object,
    detect_face_count,
    generate_presigned_get_url,
    generate_presigned_put_url,
    get_user,
    selfie_exists,
    update_display_name,
)

REQUIRED_FACE_COUNT = 1  # P-66: zero or two-plus faces is rejected, nothing guessed


def _selfie_key(user_id):
    return f"selfies/user/{user_id}/selfie.jpg"


def get_profile(payload):
    user_id = payload["userID"]
    user = get_user(user_id)
    if user is None:
        raise ValueError(f"Unknown userID: {user_id}")

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


# P-15/T-09: the browser uploads directly to S3 with this URL — Profile never sees the
# bytes, so P-66's face-count check can't happen here. See confirm_selfie below.
def mint_selfie_upload_url(payload):
    bucket = os.environ["PHOTOS_BUCKET"]
    key = _selfie_key(payload["userID"])
    return {"uploadUrl": generate_presigned_put_url(bucket, key)}


# Called by the browser once its S3 upload finishes (T-03/T-09 follow-up, 2026-08-23) —
# validates what actually landed, since mint_selfie_upload_url never saw the bytes.
def confirm_selfie(payload):
    bucket = os.environ["PHOTOS_BUCKET"]
    key = _selfie_key(payload["userID"])
    face_count = detect_face_count(bucket, key)
    if face_count != REQUIRED_FACE_COUNT:
        delete_object(bucket, key)
        raise ValueError(f"Selfie must contain exactly one face, found {face_count}")
    return {"confirmed": True}


# P-68: deletes the face reference and template, forward-looking only — match sets
# already computed on EventAttendees are left in place, untouched by this call.
def delete_selfie(payload):
    bucket = os.environ["PHOTOS_BUCKET"]
    key = _selfie_key(payload["userID"])
    delete_object(bucket, key)
    return {"deleted": True}
