import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import Manager.ttl_delete as ttl_delete


def test_handle_stream_records_cascades_each_record_with_deleted_event_image(monkeypatch):
    calls = []
    monkeypatch.setattr(
        ttl_delete,
        "delete_event_cascade",
        lambda event_id, deleted_event: calls.append((event_id, deleted_event)) or {"eventID": event_id, "deleted": True},
    )

    records = [
        {"dynamodb": {"OldImage": {"eventID": {"S": "evt_1"}, "rekognitionCollectionID": {"S": "col_1"}}}},
        {"dynamodb": {"OldImage": {"eventID": {"S": "evt_2"}, "rekognitionCollectionID": {"S": "col_2"}}}},
    ]

    results = ttl_delete.handle_stream_records(records)

    assert calls == [
        ("evt_1", {"eventID": "evt_1", "rekognitionCollectionID": "col_1"}),
        ("evt_2", {"eventID": "evt_2", "rekognitionCollectionID": "col_2"}),
    ]
    assert len(results) == 2
