import asyncio
from src.nodes.lock_manager import DistributedLockManager

def test_acquire_release_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    lm = DistributedLockManager()
    async def run_test():
        r1 = await lm.acquire("res1", "n1")
        assert r1["ok"] is True
        r2 = await lm.acquire("res1", "n2", mode="shared")
        # n2 should fail because exclusive held by n1
        assert r2["ok"] is False or r2.get("reason") in ("timeout","deadlock_detected")
        r3 = await lm.release("res1", "n1")
        assert r3["ok"] is True
    loop.run_until_complete(run_test())
