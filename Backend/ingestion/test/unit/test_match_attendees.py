import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import Manager.match_attendees as match_attendees


def test_matches_and_stores_photo_ids(monkeypatch):
    added = {}
    monkeypatch.setattr(match_attendees, "selfie_exists", lambda bucket, key: True)
    monkeypatch.setattr(match_attendees, "get_event", lambda event_id: {"rekognitionCollectionID": "evt_1-collection"})
    monkeypatch.setattr(
        match_attendees,
        "search_faces_by_image",
        lambda collection_id, bucket, key, threshold: [{"Face": {"FaceId": "face-1"}}, {"Face": {"FaceId": "face-2"}}],
    )
    monkeypatch.setattr(
        match_attendees,
        "get_faces",
        lambda face_ids: [{"photoID": "photo_1"}, {"photoID": "photo_2"}],
    )
    monkeypatch.setattr(
        match_attendees,
        "add_matched_photo_ids",
        lambda user_id, event_id, photo_ids: added.update(user_id=user_id, event_id=event_id, photo_ids=photo_ids),
    )

    result = match_attendees.resolve_and_store_matches("evt_1", "user_1")

    assert result == {"eventID": "evt_1", "userID": "user_1", "matchedCount": 2}
    assert added["photo_ids"] == {"photo_1", "photo_2"}


def test_skips_attendee_with_no_selfie(monkeypatch):
    monkeypatch.setattr(match_attendees, "selfie_exists", lambda bucket, key: False)

    result = match_attendees.resolve_and_store_matches("evt_1", "user_1")

    assert result == {"eventID": "evt_1", "userID": "user_1", "matchedCount": 0}
