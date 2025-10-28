import asyncio
import json
from src.utils.metrics import LRUCachePolicy, SimpleMetrics

metrics = SimpleMetrics()

class CacheNode:
    def __init__(self, node_id, pubsub):
        self.node_id = node_id
        self.cache = LRUCachePolicy(capacity=150)
        self.state = {}
        self.pubsub = pubsub

    async def write(self, key, value):
        try:
        evicted = self.cache.put(key, value)
        self.state[key] = "M"
        await self.pubsub.publish("cache_invalidation", json.dumps({"key": key, "from": self.node_id}))
        return {"ok": True, "evicted": evicted}
        except Exception as e:
        return {"ok": False, "error": str(e)}

    async def read(self, key):
        val = self.cache.get(key)
        if val is None:
            metrics.inc("cache_miss", 1)
            return {"ok": False, "value": None}
        metrics.inc("cache_hit", 1)
        return {"ok": True, "value": val}

    async def handle_invalidation(self, msg):
        try:
            data = json.loads(msg)
            key = data.get("key")
            if key:
                self.cache.invalidate(key)
                self.state[key] = "I"
        except Exception:
            pass
