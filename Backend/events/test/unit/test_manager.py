import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import Manager.manager as manager


def _event(**overrides):
    base = {
        "eventID": "evt_1",
        "organizerID": "user_1",
        "name": "Priya's Trip",
        "status": "ACTIVE",
        "joinPolicy": "OPEN",
        "contributionPolicy": "ATTENDEES_CAN_ADD",
        "accessCode": "AB23CD",
        "rekognitionCollectionID": "glimpses-event-evt_1",
        "createdAt": "2026-08-01T00:00:00+00:00",
        "lastUploadAt": "2026-08-01T00:00:00+00:00",
        "photoCount": 0,
        "storageBytes": 0,
    }
    base.update(overrides)
    return base


def test_create_event_creates_collection_generates_code_and_stores_qrcode(monkeypatch):
    created_collections = []
    stored_objects = {}
    put_items = []

    monkeypatch.setattr(manager, "create_collection", lambda collection_id: created_collections.append(collection_id))
    monkeypatch.setattr(manager, "access_code_exists", lambda code: False)
    monkeypatch.setattr(manager, "put_event", lambda item: put_items.append(item))
    monkeypatch.setattr(
        manager,
        "put_object",
        lambda bucket, key, body, content_type=None, content_disposition=None: stored_objects.update({key: body}),
    )

    result = manager.create_event({"organizerID": "user_1", "name": "Priya's Trip", "description": ""})

    assert result["name"] == "Priya's Trip"
    assert result["status"] == "ACTIVE"
    assert result["joinPolicy"] == manager.DEFAULT_JOIN_POLICY
    assert result["contributionPolicy"] == manager.DEFAULT_CONTRIBUTION_POLICY
    assert len(created_collections) == 1
    assert len(put_items) == 1
    assert put_items[0]["lastUploadAt"] == put_items[0]["createdAt"]
    assert any(key.endswith("qrcode.png") for key in stored_objects)


def test_create_event_requires_name():
    try:
        manager.create_event({"organizerID": "user_1", "name": ""})
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_list_events_returns_public_shape(monkeypatch):
    monkeypatch.setattr(manager, "list_events_for_organizer", lambda organizer_id: [_event()])

    result = manager.list_events({"organizerID": "user_1"})

    assert result == [manager._public_event(_event())]


def test_list_my_events_returns_only_pending_and_attendee_rows(monkeypatch):
    monkeypatch.setattr(
        manager,
        "list_attendee_rows_for_user",
        lambda user_id: [
            {"eventID": "evt_1", "status": "ATTENDEE"},
            {"eventID": "evt_2", "status": "PENDING"},
            {"eventID": "evt_3", "status": "LEFT"},
            {"eventID": "evt_4", "status": "BLOCKED"},
        ],
    )
    monkeypatch.setattr(
        manager,
        "batch_get_events",
        lambda event_ids: [_event(eventID="evt_1"), _event(eventID="evt_2")],
    )

    result = manager.list_my_events({"userID": "user_1"})

    assert {event["eventID"]: event["attendeeStatus"] for event in result} == {
        "evt_1": "ATTENDEE",
        "evt_2": "PENDING",
    }


def test_get_event_detail_raises_for_non_owner(monkeypatch):
    monkeypatch.setattr(manager, "get_event", lambda event_id: _event(organizerID="someone_else"))

    try:
        manager.get_event_detail({"eventID": "evt_1", "organizerID": "user_1"})
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_update_event_detail_updates_only_editable_fields(monkeypatch):
    monkeypatch.setattr(manager, "get_event", lambda event_id: _event())
    updated = {}
    monkeypatch.setattr(manager, "update_event", lambda event_id, fields: updated.update(fields))

    manager.update_event_detail(
        {
            "eventID": "evt_1",
            "organizerID": "user_1",
            "name": "New Name",
            "description": None,
            "joinPolicy": None,
            "contributionPolicy": None,
        }
    )

    assert updated == {"name": "New Name"}


def test_update_event_detail_rejects_non_active_event(monkeypatch):
    monkeypatch.setattr(manager, "get_event", lambda event_id: _event(status="ARCHIVED"))

    try:
        manager.update_event_detail({"eventID": "evt_1", "organizerID": "user_1", "name": "New Name"})
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_delete_event_invokes_cascade_delete(monkeypatch):
    monkeypatch.setattr(manager, "get_event", lambda event_id: _event())
    invoked = []
    monkeypatch.setattr(manager, "invoke_cascade_delete", lambda event_id: invoked.append(event_id))

    result = manager.delete_event({"eventID": "evt_1", "organizerID": "user_1"})

    assert result == {"deleted": True}
    assert invoked == ["evt_1"]


def test_archive_event_deletes_collection_and_marks_archived(monkeypatch):
    monkeypatch.setattr(manager, "get_event", lambda event_id: _event())
    deleted_collections = []
    updated = {}
    monkeypatch.setattr(manager, "delete_collection", lambda collection_id: deleted_collections.append(collection_id))
    monkeypatch.setattr(manager, "update_event", lambda event_id, fields: updated.update(fields))

    result = manager.archive_event({"eventID": "evt_1", "organizerID": "user_1"})

    assert result == {"archived": True}
    assert deleted_collections == ["glimpses-event-evt_1"]
    assert updated["status"] == "ARCHIVED"
    assert "deleteAt" in updated


def test_archive_event_is_a_no_op_when_already_archived(monkeypatch):
    monkeypatch.setattr(manager, "get_event", lambda event_id: _event(status="ARCHIVED"))
    deleted_collections = []
    monkeypatch.setattr(manager, "delete_collection", lambda collection_id: deleted_collections.append(collection_id))
    monkeypatch.setattr(manager, "update_event", lambda event_id, fields: (_ for _ in ()).throw(AssertionError))

    result = manager.archive_event({"eventID": "evt_1", "organizerID": "user_1"})

    assert result == {"archived": True}
    assert deleted_collections == []


def test_get_stats_returns_only_photo_count_and_storage(monkeypatch):
    monkeypatch.setattr(manager, "get_event", lambda event_id: _event(photoCount=12, storageBytes=4096))

    result = manager.get_stats({"eventID": "evt_1", "organizerID": "user_1"})

    assert result == {"photoCount": 12, "storageBytes": 4096}


def test_run_archive_sweep_archives_every_stale_event(monkeypatch):
    stale_events = [_event(eventID="evt_1"), _event(eventID="evt_2")]
    monkeypatch.setattr(manager, "list_stale_active_events", lambda cutoff: stale_events)
    archived = []
    monkeypatch.setattr(manager, "delete_collection", lambda collection_id: None)
    monkeypatch.setattr(manager, "update_event", lambda event_id, fields: archived.append(event_id))

    result = manager.run_archive_sweep()

    assert result == {"archivedEventIDs": ["evt_1", "evt_2"]}
    assert archived == ["evt_1", "evt_2"]
