import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from Manager.finalize import handle_finalize  # noqa: E402


def test_all_succeeded():
    result = handle_finalize({
        "jobId": "job_1",
        "eventID": "evt_1",
        "extractFailedCount": 0,
        "indexResults": [{"status": "OK"}, {"status": "OK"}],
    })
    assert result == {"jobId": "job_1", "eventID": "evt_1", "status": "SUCCEEDED", "succeededCount": 2, "failedCount": 0}


def test_partial_failure():
    result = handle_finalize({
        "jobId": "job_1",
        "eventID": "evt_1",
        "extractFailedCount": 1,
        "indexResults": [{"status": "OK"}, {"status": "FAILED"}],
    })
    assert result == {"jobId": "job_1", "eventID": "evt_1", "status": "PARTIAL", "succeededCount": 1, "failedCount": 2}


def test_total_failure_when_nothing_succeeded():
    result = handle_finalize({
        "jobId": "job_1",
        "eventID": "evt_1",
        "extractFailedCount": 3,
        "indexResults": [],
    })
    assert result == {"jobId": "job_1", "eventID": "evt_1", "status": "FAILED", "succeededCount": 0, "failedCount": 3}
