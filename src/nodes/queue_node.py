import aioredis
import asyncio
from src.utils.config import REDIS_HOST, REDIS_PORT, QUEUE_NAMESPACE
from typing import Optional

class PersistentQueue:
    def __init__(self, redis_pool):
        self.redis = redis_pool

    async def push(self, topic: str, message: str):
        key = f"{QUEUE_NAMESPACE}:{topic}"
        await self.redis.rpush(key, message)
        return {"ok": True}

    async def pop(self, topic: str, timeout: int = 2):
        key = f"{QUEUE_NAMESPACE}:{topic}"
        res = await self.redis.blpop(key, timeout=timeout)
        if res:
            return {"ok": True, "message": res[1].decode()}
        return {"ok": False, "message": None}
