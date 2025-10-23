import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from cli_multi_rapid.security.auth import APIKeyManager, JWTManager


@pytest.fixture()
def storage_file(tmp_path: Path) -> Path:
    return tmp_path / "keys.json"


@pytest.fixture()
def manager(storage_file: Path) -> APIKeyManager:
    return APIKeyManager(storage_file)


@pytest.fixture()
def jwt_stub(monkeypatch):
    payloads: dict[str, dict] = {}

    class _Expired(Exception):
        pass

    class _Invalid(Exception):
        pass

    def encode(payload, secret_key, algorithm):
        token = json.dumps(payload)
        payloads[token] = payload
        return token

    def decode(token, secret_key=None, algorithms=None, options=None):
        if token == "expired":
            raise _Expired()
        if token == "invalid":
            raise _Invalid()
        return payloads.get(token, json.loads(token))

    stub = SimpleNamespace(
        encode=encode,
        decode=decode,
        ExpiredSignatureError=_Expired,
        InvalidTokenError=_Invalid,
    )

    monkeypatch.setattr("cli_multi_rapid.security.auth.jwt", stub, raising=False)
    monkeypatch.setattr("cli_multi_rapid.security.auth.JWT_AVAILABLE", True)
    return stub


def test_create_and_verify_key_updates_last_used(monkeypatch, manager, storage_file):
    base_time = 1_700_000_000
    monkeypatch.setattr(
        "cli_multi_rapid.security.auth.time.time", lambda: float(base_time)
    )
    monkeypatch.setattr(
        "cli_multi_rapid.security.auth.secrets.token_urlsafe", lambda _: "deterministic"
    )

    api_key = manager.create_key("user-1", description="ci token", expiry_days=1)
    assert api_key == "clio_deterministic"
    assert storage_file.exists()

    stored = manager._keys[api_key]
    assert stored["user_id"] == "user-1"
    assert stored["description"] == "ci token"
    assert stored["expires_at"] == float(base_time + 86400)
    assert stored["last_used"] is None

    next_time = float(base_time + 42)
    monkeypatch.setattr(
        "cli_multi_rapid.security.auth.time.time", lambda: next_time, raising=False
    )
    verified = manager.verify_key(api_key)
    assert verified is not None
    assert verified["last_used"] == next_time

    reloaded = APIKeyManager(storage_file)
    assert reloaded.verify_key(api_key)["last_used"] >= next_time


def test_verify_key_handles_inactive_and_expired(monkeypatch, manager):
    current_time = 1000.0

    def _time():
        return current_time

    monkeypatch.setattr("cli_multi_rapid.security.auth.time.time", _time)

    sequence = iter(["active", "inactive", "expired"])
    monkeypatch.setattr(
        "cli_multi_rapid.security.auth.secrets.token_urlsafe",
        lambda _: next(sequence),
    )

    active_key = manager.create_key("user-2")
    inactive_key = manager.create_key("user-2")
    assert manager.revoke_key(inactive_key) is True

    assert manager.verify_key("missing") is None
    assert manager.verify_key(active_key) is not None
    assert manager.verify_key(inactive_key) is None

    expired_key = manager.create_key("user-3", expiry_days=1)
    manager._keys[expired_key]["expires_at"] = current_time - 1
    current_time = 2000.0
    assert manager.verify_key(expired_key) is None


def test_list_keys_for_user_and_cleanup_expired(monkeypatch, manager):
    base_time = 5_000.0
    monkeypatch.setattr("cli_multi_rapid.security.auth.time.time", lambda: base_time)

    tokens = iter(["first", "second", "third"])
    monkeypatch.setattr(
        "cli_multi_rapid.security.auth.secrets.token_urlsafe", lambda _: next(tokens)
    )

    key_one = manager.create_key("user-5", expiry_days=1)
    key_two = manager.create_key("user-5", expiry_days=1)
    manager.create_key("user-6", expiry_days=1)

    manager._keys[key_one]["expires_at"] = base_time - 10
    manager._keys[key_two]["expires_at"] = base_time + 10

    listed = manager.list_keys_for_user("user-5")
    assert len(listed) == 2
    assert all("key_prefix" in entry for entry in listed)
    assert all(not entry.get("key") for entry in listed)

    cleanup_count = manager.cleanup_expired_keys()
    assert cleanup_count == 1
    assert key_one not in manager._keys
    assert key_two in manager._keys

    persisted = json.loads(Path(manager.storage_file).read_text())
    assert key_one not in persisted
    assert key_two in persisted


def test_revoke_key_returns_false_for_unknown(manager):
    assert manager.revoke_key("does-not-exist") is False


def test_save_keys_logs_errors(monkeypatch, manager, caplog):
    def fail_dump(*_args, **_kwargs):
        raise RuntimeError("write failed")

    monkeypatch.setattr("cli_multi_rapid.security.auth.json.dump", fail_dump)

    with caplog.at_level("ERROR"):
        manager._save_keys()

    assert "Failed to save API keys" in caplog.text


def test_load_keys_logs_errors(storage_file, caplog):
    storage_file.write_text("{not json", encoding="utf-8")

    with caplog.at_level("ERROR"):
        APIKeyManager(storage_file)

    assert "Failed to load API keys" in caplog.text


def test_get_key_stats(monkeypatch, manager):
    monkeypatch.setattr("cli_multi_rapid.security.auth.time.time", lambda: 0.0)

    active_key = manager.create_key("user-7")
    revoked_key = manager.create_key("user-7")
    expired_key = manager.create_key("user-7", expiry_days=1)

    assert active_key in manager._keys
    assert manager.revoke_key(revoked_key)

    manager._keys[expired_key]["expires_at"] = -1
    manager._keys[expired_key]["is_active"] = False

    monkeypatch.setattr("cli_multi_rapid.security.auth.time.time", lambda: 1000.0)

    stats = manager.get_key_stats()
    assert stats["total_keys"] == 3
    assert stats["active_keys"] == 1
    assert stats["expired_keys"] == 1
    assert stats["revoked_keys"] == 1


def test_jwt_manager_requires_dependency(monkeypatch):
    monkeypatch.setattr("cli_multi_rapid.security.auth.JWT_AVAILABLE", False)

    with pytest.raises(ImportError):
        JWTManager("secret")


def test_jwt_manager_create_and_verify_token(monkeypatch, jwt_stub):
    base_time = 1_000.0

    def fake_time():
        nonlocal base_time
        current = base_time
        base_time += 1
        return current

    monkeypatch.setattr("cli_multi_rapid.security.auth.time.time", fake_time)

    user = SimpleNamespace(
        id="user-1",
        username="alice",
        roles=[SimpleNamespace(value="developer")],
        permissions=[SimpleNamespace(value="workflow:read")],
    )

    manager = JWTManager("secret", expiry_hours=2)
    token = manager.create_token(user)
    payload = json.loads(token)

    assert payload["user_id"] == user.id
    assert payload["roles"] == ["developer"]
    assert payload["permissions"] == ["workflow:read"]
    assert payload["exp"] == pytest.approx(1000.0 + 2 * 3600, rel=1e-6)
    assert payload["iat"] == pytest.approx(1001.0, rel=1e-6)

    verified = manager.verify_token(token)
    assert verified["username"] == "alice"
    assert manager.decode_token_without_verification(token)["username"] == "alice"


def test_jwt_manager_handles_invalid_tokens(jwt_stub):
    manager = JWTManager("secret")

    assert manager.verify_token("expired") is None
    assert manager.verify_token("invalid") is None
    assert manager.decode_token_without_verification("invalid") is None
