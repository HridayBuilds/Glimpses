import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import Manager.manager as manager


def _event(**overrides):
    base = {
        "eventID": "evt_1",
        "organizerID": "user_1",
        "status": "ACTIVE",
        "joinPolicy": "OPEN",
        "accessCode": "AB23CD",
    }
    base.update(overrides)
    return base


def _attendee(**overrides):
    base = {"userID": "user_2", "eventID": "evt_1", "status": "PENDING"}
    base.update(overrides)
    return base


def test_join_event_open_policy_admits_directly(monkeypatch):
    monkeypatch.setattr(manager, "get_event_by_access_code", lambda access_code: _event(joinPolicy="OPEN"))
    monkeypatch.setattr(manager, "get_attendee", lambda user_id, event_id: None)
    put_items = []
    monkeypatch.setattr(manager, "put_attendee", lambda item: put_items.append(item))

    result = manager.join_event({"accessCode": "AB23CD", "userID": "user_2"})

    assert result == {"eventID": "evt_1", "status": "ATTENDEE"}
    assert put_items == [{"userID": "user_2", "eventID": "evt_1", "status": "ATTENDEE"}]


def test_join_event_approval_required_parks_in_lobby(monkeypatch):
    monkeypatch.setattr(manager, "get_event_by_access_code", lambda access_code: _event(joinPolicy="APPROVAL_REQUIRED"))
    monkeypatch.setattr(manager, "get_attendee", lambda user_id, event_id: None)
    put_items = []
    monkeypatch.setattr(manager, "put_attendee", lambda item: put_items.append(item))

    result = manager.join_event({"accessCode": "AB23CD", "userID": "user_2"})

    assert result == {"eventID": "evt_1", "status": "PENDING"}
    assert put_items[0]["status"] == "PENDING"


def test_join_event_rejects_unknown_access_code(monkeypatch):
    monkeypatch.setattr(manager, "get_event_by_access_code", lambda access_code: None)

    try:
        manager.join_event({"accessCode": "ZZ00ZZ", "userID": "user_2"})
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_join_event_rejects_archived_event(monkeypatch):
    monkeypatch.setattr(manager, "get_event_by_access_code", lambda access_code: _event(status="ARCHIVED"))

    try:
        manager.join_event({"accessCode": "AB23CD", "userID": "user_2"})
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_join_event_rejects_blocked_user(monkeypatch):
    monkeypatch.setattr(manager, "get_event_by_access_code", lambda access_code: _event())
    monkeypatch.setattr(manager, "get_attendee", lambda user_id, event_id: _attendee(status="BLOCKED"))

    try:
        manager.join_event({"accessCode": "AB23CD", "userID": "user_2"})
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_join_event_rejects_organizer_joining_own_event(monkeypatch):
    monkeypatch.setattr(manager, "get_event_by_access_code", lambda access_code: _event(organizerID="user_1"))

    try:
        manager.join_event({"accessCode": "AB23CD", "userID": "user_1"})
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_join_event_rejoin_after_leave_uses_join_policy(monkeypatch):
    monkeypatch.setattr(manager, "get_event_by_access_code", lambda access_code: _event(joinPolicy="OPEN"))
    monkeypatch.setattr(manager, "get_attendee", lambda user_id, event_id: _attendee(status="LEFT"))
    updated = []
    monkeypatch.setattr(manager, "update_attendee_status", lambda user_id, event_id, status: updated.append(status))

    result = manager.join_event({"accessCode": "AB23CD", "userID": "user_2"})

    assert result == {"eventID": "evt_1", "status": "ATTENDEE"}
    assert updated == ["ATTENDEE"]


def test_leave_event_marks_attendee_left(monkeypatch):
    monkeypatch.setattr(manager, "get_event", lambda event_id: _event())
    monkeypatch.setattr(manager, "get_attendee", lambda user_id, event_id: _attendee(status="ATTENDEE"))
    updated = []
    monkeypatch.setattr(manager, "update_attendee_status", lambda user_id, event_id, status: updated.append(status))

    result = manager.leave_event({"eventID": "evt_1", "userID": "user_2"})

    assert result == {"eventID": "evt_1", "status": "LEFT"}
    assert updated == ["LEFT"]


def test_leave_event_rejects_organizer_leaving_own_event(monkeypatch):
    monkeypatch.setattr(manager, "get_event", lambda event_id: _event(organizerID="user_1"))

    try:
        manager.leave_event({"eventID": "evt_1", "userID": "user_1"})
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_leave_event_rejects_non_attendee(monkeypatch):
    monkeypatch.setattr(manager, "get_event", lambda event_id: _event())
    monkeypatch.setattr(manager, "get_attendee", lambda user_id, event_id: None)

    try:
        manager.leave_event({"eventID": "evt_1", "userID": "user_2"})
        assert False, "expected ValueError"
    except ValueError:
        pass


def _full_event(**overrides):
    return _event(
        name="Priya's Trip",
        description="A weekend away",
        createdAt="2026-08-01T00:00:00+00:00",
        contributionPolicy="ATTENDEES_CAN_ADD",
        accessCode="AB23CD",
        **overrides,
    )


def test_get_event_info_returns_limited_fields_for_pending(monkeypatch):
    monkeypatch.setattr(manager, "get_event", lambda event_id: _full_event())
    monkeypatch.setattr(manager, "get_attendee", lambda user_id, event_id: _attendee(status="PENDING"))

    result = manager.get_event_info({"eventID": "evt_1", "callerID": "user_2"})

    assert result == {
        "eventID": "evt_1",
        "name": "Priya's Trip",
        "description": "A weekend away",
        "createdAt": "2026-08-01T00:00:00+00:00",
    }


def test_get_event_info_returns_full_fields_for_attendee(monkeypatch):
    monkeypatch.setattr(manager, "get_event", lambda event_id: _full_event())
    monkeypatch.setattr(manager, "get_attendee", lambda user_id, event_id: _attendee(status="ATTENDEE"))

    result = manager.get_event_info({"eventID": "evt_1", "callerID": "user_2"})

    assert result["accessCode"] == "AB23CD"
    assert result["qrcodeUrl"].endswith("/qrcodes/event/evt_1/qrcode.png")
    assert result["joinPolicy"] == "OPEN"


def test_get_event_info_returns_full_fields_for_organizer(monkeypatch):
    monkeypatch.setattr(manager, "get_event", lambda event_id: _full_event())
    monkeypatch.setattr(manager, "get_attendee", lambda user_id, event_id: (_ for _ in ()).throw(AssertionError))

    result = manager.get_event_info({"eventID": "evt_1", "callerID": "user_1"})

    assert result["accessCode"] == "AB23CD"


def test_get_event_info_rejects_non_member(monkeypatch):
    monkeypatch.setattr(manager, "get_event", lambda event_id: _full_event())
    monkeypatch.setattr(manager, "get_attendee", lambda user_id, event_id: None)

    try:
        manager.get_event_info({"eventID": "evt_1", "callerID": "someone_else"})
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_get_event_info_rejects_blocked_attendee(monkeypatch):
    monkeypatch.setattr(manager, "get_event", lambda event_id: _full_event())
    monkeypatch.setattr(manager, "get_attendee", lambda user_id, event_id: _attendee(status="BLOCKED"))

    try:
        manager.get_event_info({"eventID": "evt_1", "callerID": "user_2"})
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_list_attendees_rejects_non_organizer(monkeypatch):
    monkeypatch.setattr(manager, "get_event", lambda event_id: _event(organizerID="user_1"))

    try:
        manager.list_attendees({"eventID": "evt_1", "organizerID": "someone_else", "status": "PENDING"})
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_list_attendees_joins_display_name_and_email(monkeypatch):
    monkeypatch.setattr(manager, "get_event", lambda event_id: _event())
    monkeypatch.setattr(manager, "list_attendees_by_status", lambda event_id, status: [_attendee()])
    monkeypatch.setattr(
        manager, "get_users", lambda user_ids: [{"userID": "user_2", "displayName": "Meera", "email": "meera@x.com"}]
    )

    result = manager.list_attendees({"eventID": "evt_1", "organizerID": "user_1", "status": "PENDING"})

    assert result == {
        "attendees": [{"userID": "user_2", "status": "PENDING", "displayName": "Meera", "email": "meera@x.com"}]
    }


def test_list_attendees_excludes_organizers_own_row(monkeypatch):
    monkeypatch.setattr(manager, "get_event", lambda event_id: _event(organizerID="user_1"))
    monkeypatch.setattr(
        manager,
        "list_attendees_by_status",
        lambda event_id, status: [_attendee(userID="user_1"), _attendee(userID="user_2")],
    )
    monkeypatch.setattr(
        manager, "get_users", lambda user_ids: [{"userID": "user_2", "displayName": "Meera", "email": "meera@x.com"}]
    )

    result = manager.list_attendees({"eventID": "evt_1", "organizerID": "user_1", "status": "ATTENDEE"})

    assert [a["userID"] for a in result["attendees"]] == ["user_2"]


def test_admit_attendee_transitions_pending_to_attendee(monkeypatch):
    monkeypatch.setattr(manager, "get_event", lambda event_id: _event())
    monkeypatch.setattr(manager, "get_attendee", lambda user_id, event_id: _attendee(status="PENDING"))
    updated = []
    monkeypatch.setattr(manager, "update_attendee_status", lambda user_id, event_id, status: updated.append(status))

    result = manager.admit_attendee({"eventID": "evt_1", "userID": "user_2", "organizerID": "user_1"})

    assert result == {"userID": "user_2", "status": "ATTENDEE"}
    assert updated == ["ATTENDEE"]


def test_admit_attendee_rejects_non_pending(monkeypatch):
    monkeypatch.setattr(manager, "get_event", lambda event_id: _event())
    monkeypatch.setattr(manager, "get_attendee", lambda user_id, event_id: _attendee(status="ATTENDEE"))

    try:
        manager.admit_attendee({"eventID": "evt_1", "userID": "user_2", "organizerID": "user_1"})
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_deny_attendee_transitions_pending_to_blocked(monkeypatch):
    monkeypatch.setattr(manager, "get_event", lambda event_id: _event())
    monkeypatch.setattr(manager, "get_attendee", lambda user_id, event_id: _attendee(status="PENDING"))
    updated = []
    monkeypatch.setattr(manager, "update_attendee_status", lambda user_id, event_id, status: updated.append(status))

    result = manager.deny_attendee({"eventID": "evt_1", "userID": "user_2", "organizerID": "user_1"})

    assert result == {"userID": "user_2", "status": "BLOCKED"}
    assert updated == ["BLOCKED"]


def test_eject_attendee_transitions_attendee_to_blocked(monkeypatch):
    monkeypatch.setattr(manager, "get_event", lambda event_id: _event())
    monkeypatch.setattr(manager, "get_attendee", lambda user_id, event_id: _attendee(status="ATTENDEE"))
    updated = []
    monkeypatch.setattr(manager, "update_attendee_status", lambda user_id, event_id, status: updated.append(status))

    result = manager.eject_attendee({"eventID": "evt_1", "userID": "user_2", "organizerID": "user_1"})

    assert result == {"userID": "user_2", "status": "BLOCKED"}
    assert updated == ["BLOCKED"]


def test_eject_attendee_rejects_non_attendee(monkeypatch):
    monkeypatch.setattr(manager, "get_event", lambda event_id: _event())
    monkeypatch.setattr(manager, "get_attendee", lambda user_id, event_id: _attendee(status="PENDING"))

    try:
        manager.eject_attendee({"eventID": "evt_1", "userID": "user_2", "organizerID": "user_1"})
        assert False, "expected ValueError"
    except ValueError:
        pass
