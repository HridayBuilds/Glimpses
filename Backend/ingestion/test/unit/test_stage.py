import io
import json
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import Manager.stage as stage


def _zip_bytes(entries):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for filename, data in entries.items():
            archive.writestr(filename, data)
    return buffer.getvalue()


_JPEG_BYTES = b"\xff\xd8\xff\xe0" + b"\x00" * 20


def test_stage_copies_each_entry_raw_and_writes_manifest(monkeypatch):
    stored_objects = {}

    monkeypatch.setattr(stage, "get_object", lambda bucket, key: _zip_bytes({"a.jpg": _JPEG_BYTES, "b.jpg": _JPEG_BYTES}))
    monkeypatch.setattr(stage, "get_user", lambda user_id: {"displayName": "Meera", "email": "meera@example.com"})
    monkeypatch.setattr(stage, "put_object", lambda bucket, key, body, content_type=None: stored_objects.update({key: body}))

    result = stage.handle_stage({
        "bucket": "glimpses-photos-test-bucket",
        "key": "uploads/event/evt_1/user/user_1/job/job_1/original.zip",
    })

    assert result["eventID"] == "evt_1"
    assert result["jobId"] == "job_1"
    assert result["stagedManifestKey"] == "uploads/event/evt_1/user/user_1/job/job_1/staged-manifest.json"

    manifest = json.loads(stored_objects[result["stagedManifestKey"]])
    assert len(manifest) == 2
    assert stored_objects[manifest[0]["rawKey"]] == _JPEG_BYTES
    assert manifest[0]["filename"] == "a.jpg"
    assert manifest[0]["uploaderDisplayName"] == "Meera"
    assert manifest[0]["uploaderEmail"] == "meera@example.com"
    assert manifest[0]["eventID"] == "evt_1"
    assert manifest[0]["userID"] == "user_1"


def test_stage_does_no_format_sniffing_or_decoding(monkeypatch):
    stored_objects = {}

    monkeypatch.setattr(stage, "get_object", lambda bucket, key: _zip_bytes({"not-an-image.txt": b"whatever bytes"}))
    monkeypatch.setattr(stage, "get_user", lambda user_id: {})
    monkeypatch.setattr(stage, "put_object", lambda bucket, key, body, content_type=None: stored_objects.update({key: body}))

    result = stage.handle_stage({
        "bucket": "glimpses-photos-test-bucket",
        "key": "uploads/event/evt_1/user/user_1/job/job_1/original.zip",
    })

    manifest = json.loads(stored_objects[result["stagedManifestKey"]])
    assert len(manifest) == 1
    assert stored_objects[manifest[0]["rawKey"]] == b"whatever bytes"
