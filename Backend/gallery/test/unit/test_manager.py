import base64
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import Manager.manager as manager


def _photo(**overrides):
    base = {
        "photoID": "p1",
        "eventID": "evt_1",
        "uploaderID": "user_1",
        "uploaderDisplayName": "Arjun",
        "uploaderEmail": "arjun@example.com",
        "filename": "img.jpg",
        "uploadedAt": "2026-08-15T10:00:00Z",
        "uploadedAtFilename": "2026-08-15T10:00:00Z#img.jpg",
        "sizeBytes": 1234,
        "s3Key": "photos/event/evt_1/p1.jpg",
        "thumbnailKey": "thumbnails/event/evt_1/p1.jpg",
    }
    base.update(overrides)
    return base


def _stub_signing(monkeypatch):
    monkeypatch.setattr(manager, "sign_cloudfront_url", lambda url, expires_at: f"{url}?signed=1")


def test_list_event_photos_paginates_via_cursor(monkeypatch):
    captured = {}

    def _query_photos_page(event_id, exclusive_start_key, limit):
        captured["exclusive_start_key"] = exclusive_start_key
        return [_photo()], {"eventID": "evt_1", "uploadedAtFilename": "2026-08-15T10:00:00Z#img.jpg"}

    monkeypatch.setattr(manager, "query_photos_page", _query_photos_page)
    _stub_signing(monkeypatch)

    result = manager.list_photos({"eventID": "evt_1", "callerID": "user_1", "mine": False, "cursor": None})

    assert captured["exclusive_start_key"] is None
    assert result["photos"] == [
        {
            "photoID": "p1",
            "eventID": "evt_1",
            "uploaderID": "user_1",
            "uploaderDisplayName": "Arjun",
            "uploaderEmail": "arjun@example.com",
            "filename": "img.jpg",
            "uploadedAt": "2026-08-15T10:00:00Z",
            "sizeBytes": 1234,
            "photoUrl": f"https://{os.environ['CLOUDFRONT_DOMAIN']}/photos/event/evt_1/p1.jpg?signed=1",
            "thumbnailUrl": f"https://{os.environ['CLOUDFRONT_DOMAIN']}/thumbnails/event/evt_1/p1.jpg?signed=1",
        }
    ]
    decoded_cursor = json.loads(base64.b64decode(result["cursor"]).decode())
    assert decoded_cursor == {"eventID": "evt_1", "uploadedAtFilename": "2026-08-15T10:00:00Z#img.jpg"}


def test_list_event_photos_decodes_cursor_into_exclusive_start_key(monkeypatch):
    captured = {}
    monkeypatch.setattr(
        manager,
        "query_photos_page",
        lambda event_id, exclusive_start_key, limit: captured.update(exclusive_start_key=exclusive_start_key) or ([], None),
    )
    _stub_signing(monkeypatch)
    cursor = base64.b64encode(json.dumps({"eventID": "evt_1", "uploadedAtFilename": "x"}).encode()).decode()

    result = manager.list_photos({"eventID": "evt_1", "callerID": "user_1", "mine": False, "cursor": cursor})

    assert captured["exclusive_start_key"] == {"eventID": "evt_1", "uploadedAtFilename": "x"}
    assert result == {"photos": [], "cursor": None}


def test_list_mine_photos_resolves_via_matched_photo_ids(monkeypatch):
    monkeypatch.setattr(
        manager, "get_attendee", lambda user_id, event_id: {"userID": user_id, "eventID": event_id, "matchedPhotoIDs": {"p1", "p2"}}
    )
    monkeypatch.setattr(
        manager,
        "batch_get_photos",
        lambda photo_ids: [
            _photo(photoID="p1", uploadedAt="2026-08-15T10:00:00Z", uploadedAtFilename="2026-08-15T10:00:00Z#img.jpg"),
            _photo(photoID="p2", uploadedAt="2026-08-16T10:00:00Z", uploadedAtFilename="2026-08-16T10:00:00Z#img.jpg"),
        ],
    )
    _stub_signing(monkeypatch)

    result = manager.list_photos({"eventID": "evt_1", "callerID": "user_2", "mine": True})

    assert [photo["photoID"] for photo in result["photos"]] == ["p2", "p1"]
    assert result["cursor"] is None


def test_list_mine_photos_with_no_attendee_row_returns_empty(monkeypatch):
    monkeypatch.setattr(manager, "get_attendee", lambda user_id, event_id: None)
    _stub_signing(monkeypatch)

    result = manager.list_photos({"eventID": "evt_1", "callerID": "user_2", "mine": True})

    assert result == {"photos": [], "cursor": None}


def test_get_photo_returns_public_shape(monkeypatch):
    monkeypatch.setattr(manager, "get_photo_by_id", lambda photo_id: _photo())
    _stub_signing(monkeypatch)

    result = manager.get_photo({"eventID": "evt_1", "photoID": "p1"})

    assert result["photoID"] == "p1"


def test_get_photo_raises_for_wrong_event(monkeypatch):
    monkeypatch.setattr(manager, "get_photo_by_id", lambda photo_id: _photo(eventID="evt_2"))

    try:
        manager.get_photo({"eventID": "evt_1", "photoID": "p1"})
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_get_download_urls_filters_to_own_event(monkeypatch):
    monkeypatch.setattr(
        manager,
        "batch_get_photos",
        lambda photo_ids: [_photo(photoID="p1"), _photo(photoID="p2", eventID="evt_2")],
    )
    monkeypatch.setattr(manager, "generate_presigned_url", lambda bucket, key: f"https://example/{key}")

    result = manager.get_download_urls({"eventID": "evt_1", "photoIDs": ["p1", "p2"]})

    assert result == {"downloadUrls": [{"photoID": "p1", "downloadUrl": "https://example/photos/event/evt_1/p1.jpg"}]}


def test_delete_photo_authorizes_uploader(monkeypatch):
    monkeypatch.setattr(manager, "get_photo_by_id", lambda photo_id: _photo(uploaderID="user_1"))
    events_calls = []
    monkeypatch.setattr(
        manager, "get_event", lambda event_id: events_calls.append(event_id) or {"organizerID": "someone_else", "status": "ACTIVE"}
    )
    invoked = {}
    monkeypatch.setattr(manager, "invoke_cascade_delete", lambda event_id, photo_ids: invoked.update(eventID=event_id, photoIDs=photo_ids))

    result = manager.delete_photo({"eventID": "evt_1", "photoID": "p1", "callerID": "user_1"})

    assert result == {"deleted": True}
    assert events_calls == ["evt_1"]
    assert invoked == {"eventID": "evt_1", "photoIDs": ["p1"]}


def test_delete_photo_authorizes_organizer(monkeypatch):
    monkeypatch.setattr(manager, "get_photo_by_id", lambda photo_id: _photo(uploaderID="user_1"))
    monkeypatch.setattr(manager, "get_event", lambda event_id: {"organizerID": "user_9", "status": "ACTIVE"})
    invoked = {}
    monkeypatch.setattr(manager, "invoke_cascade_delete", lambda event_id, photo_ids: invoked.update(photoIDs=photo_ids))

    result = manager.delete_photo({"eventID": "evt_1", "photoID": "p1", "callerID": "user_9"})

    assert result == {"deleted": True}
    assert invoked == {"photoIDs": ["p1"]}


def test_delete_photo_rejects_unauthorized_caller(monkeypatch):
    monkeypatch.setattr(manager, "get_photo_by_id", lambda photo_id: _photo(uploaderID="user_1"))
    monkeypatch.setattr(manager, "get_event", lambda event_id: {"organizerID": "user_9", "status": "ACTIVE"})

    try:
        manager.delete_photo({"eventID": "evt_1", "photoID": "p1", "callerID": "someone_else"})
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_delete_photo_rejects_when_event_archived(monkeypatch):
    monkeypatch.setattr(manager, "get_photo_by_id", lambda photo_id: _photo(uploaderID="user_1"))
    monkeypatch.setattr(manager, "get_event", lambda event_id: {"organizerID": "user_1", "status": "ARCHIVED"})

    try:
        manager.delete_photo({"eventID": "evt_1", "photoID": "p1", "callerID": "user_1"})
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_bulk_delete_photos_drops_unauthorized_and_reuses_single_events_lookup(monkeypatch):
    monkeypatch.setattr(
        manager,
        "batch_get_photos",
        lambda photo_ids: [
            _photo(photoID="p1", uploaderID="user_1"),
            _photo(photoID="p2", uploaderID="someone_else"),
            _photo(photoID="p3", uploaderID="someone_else"),
        ],
    )
    events_calls = []
    monkeypatch.setattr(
        manager, "get_event", lambda event_id: events_calls.append(event_id) or {"organizerID": "user_1", "status": "ACTIVE"}
    )
    invoked = {}
    monkeypatch.setattr(manager, "invoke_cascade_delete", lambda event_id, photo_ids: invoked.update(photoIDs=photo_ids))

    result = manager.bulk_delete_photos({"eventID": "evt_1", "photoIDs": ["p1", "p2", "p3"], "callerID": "user_1"})

    assert result == {"deletedPhotoIDs": ["p1", "p2", "p3"]}
    assert invoked == {"photoIDs": ["p1", "p2", "p3"]}
    assert events_calls == ["evt_1"]


def test_bulk_delete_photos_skips_invoke_when_nothing_authorized(monkeypatch):
    monkeypatch.setattr(manager, "batch_get_photos", lambda photo_ids: [_photo(photoID="p1", uploaderID="someone_else")])
    monkeypatch.setattr(manager, "get_event", lambda event_id: {"organizerID": "someone_else", "status": "ACTIVE"})
    invoked = []
    monkeypatch.setattr(manager, "invoke_cascade_delete", lambda event_id, photo_ids: invoked.append(photo_ids))

    result = manager.bulk_delete_photos({"eventID": "evt_1", "photoIDs": ["p1"], "callerID": "user_1"})

    assert result == {"deletedPhotoIDs": []}
    assert invoked == []


def test_bulk_delete_photos_rejects_when_event_archived(monkeypatch):
    monkeypatch.setattr(manager, "get_event", lambda event_id: {"organizerID": "user_1", "status": "ARCHIVED"})

    try:
        manager.bulk_delete_photos({"eventID": "evt_1", "photoIDs": ["p1"], "callerID": "user_1"})
        assert False, "expected ValueError"
    except ValueError:
        pass
