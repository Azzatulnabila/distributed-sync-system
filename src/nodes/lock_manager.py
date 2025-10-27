# src/nodes/lock_manager.py
import asyncio
import time
from collections import defaultdict

class DeadlockDetector:
    def __init__(self):
        # wait_for: node -> set(nodes it waits for)
        self.wait_for = defaultdict(set)

    def add_wait(self, waiter, holder):
        self.wait_for[waiter].add(holder)

    def remove_wait(self, waiter, holder):
        if holder in self.wait_for.get(waiter, set()):
            self.wait_for[waiter].remove(holder)

    def detect_deadlock(self):
        # detect cycle in wait_for graph
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
        # resource -> {"type": "shared"/"exclusive", "holders": set()}
        self.locks = {}
        self.detector = DeadlockDetector()
        self.lock = asyncio.Lock()

    async def acquire(self, resource, node_id, mode="exclusive", timeout=5):
        async with self.lock:
            start = time.time()
            while True:
                entry = self.locks.get(resource)
                if not entry:
                    # grant
                    self.locks[resource] = {"type": mode, "holders": {node_id}}
                    return {"ok": True}
                else:
                    # if shared request and existing are shared -> allow multiple
                    if mode == "shared" and entry["type"] == "shared":
                        entry["holders"].add(node_id)
                        return {"ok": True}
                    # otherwise, wait
                    # add to wait-for graph: waiter waits for current holders
                    for h in entry["holders"]:
                        self.detector.add_wait(node_id, h)
                    if self.detector.detect_deadlock():
                        # simple resolution: reject request
                        # cleanup wait-for
                        for h in entry["holders"]:
                            self.detector.remove_wait(node_id, h)
                        return {"ok": False, "reason": "deadlock_detected"}
                if time.time() - start > timeout:
                    return {"ok": False, "reason": "timeout"}
                await asyncio.sleep(0.2)

    async def release(self, resource, node_id):
        async with self.lock:
            entry = self.locks.get(resource)
            if not entry:
                return {"ok": False, "reason": "no_lock"}
            if node_id in entry["holders"]:
                entry["holders"].remove(node_id)
                # cleanup wait-for edges
                self.detector.wait_for.pop(node_id, None)
                if len(entry["holders"]) == 0:
                    self.locks.pop(resource, None)
                return {"ok": True}
            return {"ok": False, "reason": "not_holder"}
