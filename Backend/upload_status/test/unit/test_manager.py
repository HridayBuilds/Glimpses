import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import Manager.manager as manager


def _job(**overrides):
    base = {
        "jobId": "job_1",
        "eventID": "evt_1",
        "uploaderID": "user_1",
        "status": "EXTRACTING",
        "startedAt": "2026-08-23T00:00:00Z",
        "succeededCount": 3,
        "failedCount": 1,
    }
    base.update(overrides)
    return base


def _event(**overrides):
    base = {
        "eventID": "evt_1",
        "organizerID": "organizer_1",
        "status": "ACTIVE",
        "contributionPolicy": "ATTENDEES_CAN_ADD",
    }
    base.update(overrides)
    return base


def test_mint_upload_url_builds_key_from_event_and_user_and_generated_job_id(monkeypatch):
    captured_keys = []
    monkeypatch.setattr(manager, "get_event", lambda event_id: _event())
    monkeypatch.setattr(manager, "generate_presigned_put_url", lambda key: captured_keys.append(key) or "https://signed")

    result = manager.mint_upload_url({"eventID": "evt_1", "userID": "user_1"})

    assert result["uploadUrl"] == "https://signed"
    job_id = result["jobId"]
    assert captured_keys == [f"uploads/event/evt_1/user/user_1/job/{job_id}/original.zip"]


def test_mint_upload_url_allows_organizer_when_organizer_only(monkeypatch):
    monkeypatch.setattr(manager, "get_event", lambda event_id: _event(contributionPolicy="ORGANIZER_ONLY"))
    monkeypatch.setattr(manager, "generate_presigned_put_url", lambda key: "https://signed")

    result = manager.mint_upload_url({"eventID": "evt_1", "userID": "organizer_1"})

    assert result["uploadUrl"] == "https://signed"


def test_mint_upload_url_rejects_attendee_when_organizer_only(monkeypatch):
    monkeypatch.setattr(manager, "get_event", lambda event_id: _event(contributionPolicy="ORGANIZER_ONLY"))

    with pytest.raises(ValueError):
        manager.mint_upload_url({"eventID": "evt_1", "userID": "user_1"})


def test_mint_upload_url_rejects_unknown_event(monkeypatch):
    monkeypatch.setattr(manager, "get_event", lambda event_id: None)

    with pytest.raises(ValueError):
        manager.mint_upload_url({"eventID": "evt_1", "userID": "user_1"})


def test_mint_upload_url_rejects_archived_event(monkeypatch):
    monkeypatch.setattr(manager, "get_event", lambda event_id: _event(status="ARCHIVED"))

    with pytest.raises(ValueError):
        manager.mint_upload_url({"eventID": "evt_1", "userID": "organizer_1"})


def test_get_job_status_returns_job_owned_by_caller(monkeypatch):
    monkeypatch.setattr(manager, "get_job", lambda job_id: _job())

    result = manager.get_job_status({"eventID": "evt_1", "jobId": "job_1", "userID": "user_1"})

    assert result == {
        "jobId": "job_1",
        "status": "EXTRACTING",
        "startedAt": "2026-08-23T00:00:00Z",
        "succeededCount": 3,
        "failedCount": 1,
    }


def test_get_job_status_rejects_job_belonging_to_another_uploader(monkeypatch):
    monkeypatch.setattr(manager, "get_job", lambda job_id: _job(uploaderID="user_2"))

    try:
        manager.get_job_status({"eventID": "evt_1", "jobId": "job_1", "userID": "user_1"})
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_get_job_status_rejects_unknown_job(monkeypatch):
    monkeypatch.setattr(manager, "get_job", lambda job_id: None)

    try:
        manager.get_job_status({"eventID": "evt_1", "jobId": "job_1", "userID": "user_1"})
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_get_latest_job_returns_most_recent_via_dao(monkeypatch):
    monkeypatch.setattr(manager, "query_latest_job", lambda event_id, user_id: _job(jobId="job_2"))

    result = manager.get_latest_job({"eventID": "evt_1", "userID": "user_1"})

    assert result["jobId"] == "job_2"


def test_get_latest_job_raises_when_uploader_has_no_jobs(monkeypatch):
    monkeypatch.setattr(manager, "query_latest_job", lambda event_id, user_id: None)

    try:
        manager.get_latest_job({"eventID": "evt_1", "userID": "user_1"})
        assert False, "expected ValueError"
    except ValueError:
        pass
