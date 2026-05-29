from __future__ import annotations

import json
import os
from datetime import date, datetime
from pathlib import Path

from dotenv import load_dotenv
from redis import Redis

BASE_DIR = Path(__file__).resolve().parents[3]
load_dotenv(BASE_DIR / ".env")

DEFAULT_REDIS_URL = "redis://localhost:6379/0"
REDIS_URL = os.getenv("REDIS_URL", DEFAULT_REDIS_URL)

CACHE_EXPIRE_SECONDS = 300


class CacheService:
    def __init__(self, url: str | None = None) -> None:
        self.client = Redis.from_url(url or REDIS_URL, decode_responses=True)

    @staticmethod
    def _json_serializer(value: object) -> str:
        if isinstance(value, (datetime, date)):
            return value.isoformat()
        raise TypeError(f"Object of type {type(value)} is not JSON serializable")

    def get_json(self, key: str) -> dict | None:
        raw = self.client.get(key)
        if raw is None:
            return None
        return json.loads(raw)

    def set_json(self, key: str, value: dict, expire: int | None = None) -> None:
        payload = json.dumps(value, default=self._json_serializer)
        self.client.set(key, payload, ex=expire)

    def delete(self, key: str) -> None:
        self.client.delete(key)

    @staticmethod
    def task_list_cache_key(user_id: int) -> str:
        return f"tasks:user:{user_id}"

    def get_task_list(self, user_id: int) -> dict | None:
        return self.get_json(self.task_list_cache_key(user_id))

    def set_task_list(self, user_id: int, data: dict, expire: int = CACHE_EXPIRE_SECONDS) -> None:
        self.set_json(self.task_list_cache_key(user_id), data, expire=expire)

    def delete_task_list(self, user_id: int) -> None:
        self.delete(self.task_list_cache_key(user_id))


cache_service = CacheService()
