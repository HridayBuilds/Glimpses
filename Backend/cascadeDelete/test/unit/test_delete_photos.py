import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import Manager.delete_photos as delete_photos


def _photo(**overrides):
    base = {
        "photoID": "p1",
        "eventID": "evt_1",
        "sizeBytes": 1234,
        "s3Key": "photos/event/evt_1/p1.jpg",
        "thumbnailKey": "thumbnails/event/evt_1/p1.jpg",
    }
    base.update(overrides)
    return base


def test_delete_photos_cascade_skips_photo_ids_already_gone(monkeypatch):
    monkeypatch.setattr(delete_photos, "get_event", lambda event_id: {"rekognitionCollectionID": "col_1"})
    monkeypatch.setattr(delete_photos, "get_photo", lambda photo_id: None)
    monkeypatch.setattr(delete_photos, "query_faces_by_event", lambda event_id: [])
    s3_calls = []
    monkeypatch.setattr(delete_photos, "delete_s3_objects", lambda bucket, keys: s3_calls.append(keys))
    decrement_calls = []
    monkeypatch.setattr(
        delete_photos, "decrement_event_counters", lambda event_id, p, s: decrement_calls.append((event_id, p, s))
    )

    result = delete_photos.delete_photos_cascade("evt_1", ["p1"])

    assert result == {"eventID": "evt_1", "deletedPhotoIDs": []}
    assert s3_calls == [[]]
    assert decrement_calls == []


def test_delete_photos_cascade_deletes_faces_row_s3_and_decrements_counters(monkeypatch):
    monkeypatch.setattr(delete_photos, "get_event", lambda event_id: {"rekognitionCollectionID": "col_1"})
    monkeypatch.setattr(delete_photos, "get_photo", lambda photo_id: _photo(photoID=photo_id))
    monkeypatch.setattr(
        delete_photos,
        "query_faces_by_event",
        lambda event_id: [{"rekognitionFaceID": "f1", "photoID": "p1"}, {"rekognitionFaceID": "f2", "photoID": "other"}],
    )
    rekognition_calls = []
    monkeypatch.setattr(
        delete_photos, "delete_faces_from_collection", lambda collection_id, face_ids: rekognition_calls.append((collection_id, face_ids))
    )
    faces_calls = []
    monkeypatch.setattr(delete_photos, "batch_delete_faces", lambda face_ids: faces_calls.append(face_ids))
    photos_calls = []
    monkeypatch.setattr(delete_photos, "batch_delete_photos", lambda photo_ids: photos_calls.append(photo_ids))
    s3_calls = []
    monkeypatch.setattr(delete_photos, "delete_s3_objects", lambda bucket, keys: s3_calls.append(keys))
    decrement_calls = []
    monkeypatch.setattr(
        delete_photos, "decrement_event_counters", lambda event_id, p, s: decrement_calls.append((event_id, p, s))
    )

    result = delete_photos.delete_photos_cascade("evt_1", ["p1"])

    assert result == {"eventID": "evt_1", "deletedPhotoIDs": ["p1"]}
    assert rekognition_calls == [("col_1", ["f1"])]
    assert faces_calls == [["f1"]]
    assert photos_calls == [["p1"]]
    assert s3_calls == [["photos/event/evt_1/p1.jpg", "thumbnails/event/evt_1/p1.jpg"]]
    assert decrement_calls == [("evt_1", -1, -1234)]


def test_delete_photos_cascade_skips_rekognition_when_event_missing(monkeypatch):
    monkeypatch.setattr(delete_photos, "get_event", lambda event_id: None)
    monkeypatch.setattr(delete_photos, "get_photo", lambda photo_id: _photo())
    monkeypatch.setattr(delete_photos, "query_faces_by_event", lambda event_id: [{"rekognitionFaceID": "f1", "photoID": "p1"}])

    def _fail(*args, **kwargs):
        assert False, "should not call Rekognition when the event row is gone"

    monkeypatch.setattr(delete_photos, "delete_faces_from_collection", _fail)
    monkeypatch.setattr(delete_photos, "batch_delete_faces", lambda face_ids: None)
    monkeypatch.setattr(delete_photos, "batch_delete_photos", lambda photo_ids: None)
    monkeypatch.setattr(delete_photos, "delete_s3_objects", lambda bucket, keys: None)
    monkeypatch.setattr(delete_photos, "decrement_event_counters", lambda event_id, p, s: None)

    result = delete_photos.delete_photos_cascade("evt_1", ["p1"])

    assert result == {"eventID": "evt_1", "deletedPhotoIDs": ["p1"]}
