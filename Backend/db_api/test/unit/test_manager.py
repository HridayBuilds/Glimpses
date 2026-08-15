import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import Manager.manager as manager  # noqa: E402


def test_create_builds_item_with_derived_eventUploaderKey_and_zeroed_counts(monkeypatch):
    created = {}
    monkeypatch.setattr(manager, "create_job", lambda item: created.update(item))

    result = manager.handle_action(
        "create",
        {
            "jobId": "job_1",
            "eventID": "evt_1",
            "uploaderID": "user_1",
            "status": "EXTRACTING",
            "startedAt": "2026-08-15T10:00:00Z",
        },
    )

    assert result == {"jobId": "job_1"}
    assert created == {
        "jobId": "job_1",
        "eventID": "evt_1",
        "uploaderID": "user_1",
        "status": "EXTRACTING",
        "startedAt": "2026-08-15T10:00:00Z",
        "eventUploaderKey": "evt_1#user_1",
        "succeededCount": 0,
        "failedCount": 0,
    }


def test_update_status_only_passes_fields_present_in_payload(monkeypatch):
    calls = {}
    monkeypatch.setattr(
        manager, "update_job_status", lambda job_id, updates: calls.update(job_id=job_id, updates=updates)
    )

    result = manager.handle_action("update_status", {"jobId": "job_1", "status": "INDEXING"})

    assert result == {"jobId": "job_1"}
    assert calls == {"job_id": "job_1", "updates": {"status": "INDEXING"}}


def test_update_status_includes_counts_when_provided(monkeypatch):
    calls = {}
    monkeypatch.setattr(
        manager, "update_job_status", lambda job_id, updates: calls.update(job_id=job_id, updates=updates)
    )

    manager.handle_action(
        "update_status",
        {"jobId": "job_1", "status": "COMPLETE_WITH_ERRORS", "succeededCount": 594, "failedCount": 6},
    )

    assert calls["updates"] == {
        "status": "COMPLETE_WITH_ERRORS",
        "succeededCount": 594,
        "failedCount": 6,
    }


def test_unknown_action_raises():
    try:
        manager.handle_action("delete", {})
        assert False, "expected ValueError"
    except ValueError:
        pass
