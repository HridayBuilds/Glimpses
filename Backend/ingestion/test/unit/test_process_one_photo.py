import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import Manager.process_one_photo as process_one_photo

_JPEG_BYTES = b"\xff\xd8\xff\xe0" + b"\x00" * 20
_PAYLOAD = {
    "eventID": "evt_1",
    "userID": "user_1",
    "filename": "a.jpg",
    "rawKey": "uploads/event/evt_1/user/user_1/job/job_1/raw/0",
    "uploadedAt": "2026-08-28T00:00:00+00:00",
    "uploaderDisplayName": "Meera",
    "uploaderEmail": "meera@example.com",
}


def test_process_one_photo_succeeds(monkeypatch):
    stored_objects = {}
    photos = []

    monkeypatch.setattr(process_one_photo, "get_object", lambda bucket, key: _JPEG_BYTES)
    monkeypatch.setattr(process_one_photo, "put_object", lambda bucket, key, body, content_type=None: stored_objects.update({key: body}))
    monkeypatch.setattr(process_one_photo, "make_thumbnail", lambda jpeg_bytes, max_dimension=400: b"thumb-bytes")
    monkeypatch.setattr(process_one_photo, "put_photo_if_absent", lambda item: photos.append(item) or True)
    monkeypatch.setattr(process_one_photo, "increment_event_counters", lambda event_id, photo_count_delta=0, size_bytes_delta=0: None)

    result = process_one_photo.handle_process_one_photo(_PAYLOAD)

    assert result["status"] == "SUCCEEDED"
    assert result["eventID"] == "evt_1"
    assert result["s3Key"].startswith("photos/event/evt_1/")
    assert photos[0]["uploaderDisplayName"] == "Meera"
    assert photos[0]["filename"] == "a.jpg"


def test_process_one_photo_skips_duplicate_without_failing(monkeypatch):
    monkeypatch.setattr(process_one_photo, "get_object", lambda bucket, key: _JPEG_BYTES)
    monkeypatch.setattr(process_one_photo, "put_object", lambda bucket, key, body, content_type=None: None)
    monkeypatch.setattr(process_one_photo, "make_thumbnail", lambda jpeg_bytes, max_dimension=400: b"thumb-bytes")
    monkeypatch.setattr(process_one_photo, "put_photo_if_absent", lambda item: False)

    result = process_one_photo.handle_process_one_photo(_PAYLOAD)

    assert result == {"filename": "a.jpg", "status": "DUPLICATE"}


def test_process_one_photo_returns_failed_on_unrecognized_format(monkeypatch):
    monkeypatch.setattr(process_one_photo, "get_object", lambda bucket, key: b"not-an-image")

    result = process_one_photo.handle_process_one_photo(_PAYLOAD)

    assert result == {"filename": "a.jpg", "status": "FAILED"}


def test_process_one_photo_converts_heic_via_invoke(monkeypatch):
    heic_bytes = b"\x00\x00\x00\x18ftypheic" + b"\x00" * 8
    invoked = {}
    deleted = {}

    monkeypatch.setattr(process_one_photo, "get_object", lambda bucket, key: (
        heic_bytes if key == _PAYLOAD["rawKey"] else _JPEG_BYTES
    ))
    monkeypatch.setattr(process_one_photo, "put_object", lambda bucket, key, body, content_type=None: None)

    def _fake_invoke(bucket, key):
        invoked["key"] = key
        return key.replace(".heic", ".jpg")

    monkeypatch.setattr(process_one_photo, "invoke_heic_converter", _fake_invoke)
    monkeypatch.setattr(process_one_photo, "delete_object", lambda bucket, key: deleted.update({"key": key}))
    monkeypatch.setattr(process_one_photo, "make_thumbnail", lambda jpeg_bytes, max_dimension=400: b"thumb-bytes")
    monkeypatch.setattr(process_one_photo, "put_photo_if_absent", lambda item: True)
    monkeypatch.setattr(process_one_photo, "increment_event_counters", lambda event_id, photo_count_delta=0, size_bytes_delta=0: None)

    result = process_one_photo.handle_process_one_photo(dict(_PAYLOAD, filename="a.heic"))

    assert result["status"] == "SUCCEEDED"
    assert invoked["key"].endswith(".heic")
    assert deleted["key"] == invoked["key"]
