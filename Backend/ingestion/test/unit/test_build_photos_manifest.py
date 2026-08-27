import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import Manager.build_photos_manifest as build_photos_manifest


def test_build_photos_manifest_keeps_only_succeeded_photos(monkeypatch):
    stored_objects = {}
    monkeypatch.setattr(build_photos_manifest, "put_object", lambda bucket, key, body, content_type=None: stored_objects.update({key: body}))

    result = build_photos_manifest.handle_build_photos_manifest({
        "jobId": "job_1",
        "eventID": "evt_1",
        "processResults": [
            {"filename": "a.jpg", "status": "SUCCEEDED", "photoID": "photo_1", "eventID": "evt_1", "s3Key": "photos/event/evt_1/photo_1.jpg"},
            {"filename": "b.jpg", "status": "FAILED"},
            {"filename": "c.jpg", "status": "DUPLICATE"},
        ],
    })

    assert result["eventID"] == "evt_1"
    assert result["jobId"] == "job_1"
    assert result["processFailedCount"] == 1
    assert result["manifestKey"] == "uploads/event/evt_1/job/job_1/photos-manifest.json"

    manifest = json.loads(stored_objects[result["manifestKey"]])
    assert manifest == [{"photoID": "photo_1", "eventID": "evt_1", "s3Key": "photos/event/evt_1/photo_1.jpg"}]


def test_build_photos_manifest_handles_no_results(monkeypatch):
    monkeypatch.setattr(build_photos_manifest, "put_object", lambda bucket, key, body, content_type=None: None)

    result = build_photos_manifest.handle_build_photos_manifest({
        "jobId": "job_1",
        "eventID": "evt_1",
    })

    assert result["processFailedCount"] == 0
