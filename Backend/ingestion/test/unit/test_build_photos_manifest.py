import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import Manager.build_photos_manifest as build_photos_manifest


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


def test_build_photos_manifest_keeps_only_succeeded_photos(monkeypatch):
    stored_objects = {}
    objects = {
        "results/manifest.json": _manifest_bytes(succeeded_keys=["results/succeeded-0.json"]),
        "results/succeeded-0.json": _result_file_bytes(
            [
                {"filename": "a.jpg", "status": "SUCCEEDED", "photoID": "photo_1", "eventID": "evt_1", "s3Key": "photos/event/evt_1/photo_1.jpg"},
                {"filename": "b.jpg", "status": "FAILED"},
                {"filename": "c.jpg", "status": "DUPLICATE"},
            ]
        ),
    }
    monkeypatch.setattr(build_photos_manifest, "get_object", lambda bucket, key: objects[key])
    monkeypatch.setattr(build_photos_manifest, "put_object", lambda bucket, key, body, content_type=None: stored_objects.update({key: body}))

    result = build_photos_manifest.handle_build_photos_manifest(
        {
            "jobId": "job_1",
            "eventID": "evt_1",
            "processResultsBucket": "results-bucket",
            "processResultsManifestKey": "results/manifest.json",
        }
    )

    assert result["eventID"] == "evt_1"
    assert result["jobId"] == "job_1"
    assert result["processFailedCount"] == 1
    assert result["manifestKey"] == "uploads/event/evt_1/job/job_1/photos-manifest.json"

    manifest = json.loads(stored_objects[result["manifestKey"]])
    assert manifest == [{"photoID": "photo_1", "eventID": "evt_1", "s3Key": "photos/event/evt_1/photo_1.jpg"}]


def test_build_photos_manifest_counts_task_level_failures(monkeypatch):
    objects = {
        "results/manifest.json": _manifest_bytes(succeeded_keys=[], failed_keys=["results/failed-0.json"]),
        "results/failed-0.json": json.dumps([{"Error": "States.Timeout"}, {"Error": "States.Timeout"}]).encode("utf-8"),
    }
    monkeypatch.setattr(build_photos_manifest, "get_object", lambda bucket, key: objects[key])
    monkeypatch.setattr(build_photos_manifest, "put_object", lambda bucket, key, body, content_type=None: None)

    result = build_photos_manifest.handle_build_photos_manifest(
        {
            "jobId": "job_1",
            "eventID": "evt_1",
            "processResultsBucket": "results-bucket",
            "processResultsManifestKey": "results/manifest.json",
        }
    )

    assert result["processFailedCount"] == 2
