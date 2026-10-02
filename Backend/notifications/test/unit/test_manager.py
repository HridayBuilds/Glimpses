import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from boto3.dynamodb.types import TypeSerializer

import Manager.manager as manager
from Manager.templates import render_email


def _record(old=None, new=None, event_id="stream-record-1"):
    serializer = TypeSerializer()
    return {
        "eventID": event_id,
        "dynamodb": {
            "OldImage": {key: serializer.serialize(value) for key, value in (old or {}).items()},
            "NewImage": {key: serializer.serialize(value) for key, value in (new or {}).items()},
        },
    }


def test_membership_and_match_notifications(monkeypatch):
    calls = []
    monkeypatch.setattr(manager, "get_event", lambda event_id: {"eventID": event_id, "name": "Spring Party", "organizerID": "owner"})
    monkeypatch.setattr(manager, "get_user", lambda user_id: {"displayName": "Meera"})
    monkeypatch.setattr(manager, "_send", lambda *args: calls.append(args) or True)
    pending = {"eventID": "e1", "userID": "u1", "status": "PENDING"}
    approved = {**pending, "status": "ATTENDEE", "matchedPhotoIDs": {"p1", "p2"}}
    declined = {**pending, "status": "BLOCKED"}
    result = manager.handle_notification_event({"Records": [
        _record(new=pending), _record(old=pending, new=approved), _record(old=pending, new=declined),
    ]})
    assert result == {"sentCount": 4}
    assert [call[0] for call in calls] == ["join_request", "approved", "photos_ready", "declined"]
    assert calls[0][1] == "owner"
    assert calls[1][1] == "u1"


def test_upload_archive_and_delete_notifications(monkeypatch):
    calls = []
    monkeypatch.setattr(manager, "get_event", lambda event_id: {"eventID": event_id, "name": "Spring Party"})
    monkeypatch.setattr(manager, "list_admitted_user_ids", lambda event_id: iter(["u1", "u2"]))
    monkeypatch.setattr(manager, "_send", lambda *args: calls.append(args) or True)
    old_job = {"jobId": "j1", "eventID": "e1", "uploaderID": "u1", "status": "MATCHING"}
    success = {**old_job, "status": "SUCCESS", "succeededCount": 3}
    failure = {**old_job, "status": "FAILED"}
    old_event = {"eventID": "e1", "name": "Spring Party", "status": "ACTIVE"}
    archived = {**old_event, "status": "ARCHIVED", "archivedAt": "2026-10-02T00:00:00Z"}
    assert manager.handle_notification_event({"Records": [
        _record(old=old_job, new=success), _record(old=old_job, new=failure),
        _record(old=old_event, new=archived),
    ]}) == {"sentCount": 4}
    assert manager.handle_notification_event({
        "kind": "deleted", "eventID": "e1", "eventName": "Spring Party",
        "deletedAt": "2026-10-02", "userIDs": ["u1", "u2"],
    }) == {"sentCount": 2}
    assert [call[0] for call in calls] == ["upload_success", "upload_failed", "archived", "archived", "deleted", "deleted"]


def test_html_and_text_are_clear_and_escape_user_content():
    kinds = ("join_request", "approved", "declined", "photos_ready", "upload_success", "upload_failed", "archived", "deleted")
    for kind in kinds:
        subject, html, plain = render_email(kind, "Meera <script>", "Event <script>", "https://example.com", {
            "requesterName": "Sam <script>", "photoCount": 4, "succeededCount": 2,
        })
        assert "<script>" not in html
        assert "&lt;script&gt;" in html
        assert "Hi Meera" in plain
        assert "—" not in subject + html + plain
