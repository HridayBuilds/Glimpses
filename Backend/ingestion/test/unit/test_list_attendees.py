import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import Manager.list_attendees as list_attendees


def test_list_attendees_writes_manifest_of_admitted_userids(monkeypatch):
    stored_objects = {}
    monkeypatch.setattr(list_attendees, "list_admitted_attendees", lambda event_id: ["user_1", "user_2"])
    monkeypatch.setattr(list_attendees, "put_object", lambda bucket, key, body, content_type=None: stored_objects.update({key: body}))

    result = list_attendees.handle_list_attendees({"eventID": "evt_1", "jobId": "job_1"})

    assert result["eventID"] == "evt_1"
    assert result["attendeesManifestKey"] == "uploads/event/evt_1/job/job_1/attendees-manifest.json"
    assert json.loads(stored_objects[result["attendeesManifestKey"]]) == ["user_1", "user_2"]


def test_list_attendees_empty_event(monkeypatch):
    stored_objects = {}
    monkeypatch.setattr(list_attendees, "list_admitted_attendees", lambda event_id: [])
    monkeypatch.setattr(list_attendees, "put_object", lambda bucket, key, body, content_type=None: stored_objects.update({key: body}))

    result = list_attendees.handle_list_attendees({"eventID": "evt_1", "jobId": "job_1"})

    assert json.loads(stored_objects[result["attendeesManifestKey"]]) == []
