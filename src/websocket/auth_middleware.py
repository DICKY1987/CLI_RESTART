from __future__ import annotations

import base64
import json
import secrets


class WebSocketAuthMiddleware:
    """Minimal in-memory auth helper for tests.

    Provides token, API key, and session helpers without external deps.
    """

    def __init__(self, secret_key: str, redis_url: str | None = None) -> None:
        self.secret_key = secret_key
        self.redis_url = redis_url
        self._api_keys: dict[str, dict] = {}
        self._sessions: dict[str, dict] = {}

    def generate_token(self, user_id: str, username: str, roles: list[str], permissions: list[str]) -> str:
        payload = {
            "user_id": user_id,
            "username": username,
            "roles": roles,
            "permissions": permissions,
        }
        raw = json.dumps(payload, separators=(",", ":"))
        return base64.urlsafe_b64encode(raw.encode("utf-8")).decode("ascii")

    async def authenticate_token(self, token: str) -> dict | None:
        try:
            raw = base64.urlsafe_b64decode(token.encode("ascii")).decode("utf-8")
            data = json.loads(raw)
            return data if isinstance(data, dict) and "user_id" in data else None
        except Exception:
            return None

    async def create_api_key(self, user_id: str, username: str, roles: list[str], permissions: list[str]) -> str:
        key = secrets.token_urlsafe(24)
        self._api_keys[key] = {
            "user_id": user_id,
            "username": username,
            "roles": roles,
            "permissions": permissions,
        }
        return key

    async def authenticate_api_key(self, api_key: str) -> dict | None:
        return self._api_keys.get(api_key)

    async def create_session(self, user_id: str, username: str, roles: list[str], permissions: list[str]) -> str:
        session_id = secrets.token_urlsafe(24)
        self._sessions[session_id] = {
            "user_id": user_id,
            "username": username,
            "roles": roles,
            "permissions": permissions,
        }
        return session_id

    async def authenticate_session(self, session_id: str) -> dict | None:
        return self._sessions.get(session_id)

    def check_permission(self, user_info: dict, permission: str) -> bool:
        # Admin role has all permissions
        if "admin" in (user_info.get("roles") or []):
            return True
        return permission in (user_info.get("permissions") or [])

    def check_role(self, user_info: dict, role: str) -> bool:
        return role in (user_info.get("roles") or [])

