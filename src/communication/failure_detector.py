import asyncio
import time
from typing import Dict

class SimpleFailureDetector:
    """
    Heartbeat-based lightweight failure detector.
    Maintains last heartbeat timestamp per peer and provides is_alive check.
    """
    def __init__(self, timeout_seconds: float = 8.0):
        self.last_seen: Dict[str, float] = {}
        self.timeout = timeout_seconds

    def heartbeat(self, node_id: str):
        self.last_seen[node_id] = time.time()

    def is_alive(self, node_id: str) -> bool:
        t = self.last_seen.get(node_id)
        if t is None:
            return False
        return (time.time() - t) < self.timeout

    async def monitor_loop(self, callback_down, interval: float = 3.0):
        """
        Periodically check peers; if a peer timed out, call callback_down(node_id).
        callback_down must be async function.
        """
        while True:
            now = time.time()
            for node_id, ts in list(self.last_seen.items()):
                if (now - ts) > self.timeout:
                    try:
                        await callback_down(node_id)
                    except Exception:
                        pass
            await asyncio.sleep(interval)
