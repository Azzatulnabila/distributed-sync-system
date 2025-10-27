import asyncio
import time
from collections import defaultdict
from src.utils.metrics import SimpleMetrics

metrics = SimpleMetrics()

class DeadlockDetector:
    def __init__(self):
        self.wait_for = defaultdict(set)

    def add_wait(self, waiter, holder):
        self.wait_for[waiter].add(holder)

    def remove_wait(self, waiter, holder):
        if holder in self.wait_for.get(waiter, set()):
            self.wait_for[waiter].remove(holder)

    def detect_deadlock(self):
        visited = set()
        stack = set()
        def dfs(node):
            visited.add(node)
            stack.add(node)
            for nbr in self.wait_for.get(node, []):
                if nbr not in visited:
                    if dfs(nbr):
                        return True
                elif nbr in stack:
                    return True
            stack.remove(node)
            return False
        for n in list(self.wait_for.keys()):
            if n not in visited:
                if dfs(n):
                    return True
        return False

class DistributedLockManager:
    def __init__(self):
        self.locks = {}
        self.detector = DeadlockDetector()
        self.lock = asyncio.Lock()

    async def acquire(self, resource, node_id, mode="exclusive", timeout=6):
        start = time.time()
        async with self.lock:
            while True:
                entry = self.locks.get(resource)
                if not entry:
                    self.locks[resource] = {"type": mode, "holders": {node_id}}
                    metrics.inc("locks_acquired", 1)
                    return {"ok": True}
                else:
                    if mode == "shared" and entry["type"] == "shared":
                        entry["holders"].add(node_id)
                        metrics.inc("locks_acquired", 1)
                        return {"ok": True}
                    for h in entry["holders"]:
                        self.detector.add_wait(node_id, h)
                    if self.detector.detect_deadlock():
                        for h in entry["holders"]:
                            self.detector.remove_wait(node_id, h)
                        metrics.inc("locks_failed", 1)
                        return {"ok": False, "reason": "deadlock_detected"}
                if (time.time() - start) > timeout:
                    metrics.inc("locks_failed", 1)
                    return {"ok": False, "reason": "timeout"}
                await asyncio.sleep(0.1)

    async def release(self, resource, node_id):
        async with self.lock:
            entry = self.locks.get(resource)
            if not entry:
                return {"ok": False, "reason": "no_lock"}
            if node_id in entry["holders"]:
                entry["holders"].remove(node_id)
                self.detector.wait_for.pop(node_id, None)
                if len(entry["holders"]) == 0:
                    self.locks.pop(resource, None)
                return {"ok": True}
            return {"ok": False, "reason": "not_holder"}
