import asyncio
import aioredis
from aiohttp import web
from src.utils.config import NODE_ID, PORT, REDIS_HOST, REDIS_PORT
from src.consensus.raft import RaftNode
from src.nodes.lock_manager import DistributedLockManager
from src.nodes.queue_node import PersistentQueue
from src.nodes.cache_node import CacheNode

routes = web.RouteTableDef()

class NodeServer:
    def __init__(self):
        self.node_id = NODE_ID
        self.app = web.Application()
        self.app.add_routes(routes)
        self.lock_mgr = DistributedLockManager()
        self.redis = None
        self.queue = None
        self.cache = None
        self.raft = RaftNode(on_become_leader=self.on_become_leader)
        self.pubsub = None

    async def init_redis(self):
        self.redis = await aioredis.create_redis_pool((REDIS_HOST, REDIS_PORT), minsize=1, maxsize=5)
        self.queue = PersistentQueue(self.redis)
        self.pubsub = await aioredis.create_redis((REDIS_HOST, REDIS_PORT))
        self.cache = CacheNode(self.node_id, self.pubsub)

    async def on_become_leader(self):
        print(f"[{self.node_id}] became leader")

    async def start(self):
        await self.init_redis()
        await self.raft.start()
        asyncio.create_task(self.subscriber())
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", PORT)
        await site.start()
        print(f"[{self.node_id}] HTTP server listening on {PORT}", flush=True)
        while True:
            await asyncio.sleep(3600)

    async def subscriber(self):
        res = await self.pubsub.subscribe("cache_invalidation")
        ch = res[0]
        while await ch.wait_message():
            msg = await ch.get(encoding="utf-8")
            await self.cache.handle_invalidation(msg)
