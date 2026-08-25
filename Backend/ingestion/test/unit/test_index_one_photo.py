import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import Manager.index_one_photo as index_one_photo


def test_indexes_faces_and_stores_each_one(monkeypatch):
    stored_faces = []
    monkeypatch.setattr(index_one_photo, "get_event", lambda event_id: {"rekognitionCollectionID": "evt_1-collection"})
    monkeypatch.setattr(
        index_one_photo,
        "index_faces",
        lambda collection_id, bucket, key: [{"Face": {"FaceId": "face-1"}}, {"Face": {"FaceId": "face-2"}}],
    )
    monkeypatch.setattr(index_one_photo, "put_face", lambda item: stored_faces.append(item))

    result = index_one_photo.handle_index_one_photo({
        "eventID": "evt_1",
        "photoID": "photo_1",
        "s3Key": "photos/event/evt_1/photo_1.jpg",
    })

    assert result == {"photoID": "photo_1", "status": "SUCCEEDED", "faceCount": 2}
    assert stored_faces == [
        {"rekognitionFaceID": "face-1", "eventID": "evt_1", "photoID": "photo_1"},
        {"rekognitionFaceID": "face-2", "eventID": "evt_1", "photoID": "photo_1"},
    ]


def test_handles_photo_with_no_faces(monkeypatch):
    monkeypatch.setattr(index_one_photo, "get_event", lambda event_id: {"rekognitionCollectionID": "evt_1-collection"})
    monkeypatch.setattr(index_one_photo, "index_faces", lambda collection_id, bucket, key: [])
    monkeypatch.setattr(index_one_photo, "put_face", lambda item: (_ for _ in ()).throw(AssertionError("should not be called")))

    result = index_one_photo.handle_index_one_photo({
        "eventID": "evt_1",
        "photoID": "photo_1",
        "s3Key": "photos/event/evt_1/photo_1.jpg",
    })

    assert result == {"photoID": "photo_1", "status": "SUCCEEDED", "faceCount": 0}


def test_indexing_error_is_caught_and_counted_as_failed(monkeypatch):
    monkeypatch.setattr(index_one_photo, "get_event", lambda event_id: {"rekognitionCollectionID": "evt_1-collection"})
    monkeypatch.setattr(index_one_photo, "index_faces", lambda collection_id, bucket, key: (_ for _ in ()).throw(RuntimeError("boom")))
    monkeypatch.setattr(index_one_photo, "put_face", lambda item: (_ for _ in ()).throw(AssertionError("should not be called")))

    result = index_one_photo.handle_index_one_photo({
        "eventID": "evt_1",
        "photoID": "photo_1",
        "s3Key": "photos/event/evt_1/photo_1.jpg",
    })

    assert result == {"photoID": "photo_1", "status": "FAILED", "faceCount": 0}
