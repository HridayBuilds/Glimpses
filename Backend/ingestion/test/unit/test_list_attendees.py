import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import Manager.list_attendees as list_attendees


def test_list_attendees_returns_admitted_userids(monkeypatch):
    monkeypatch.setattr(list_attendees, "list_admitted_attendees", lambda event_id: ["user_1", "user_2"])

    result = list_attendees.handle_list_attendees({"eventID": "evt_1"})

    assert result == {"eventID": "evt_1", "attendeeIDs": ["user_1", "user_2"]}


def test_list_attendees_empty_event(monkeypatch):
    monkeypatch.setattr(list_attendees, "list_admitted_attendees", lambda event_id: [])

    result = list_attendees.handle_list_attendees({"eventID": "evt_1"})

    assert result == {"eventID": "evt_1", "attendeeIDs": []}
