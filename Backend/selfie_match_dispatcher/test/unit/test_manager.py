import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import Manager.manager as manager


def test_dispatches_only_admitted_events_for_current_selfie(monkeypatch):
    calls = []
    monkeypatch.setattr(manager, "get_user", lambda user_id: {"selfieVersion": "version-2"})
    monkeypatch.setattr(manager, "list_attendee_rows_for_user", lambda user_id: iter([
        {"eventID": "event-a", "status": "ATTENDEE"},
        {"eventID": "event-b", "status": "PENDING"},
        {"eventID": "event-c", "status": "ATTENDEE"},
        {"eventID": "event-d", "status": "LEFT"},
    ]))
    monkeypatch.setattr(manager, "invoke_ingestion", lambda function, payload: calls.append((function, payload)))

    result = manager.dispatch({"userID": "user-1", "selfieVersion": "version-2"})

    assert result == {"userID": "user-1", "scheduledCount": 2}
    assert [payload["eventID"] for _, payload in calls] == ["event-a", "event-c"]
    assert all(payload["selfieVersion"] == "version-2" for _, payload in calls)


def test_stale_dispatch_does_not_schedule_any_event(monkeypatch):
    monkeypatch.setattr(manager, "get_user", lambda user_id: {"selfieVersion": "version-3"})
    monkeypatch.setattr(manager, "list_attendee_rows_for_user", lambda user_id: (_ for _ in ()).throw(AssertionError("should not query")))

    assert manager.dispatch({"userID": "user-1", "selfieVersion": "version-2"}) == {
        "userID": "user-1", "scheduledCount": 0, "stale": True,
    }
