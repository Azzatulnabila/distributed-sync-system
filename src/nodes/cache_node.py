# src/nodes/cache_node.py
import asyncio
import json
from src.utils.lru_cache import SimpleLRU

class CacheNode:
    def __init__(self, node_id, pubsub):
        self.node_id = node_id
        self.cache = SimpleLRU(capacity=200)
        # state map: key -> state M/E/S/I (we will use M,S,I for simplicity)
        self.state = {}
        self.pubsub = pubsub  # aioredis pubsub

    async def write(self, key, value):
        # Update locally
        evicted = self.cache.put(key, value)
        self.state[key] = "M"
        # publish invalidation to other nodes
        channel = "cache_invalidation"
        await self.pubsub.publish(channel, json.dumps({"key": key, "from": self.node_id}))
        return {"ok": True, "evicted": evicted}

    async def read(self, key):
        val = self.cache.get(key)
        if val is None:
            return {"ok": False, "value": None}
        return {"ok": True, "value": val}

    async def handle_invalidation(self, msg):
        try:
            data = json.loads(msg)
            key = data.get("key")
            if key:
                self.cache.invalidate(key)
                self.state[key] = "I"
        except:
            pass
