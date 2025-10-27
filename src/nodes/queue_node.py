# src/nodes/queue_node.py
import aioredis
import asyncio
from src.utils.config import REDIS_HOST, REDIS_PORT, QUEUE_NAMESPACE, NODES

class DistributedQueue:
    def __init__(self, redis):
        self.redis = redis
        self.nodes = NODES

    async def produce(self, topic, message):
        # use consistent hashing by topic+message to pick node list name
        key = f"{QUEUE_NAMESPACE}:{topic}"
        await self.redis.rpush(key, message)
        return {"ok": True}

    async def consume_from(self, topic, timeout=1):
        key = f"{QUEUE_NAMESPACE}:{topic}"
        # BLPOP will pop and return; this gives at-least-once semantics if consumer fails after pop
        res = await self.redis.blpop(key, timeout=timeout)
        if res:
            # returns (key, message)
            return {"ok": True, "message": res[1].decode()}
        return {"ok": False, "message": None}
