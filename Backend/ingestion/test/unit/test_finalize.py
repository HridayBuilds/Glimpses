import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import Manager.finalize as finalize


def _manifest_bytes(succeeded_keys=(), failed_keys=()):
    return json.dumps(
        {
            "ResultFiles": {
                "SUCCEEDED": [{"Key": key} for key in succeeded_keys],
                "FAILED": [{"Key": key} for key in failed_keys],
            }
        }
    ).encode("utf-8")


def _result_file_bytes(outputs):
    return json.dumps([{"Output": json.dumps(output)} for output in outputs]).encode("utf-8")


def test_all_succeeded(monkeypatch):
    objects = {
        "results/manifest.json": _manifest_bytes(succeeded_keys=["results/succeeded-0.json"]),
        "results/succeeded-0.json": _result_file_bytes([{"status": "SUCCEEDED"}, {"status": "SUCCEEDED"}]),
    }
    monkeypatch.setattr(finalize, "get_object", lambda bucket, key: objects[key])

    result = finalize.handle_finalize(
        {
            "jobId": "job_1",
            "eventID": "evt_1",
            "processFailedCount": 0,
            "indexResultsBucket": "results-bucket",
            "indexResultsManifestKey": "results/manifest.json",
        }
    )

    assert result == {"jobId": "job_1", "eventID": "evt_1", "succeededCount": 2, "failedCount": 0}


def test_some_photos_failed_but_others_succeeded(monkeypatch):
    objects = {
        "results/manifest.json": _manifest_bytes(succeeded_keys=["results/succeeded-0.json"]),
        "results/succeeded-0.json": _result_file_bytes([{"status": "SUCCEEDED"}, {"status": "FAILED"}]),
    }
    monkeypatch.setattr(finalize, "get_object", lambda bucket, key: objects[key])

    result = finalize.handle_finalize(
        {
            "jobId": "job_1",
            "eventID": "evt_1",
            "processFailedCount": 1,
            "indexResultsBucket": "results-bucket",
            "indexResultsManifestKey": "results/manifest.json",
        }
    )

    assert result == {"jobId": "job_1", "eventID": "evt_1", "succeededCount": 1, "failedCount": 2}


def test_total_failure_when_nothing_succeeded(monkeypatch):
    objects = {"results/manifest.json": _manifest_bytes()}
    monkeypatch.setattr(finalize, "get_object", lambda bucket, key: objects[key])

    result = finalize.handle_finalize(
        {
            "jobId": "job_1",
            "eventID": "evt_1",
            "processFailedCount": 3,
            "indexResultsBucket": "results-bucket",
            "indexResultsManifestKey": "results/manifest.json",
        }
    )

    assert result == {"jobId": "job_1", "eventID": "evt_1", "succeededCount": 0, "failedCount": 3}


def test_counts_task_level_index_failures(monkeypatch):
    objects = {
        "results/manifest.json": _manifest_bytes(succeeded_keys=["results/succeeded-0.json"], failed_keys=["results/failed-0.json"]),
        "results/succeeded-0.json": _result_file_bytes([{"status": "SUCCEEDED"}]),
        "results/failed-0.json": json.dumps([{"Error": "States.Timeout"}]).encode("utf-8"),
    }
    monkeypatch.setattr(finalize, "get_object", lambda bucket, key: objects[key])

    result = finalize.handle_finalize(
        {
            "jobId": "job_1",
            "eventID": "evt_1",
            "processFailedCount": 0,
            "indexResultsBucket": "results-bucket",
            "indexResultsManifestKey": "results/manifest.json",
        }
    )

    assert result == {"jobId": "job_1", "eventID": "evt_1", "succeededCount": 1, "failedCount": 1}
