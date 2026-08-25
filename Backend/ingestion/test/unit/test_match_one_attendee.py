import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import Manager.match_one_attendee as match_one_attendee


def test_resolves_each_stream_record(monkeypatch):
    calls = []

    def _fake_resolve(event_id, user_id):
        calls.append((event_id, user_id))
        return {"eventID": event_id, "userID": user_id, "matchedCount": 1}

    monkeypatch.setattr(match_one_attendee, "resolve_and_store_matches", _fake_resolve)

    records = [
        {"dynamodb": {"Keys": {"userID": {"S": "user_1"}, "eventID": {"S": "evt_1"}}}},
        {"dynamodb": {"Keys": {"userID": {"S": "user_2"}, "eventID": {"S": "evt_1"}}}},
    ]

    results = match_one_attendee.handle_stream_records(records)

    assert calls == [("evt_1", "user_1"), ("evt_1", "user_2")]
    assert len(results) == 2
