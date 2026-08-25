import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from Manager.finalize import handle_finalize


def test_all_succeeded():
    result = handle_finalize({
        "jobId": "job_1",
        "eventID": "evt_1",
        "extractFailedCount": 0,
        "indexResults": [{"status": "OK"}, {"status": "OK"}],
    })
    assert result == {"jobId": "job_1", "eventID": "evt_1", "succeededCount": 2, "failedCount": 0}


def test_some_photos_failed_but_others_succeeded():
    result = handle_finalize({
        "jobId": "job_1",
        "eventID": "evt_1",
        "extractFailedCount": 1,
        "indexResults": [{"status": "OK"}, {"status": "FAILED"}],
    })
    assert result == {"jobId": "job_1", "eventID": "evt_1", "succeededCount": 1, "failedCount": 2}


def test_total_failure_when_nothing_succeeded():
    result = handle_finalize({
        "jobId": "job_1",
        "eventID": "evt_1",
        "extractFailedCount": 3,
        "indexResults": [],
    })
    assert result == {"jobId": "job_1", "eventID": "evt_1", "succeededCount": 0, "failedCount": 3}
