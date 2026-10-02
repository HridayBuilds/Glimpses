import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import Manager.manager as manager

UPLOAD_ID = "12345678-1234-4123-8123-123456789abc"


def test_get_profile_returns_profile_without_selfie_url_when_no_selfie(monkeypatch):
    monkeypatch.setattr(
        manager, "get_user", lambda user_id: {"userID": "user_1", "displayName": "Meera", "email": "meera@example.com"}
    )
    monkeypatch.setattr(manager, "selfie_exists", lambda bucket, key: False)

    result = manager.get_profile({"userID": "user_1"})

    assert result == {"userID": "user_1", "displayName": "Meera", "email": "meera@example.com", "emailNotificationsEnabled": True}


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
    assert result == {"userID": "missing", "displayName": "Meera", "email": "meera@example.com", "emailNotificationsEnabled": True}


def test_email_notifications_preference_requires_boolean(monkeypatch):
    changed = []
    monkeypatch.setattr(manager, "set_email_notifications_enabled", lambda user_id, enabled: changed.append((user_id, enabled)))
    assert manager.update_email_notifications({"userID": "user_1", "enabled": False}) == {"emailNotificationsEnabled": False}
    assert changed == [("user_1", False)]
    try:
        manager.update_email_notifications({"userID": "user_1", "enabled": "false"})
        assert False, "expected ValueError"
    except ValueError:
        pass


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
    monkeypatch.setattr(manager.uuid, "uuid4", lambda: UPLOAD_ID)

    result = manager.mint_selfie_upload_url({"userID": "user_1"})

    assert result == {"uploadUrl": f"https://example/selfies/pending/user/user_1/{UPLOAD_ID}.jpg", "uploadId": UPLOAD_ID}


def test_confirm_selfie_keeps_object_when_exactly_one_face(monkeypatch):
    deleted = []
    copied = []
    scheduled = []
    monkeypatch.setattr(manager, "detect_face_count", lambda bucket, key: 1)
    monkeypatch.setattr(manager, "delete_object", lambda bucket, key: deleted.append(key))
    monkeypatch.setattr(manager, "copy_object", lambda bucket, source, target: copied.append((source, target)))
    monkeypatch.setattr(manager, "get_user", lambda user_id: {})
    monkeypatch.setattr(manager, "create_user", lambda user_id, email, name: None)
    monkeypatch.setattr(manager, "set_current_selfie", lambda user_id, key, version: None)
    monkeypatch.setattr(manager, "invoke_selfie_match_dispatcher", lambda user_id, version: scheduled.append((user_id, version)))
    monkeypatch.setattr(manager, "selfie_exists", lambda bucket, key: False)

    result = manager.confirm_selfie({"userID": "user_1", "uploadId": UPLOAD_ID})

    assert result == {"confirmed": True}
    assert copied == [(f"selfies/pending/user/user_1/{UPLOAD_ID}.jpg", f"selfies/user/user_1/{UPLOAD_ID}.jpg")]
    assert deleted == [f"selfies/pending/user/user_1/{UPLOAD_ID}.jpg"]
    assert scheduled == [("user_1", UPLOAD_ID)]


def test_confirm_selfie_deletes_object_and_raises_when_zero_faces(monkeypatch):
    deleted = []
    monkeypatch.setattr(manager, "detect_face_count", lambda bucket, key: 0)
    monkeypatch.setattr(manager, "delete_object", lambda bucket, key: deleted.append(key))

    try:
        manager.confirm_selfie({"userID": "user_1", "uploadId": UPLOAD_ID})
        assert False, "expected ValueError"
    except ValueError:
        pass

    assert deleted == [f"selfies/pending/user/user_1/{UPLOAD_ID}.jpg"]


def test_confirm_selfie_deletes_object_and_raises_when_multiple_faces(monkeypatch):
    deleted = []
    monkeypatch.setattr(manager, "detect_face_count", lambda bucket, key: 2)
    monkeypatch.setattr(manager, "delete_object", lambda bucket, key: deleted.append(key))

    try:
        manager.confirm_selfie({"userID": "user_1", "uploadId": UPLOAD_ID})
        assert False, "expected ValueError"
    except ValueError:
        pass

    assert deleted == [f"selfies/pending/user/user_1/{UPLOAD_ID}.jpg"]


def test_delete_selfie_deletes_object(monkeypatch):
    deleted = []
    monkeypatch.setattr(manager, "delete_object", lambda bucket, key: deleted.append(key))
    monkeypatch.setattr(manager, "get_user", lambda user_id: {"selfieKey": "selfies/user/user_1/new.jpg"})
    monkeypatch.setattr(manager, "clear_current_selfie", lambda user_id: None)

    result = manager.delete_selfie({"userID": "user_1"})

    assert result == {"deleted": True}
    assert deleted == ["selfies/user/user_1/new.jpg"]
