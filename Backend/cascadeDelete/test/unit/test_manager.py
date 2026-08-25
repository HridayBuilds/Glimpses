import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import Manager.manager as manager


def test_handle_action_dispatches_delete_event(monkeypatch):
    calls = []
    monkeypatch.setattr(manager, "delete_event_cascade", lambda event_id: calls.append(event_id) or {"deleted": True})

    result = manager.handle_action({"action": "delete_event", "eventID": "evt_1"})

    assert calls == ["evt_1"]
    assert result == {"deleted": True}


def test_handle_action_dispatches_delete_photos(monkeypatch):
    calls = []
    monkeypatch.setattr(
        manager, "delete_photos_cascade", lambda event_id, photo_ids: calls.append((event_id, photo_ids)) or {"deletedPhotoIDs": photo_ids}
    )

    result = manager.handle_action({"action": "delete_photos", "eventID": "evt_1", "photoIDs": ["p1", "p2"]})

    assert calls == [("evt_1", ["p1", "p2"])]
    assert result == {"deletedPhotoIDs": ["p1", "p2"]}


def test_handle_action_raises_for_unknown_action():
    try:
        manager.handle_action({"action": "not_a_real_action"})
        assert False, "expected ValueError"
    except ValueError:
        pass
