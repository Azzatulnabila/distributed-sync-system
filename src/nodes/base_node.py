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
        self.redis = await aioredis.from_url(f"redis://{REDIS_HOST}", decode_responses=True)
        self.queue = PersistentQueue(self.redis)
        self.cache = CacheNode(self.node_id, self.redis)

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
        pubsub = self.redis.pubsub()
        await pubsub.subscribe("cache_invalidation")
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message:
                await self.cache.handle_invalidation(message["data"])
            await asyncio.sleep(0.01)

