import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import Manager.delete_event as delete_event


def _event(**overrides):
    base = {"eventID": "evt_1", "rekognitionCollectionID": "glimpses-event-evt_1"}
    base.update(overrides)
    return base


def test_delete_event_cascade_no_op_when_event_missing(monkeypatch):
    monkeypatch.setattr(delete_event, "get_event", lambda event_id: None)

    result = delete_event.delete_event_cascade("evt_1")

    assert result == {"eventID": "evt_1", "deleted": False}


def test_delete_event_cascade_deletes_collection_faces_photos_s3_and_attendees(monkeypatch):
    monkeypatch.setattr(delete_event, "get_event", lambda event_id: _event())
    collection_calls = []
    monkeypatch.setattr(delete_event, "delete_collection", lambda collection_id: collection_calls.append(collection_id))
    monkeypatch.setattr(
        delete_event,
        "query_faces_by_event",
        lambda event_id: [{"rekognitionFaceID": "f1"}, {"rekognitionFaceID": "f2"}],
    )
    faces_calls = []
    monkeypatch.setattr(delete_event, "batch_delete_faces", lambda face_ids: faces_calls.append(face_ids))
    monkeypatch.setattr(
        delete_event,
        "query_photos_by_event",
        lambda event_id: [
            {"photoID": "p1", "s3Key": "photos/event/evt_1/p1.jpg", "thumbnailKey": "thumbnails/event/evt_1/p1.jpg"}
        ],
    )
    s3_calls = []
    monkeypatch.setattr(delete_event, "delete_s3_objects", lambda bucket, keys: s3_calls.append((bucket, keys)))
    photos_calls = []
    monkeypatch.setattr(delete_event, "batch_delete_photos", lambda photo_ids: photos_calls.append(photo_ids))
    monkeypatch.setattr(delete_event, "query_attendees_by_event", lambda event_id: [{"userID": "user_1"}, {"userID": "user_2"}])
    attendees_calls = []
    monkeypatch.setattr(
        delete_event, "batch_delete_attendees", lambda event_id, user_ids: attendees_calls.append((event_id, user_ids))
    )
    row_calls = []
    monkeypatch.setattr(delete_event, "delete_event_row", lambda event_id: row_calls.append(event_id))

    result = delete_event.delete_event_cascade("evt_1")

    assert result == {"eventID": "evt_1", "deleted": True}
    assert collection_calls == ["glimpses-event-evt_1"]
    assert faces_calls == [["f1", "f2"]]
    assert s3_calls == [("glimpses-photos-test-bucket", ["photos/event/evt_1/p1.jpg", "thumbnails/event/evt_1/p1.jpg"])]
    assert photos_calls == [["p1"]]
    assert attendees_calls == [("evt_1", ["user_1", "user_2"])]
    assert row_calls == ["evt_1"]


def test_delete_event_cascade_skips_batch_calls_when_nothing_to_delete(monkeypatch):
    monkeypatch.setattr(delete_event, "get_event", lambda event_id: _event())
    monkeypatch.setattr(delete_event, "delete_collection", lambda collection_id: None)
    monkeypatch.setattr(delete_event, "query_faces_by_event", lambda event_id: [])
    monkeypatch.setattr(delete_event, "query_photos_by_event", lambda event_id: [])
    monkeypatch.setattr(delete_event, "query_attendees_by_event", lambda event_id: [])
    s3_calls = []
    monkeypatch.setattr(delete_event, "delete_s3_objects", lambda bucket, keys: s3_calls.append(keys))

    def _fail(*args, **kwargs):
        assert False, "should not be called when there is nothing to delete"

    monkeypatch.setattr(delete_event, "batch_delete_faces", _fail)
    monkeypatch.setattr(delete_event, "batch_delete_photos", _fail)
    monkeypatch.setattr(delete_event, "batch_delete_attendees", _fail)
    monkeypatch.setattr(delete_event, "delete_event_row", lambda event_id: None)

    result = delete_event.delete_event_cascade("evt_1")

    assert result == {"eventID": "evt_1", "deleted": True}
    assert s3_calls == [[]]
