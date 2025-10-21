from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field


@dataclass
class Connection:
    websocket: any
    subscriptions: set[str] = field(default_factory=set)
    user_id: str | None = None


class ConnectionManager:
    """In-memory WebSocket connection manager used for tests."""

    def __init__(self, redis_url: str | None = None) -> None:
        self.redis_url = redis_url
        self.connections: dict[str, Connection] = {}

    async def connect(self, websocket) -> str:
        await websocket.accept()
        client_id = str(uuid.uuid4())
        self.connections[client_id] = Connection(websocket=websocket)
        return client_id

    async def disconnect(self, client_id: str) -> None:
        self.connections.pop(client_id, None)

    async def subscribe(self, client_id: str, topics: list[str]) -> bool:
        conn = self.connections.get(client_id)
        if not conn:
            return False
        for t in topics:
            conn.subscriptions.add(str(t))
        return True

    async def unsubscribe(self, client_id: str, topics: list[str]) -> None:
        conn = self.connections.get(client_id)
        if not conn:
            return
        for t in topics:
            conn.subscriptions.discard(str(t))

    async def broadcast_to_topic(self, topic: str, message: dict) -> int:
        payload = json.dumps(message)
        sent = 0
        for conn in self.connections.values():
            if topic in conn.subscriptions:
                await conn.websocket.send_text(payload)
                sent += 1
        return sent

    async def broadcast_to_all(self, message: dict) -> int:
        payload = json.dumps(message)
        sent = 0
        for conn in self.connections.values():
            await conn.websocket.send_text(payload)
            sent += 1
        return sent

    def get_connection_stats(self) -> dict:
        topics: set[str] = set()
        by_topic: dict[str, int] = {}
        for conn in self.connections.values():
            for t in conn.subscriptions:
                topics.add(t)
                by_topic[t] = by_topic.get(t, 0) + 1
        return {
            "total_connections": len(self.connections),
            "unique_users": len({c.user_id for c in self.connections.values() if c.user_id}),
            "topics": sorted(topics),
            "connections_by_topic": by_topic,
        }

