import io
import json
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import Manager.extract as extract  # noqa: E402


def _zip_bytes(entries):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for filename, data in entries.items():
            archive.writestr(filename, data)
    return buffer.getvalue()


_JPEG_BYTES = b"\xff\xd8\xff\xe0" + b"\x00" * 20


def test_extract_stores_photo_and_thumbnail_for_each_entry(monkeypatch):
    stored_objects = {}
    photos = []

    monkeypatch.setattr(extract, "get_object", lambda bucket, key: _zip_bytes({"a.jpg": _JPEG_BYTES}))
    monkeypatch.setattr(extract, "get_user", lambda user_id: {"displayName": "Meera", "email": "meera@example.com"})
    monkeypatch.setattr(extract, "is_duplicate", lambda event_id, content_hash: False)
    monkeypatch.setattr(extract, "put_object", lambda bucket, key, body, content_type=None: stored_objects.update({key: body}))
    monkeypatch.setattr(extract, "make_thumbnail", lambda jpeg_bytes, max_dimension=400: b"thumb-bytes")
    monkeypatch.setattr(extract, "put_photo", lambda item: photos.append(item))
    monkeypatch.setattr(extract, "increment_event_counters", lambda event_id, photo_count_delta=0, size_bytes_delta=0: None)

    result = extract.handle_extract({
        "bucket": "glimpses-photos-test-bucket",
        "key": "uploads/event/evt_1/user/user_1/job/job_1/original.zip",
    })

    assert result["eventID"] == "evt_1"
    assert result["jobId"] == "job_1"
    assert result["extractFailedCount"] == 0
    assert result["manifestKey"] == "uploads/event/evt_1/user/user_1/job/job_1/manifest.json"
    manifest = json.loads(stored_objects[result["manifestKey"]])
    assert len(manifest) == 1
    assert manifest[0]["s3Key"].startswith("photos/event/evt_1/")
    assert photos[0]["uploaderDisplayName"] == "Meera"
    assert photos[0]["uploaderEmail"] == "meera@example.com"
    assert photos[0]["filename"] == "a.jpg"


def test_extract_skips_duplicate_without_counting_as_failure(monkeypatch):
    stored_objects = {}

    monkeypatch.setattr(extract, "get_object", lambda bucket, key: _zip_bytes({"a.jpg": _JPEG_BYTES}))
    monkeypatch.setattr(extract, "get_user", lambda user_id: {})
    monkeypatch.setattr(extract, "is_duplicate", lambda event_id, content_hash: True)
    monkeypatch.setattr(extract, "put_object", lambda bucket, key, body, content_type=None: stored_objects.update({key: body}))

    result = extract.handle_extract({
        "bucket": "glimpses-photos-test-bucket",
        "key": "uploads/event/evt_1/user/user_1/job/job_1/original.zip",
    })

    assert json.loads(stored_objects[result["manifestKey"]]) == []
    assert result["extractFailedCount"] == 0


def test_extract_counts_unrecognized_format_as_failure(monkeypatch):
    stored_objects = {}

    monkeypatch.setattr(extract, "get_object", lambda bucket, key: _zip_bytes({"a.txt": b"not-an-image"}))
    monkeypatch.setattr(extract, "get_user", lambda user_id: {})
    monkeypatch.setattr(extract, "put_object", lambda bucket, key, body, content_type=None: stored_objects.update({key: body}))

    result = extract.handle_extract({
        "bucket": "glimpses-photos-test-bucket",
        "key": "uploads/event/evt_1/user/user_1/job/job_1/original.zip",
    })

    assert json.loads(stored_objects[result["manifestKey"]]) == []
    assert result["extractFailedCount"] == 1


def test_extract_converts_heic_via_invoke(monkeypatch):
    heic_bytes = b"\x00\x00\x00\x18ftypheic" + b"\x00" * 8
    invoked = {}
    stored_objects = {}
    deleted = {}

    monkeypatch.setattr(extract, "get_object", lambda bucket, key: (
        _zip_bytes({"a.heic": heic_bytes}) if key.endswith(".zip") else _JPEG_BYTES
    ))
    monkeypatch.setattr(extract, "get_user", lambda user_id: {})
    monkeypatch.setattr(extract, "is_duplicate", lambda event_id, content_hash: False)
    monkeypatch.setattr(extract, "put_object", lambda bucket, key, body, content_type=None: stored_objects.update({key: body}))

    def _fake_invoke(bucket, key):
        invoked["bucket"] = bucket
        invoked["key"] = key
        return key.replace(".heic", ".jpg")

    monkeypatch.setattr(extract, "invoke_heic_converter", _fake_invoke)
    monkeypatch.setattr(extract, "delete_object", lambda bucket, key: deleted.update({"key": key}))
    monkeypatch.setattr(extract, "make_thumbnail", lambda jpeg_bytes, max_dimension=400: b"thumb-bytes")
    monkeypatch.setattr(extract, "put_photo", lambda item: None)
    monkeypatch.setattr(extract, "increment_event_counters", lambda event_id, photo_count_delta=0, size_bytes_delta=0: None)

    result = extract.handle_extract({
        "bucket": "glimpses-photos-test-bucket",
        "key": "uploads/event/evt_1/user/user_1/job/job_1/original.zip",
    })

    assert result["extractFailedCount"] == 0
    assert invoked["key"].endswith(".heic")
    assert deleted["key"] == invoked["key"]
