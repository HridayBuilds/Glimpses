import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import Manager.manager as manager


class _FakeStreamingBody:
    def __init__(self, data: bytes):
        self._data = data

    def iter_chunks(self, chunk_size=65536):
        yield self._data


def test_kickoff_creates_pending_row_and_invokes_self_async(monkeypatch):
    created = {}
    invoked = {}
    monkeypatch.setattr(manager, "create_download", lambda item: created.update(item))
    monkeypatch.setattr(
        manager,
        "invoke_self_async",
        lambda function_name, payload: invoked.update(function_name=function_name, payload=payload),
    )

    result = manager.kickoff(
        {"eventID": "evt_1", "requesterID": "user_1", "photoIds": ["p1", "p2"]}
    )

    download_id = result["downloadId"]
    assert created["downloadId"] == download_id
    assert created["eventID"] == "evt_1"
    assert created["requesterID"] == "user_1"
    assert created["status"] == "PENDING"
    assert invoked["payload"] == {
        "action": "build",
        "downloadId": download_id,
        "eventID": "evt_1",
        "photoIds": ["p1", "p2"],
    }


def test_status_returns_pending_without_url(monkeypatch):
    monkeypatch.setattr(manager, "get_download", lambda download_id: {"status": "PENDING"})

    result = manager.status({"downloadId": "dl_1"})

    assert result == {"status": "PENDING"}


def test_status_returns_ready_with_presigned_url(monkeypatch):
    monkeypatch.setattr(
        manager,
        "get_download",
        lambda download_id: {"status": "READY", "s3Key": "downloads/event/evt_1/dl_1.zip"},
    )
    monkeypatch.setattr(manager, "generate_presigned_url", lambda bucket, key: f"https://example/{key}")

    result = manager.status({"downloadId": "dl_1"})

    assert result == {"status": "READY", "downloadUrl": "https://example/downloads/event/evt_1/dl_1.zip"}


def test_status_raises_for_unknown_download_id(monkeypatch):
    monkeypatch.setattr(manager, "get_download", lambda download_id: None)

    try:
        manager.status({"downloadId": "missing"})
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_build_streams_photos_into_zip_and_marks_ready(monkeypatch):
    uploaded_parts = []
    status_updates = {}
    monkeypatch.setattr(manager, "list_photo_keys", lambda event_id, photo_ids: ["photos/event/evt_1/p1.jpg"])
    monkeypatch.setattr(manager, "create_multipart_upload", lambda bucket, key: "upload-1")
    monkeypatch.setattr(
        manager, "get_object_stream", lambda bucket, key: _FakeStreamingBody(b"fake-jpeg-bytes")
    )
    monkeypatch.setattr(
        manager,
        "upload_part",
        lambda bucket, key, upload_id, part_number, body: uploaded_parts.append(part_number) or "etag",
    )
    monkeypatch.setattr(manager, "complete_multipart_upload", lambda bucket, key, upload_id, parts: None)
    monkeypatch.setattr(
        manager, "update_download_status", lambda download_id, updates: status_updates.update(updates)
    )

    result = manager.build(
        {"downloadId": "dl_1", "eventID": "evt_1", "photoIds": ["p1"]}
    )

    assert result == {"downloadId": "dl_1", "status": "READY"}
    assert uploaded_parts == [1]
    assert status_updates == {"status": "READY", "s3Key": "downloads/event/evt_1/dl_1.zip"}


def test_build_marks_failed_and_aborts_multipart_on_error(monkeypatch):
    status_updates = {}
    aborted = {}
    monkeypatch.setattr(manager, "list_photo_keys", lambda event_id, photo_ids: ["photos/event/evt_1/p1.jpg"])
    monkeypatch.setattr(manager, "create_multipart_upload", lambda bucket, key: "upload-1")

    def _raise_get_object_stream(bucket, key):
        raise RuntimeError("S3 read failed")

    monkeypatch.setattr(manager, "get_object_stream", _raise_get_object_stream)
    monkeypatch.setattr(
        manager,
        "abort_multipart_upload",
        lambda bucket, key, upload_id: aborted.update(bucket=bucket, key=key, upload_id=upload_id),
    )
    monkeypatch.setattr(
        manager, "update_download_status", lambda download_id, updates: status_updates.update(updates)
    )

    try:
        manager.build({"downloadId": "dl_1", "eventID": "evt_1", "photoIds": ["p1"]})
        assert False, "expected RuntimeError"
    except RuntimeError:
        pass

    assert aborted == {"bucket": "glimpses-photos-test-bucket", "key": "downloads/event/evt_1/dl_1.zip", "upload_id": "upload-1"}
    assert status_updates == {"status": "FAILED"}
