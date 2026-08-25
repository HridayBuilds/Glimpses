import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import Manager.manager as manager


def test_get_profile_returns_profile_without_selfie_url_when_no_selfie(monkeypatch):
    monkeypatch.setattr(
        manager, "get_user", lambda user_id: {"userID": "user_1", "displayName": "Meera", "email": "meera@example.com"}
    )
    monkeypatch.setattr(manager, "selfie_exists", lambda bucket, key: False)

    result = manager.get_profile({"userID": "user_1"})

    assert result == {"userID": "user_1", "displayName": "Meera", "email": "meera@example.com"}


def test_get_profile_returns_selfie_url_when_selfie_exists(monkeypatch):
    monkeypatch.setattr(
        manager, "get_user", lambda user_id: {"userID": "user_1", "displayName": "Meera", "email": "meera@example.com"}
    )
    monkeypatch.setattr(manager, "selfie_exists", lambda bucket, key: True)
    monkeypatch.setattr(manager, "generate_presigned_get_url", lambda bucket, key: f"https://example/{key}")

    result = manager.get_profile({"userID": "user_1"})

    assert result["selfieUrl"] == "https://example/selfies/user/user_1/selfie.jpg"


def test_get_profile_creates_user_when_unknown(monkeypatch):
    created = {}
    users = {}

    def fake_get_user(user_id):
        return users.get(user_id)

    def fake_create_user(user_id, email, display_name):
        created.update(userID=user_id, email=email, displayName=display_name)
        users[user_id] = {"userID": user_id, "email": email, "displayName": display_name}

    monkeypatch.setattr(manager, "get_user", fake_get_user)
    monkeypatch.setattr(manager, "create_user", fake_create_user)
    monkeypatch.setattr(manager, "selfie_exists", lambda bucket, key: False)

    result = manager.get_profile({"userID": "missing", "email": "meera@example.com", "name": "Meera"})

    assert created == {"userID": "missing", "email": "meera@example.com", "displayName": "Meera"}
    assert result == {"userID": "missing", "displayName": "Meera", "email": "meera@example.com"}


def test_update_profile_updates_display_name(monkeypatch):
    updated = {}
    monkeypatch.setattr(
        manager, "update_display_name", lambda user_id, display_name: updated.update(userID=user_id, displayName=display_name)
    )

    result = manager.update_profile({"userID": "user_1", "displayName": "Meera Nair"})

    assert result == {"userID": "user_1"}
    assert updated == {"userID": "user_1", "displayName": "Meera Nair"}


def test_mint_selfie_upload_url_returns_url(monkeypatch):
    monkeypatch.setattr(manager, "generate_presigned_put_url", lambda bucket, key: f"https://example/{key}")

    result = manager.mint_selfie_upload_url({"userID": "user_1"})

    assert result == {"uploadUrl": "https://example/selfies/user/user_1/selfie.jpg"}


def test_confirm_selfie_keeps_object_when_exactly_one_face(monkeypatch):
    deleted = []
    monkeypatch.setattr(manager, "detect_face_count", lambda bucket, key: 1)
    monkeypatch.setattr(manager, "delete_object", lambda bucket, key: deleted.append(key))

    result = manager.confirm_selfie({"userID": "user_1"})

    assert result == {"confirmed": True}
    assert deleted == []


def test_confirm_selfie_deletes_object_and_raises_when_zero_faces(monkeypatch):
    deleted = []
    monkeypatch.setattr(manager, "detect_face_count", lambda bucket, key: 0)
    monkeypatch.setattr(manager, "delete_object", lambda bucket, key: deleted.append(key))

    try:
        manager.confirm_selfie({"userID": "user_1"})
        assert False, "expected ValueError"
    except ValueError:
        pass

    assert deleted == ["selfies/user/user_1/selfie.jpg"]


def test_confirm_selfie_deletes_object_and_raises_when_multiple_faces(monkeypatch):
    deleted = []
    monkeypatch.setattr(manager, "detect_face_count", lambda bucket, key: 2)
    monkeypatch.setattr(manager, "delete_object", lambda bucket, key: deleted.append(key))

    try:
        manager.confirm_selfie({"userID": "user_1"})
        assert False, "expected ValueError"
    except ValueError:
        pass

    assert deleted == ["selfies/user/user_1/selfie.jpg"]


def test_delete_selfie_deletes_object(monkeypatch):
    deleted = []
    monkeypatch.setattr(manager, "delete_object", lambda bucket, key: deleted.append(key))

    result = manager.delete_selfie({"userID": "user_1"})

    assert result == {"deleted": True}
    assert deleted == ["selfies/user/user_1/selfie.jpg"]
