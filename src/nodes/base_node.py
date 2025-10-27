# src/nodes/base_node.py
import asyncio
from aiohttp import web
import aioredis
import os
from src.utils.config import NODE_ID, PORT, REDIS_HOST, REDIS_PORT, NODES
from src.consensus.raft_like import RaftLike
from src.nodes.lock_manager import DistributedLockManager
from src.nodes.queue_node import DistributedQueue
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
        self.raft = RaftLike(on_become_leader=self.on_become_leader)
        self.pubsub_task = None

    async def init_redis(self):
        self.redis = await aioredis.create_redis_pool((REDIS_HOST, REDIS_PORT), minsize=1, maxsize=5)
        self.queue = DistributedQueue(self.redis)
        # pubsub setup: create a separate connection
        self.pubsub = await aioredis.create_redis((REDIS_HOST, REDIS_PORT))
        self.cache = CacheNode(self.node_id, self.pubsub)

    async def on_become_leader(self):
        print(f"[{self.node_id}] I am leader now")

    async def start(self):
        await self.init_redis()
        await self.raft.start()
        # start subscriber
        self.pubsub_task = asyncio.create_task(self.subscriber())
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", PORT)
        await site.start()
        print(f"[{self.node_id}] HTTP server started on port {PORT}")

    async def subscriber(self):
        sub = await self.pubsub.subscribe("cache_invalidation")
        ch = sub[0]
        while await ch.wait_message():
            msg = await ch.get(encoding="utf-8")
            await self.cache.handle_invalidation(msg)

node_server = NodeServer()

# Raft endpoints
@routes.post("/raft/heartbeat")
async def heartbeat(request):
    data = await request.json()
    res = await node_server.raft.handle_heartbeat(data.get("term"), data.get("leader"))
    return web.json_response(res)

@routes.post("/raft/request_vote")
async def request_vote(request):
    data = await request.json()
    res = await node_server.raft.handle_vote_request(data.get("term"), data.get("candidate"))
    return web.json_response(res)

# Lock endpoints
@routes.post("/lock/acquire")
async def lock_acquire(request):
    data = await request.json()
    resource = data.get("resource")
    mode = data.get("mode", "exclusive")
    res = await node_server.lock_mgr.acquire(resource, node_server.node_id, mode=mode)
    return web.json_response(res)

@routes.post("/lock/release")
async def lock_release(request):
    data = await request.json()
    resource = data.get("resource")
    res = await node_server.lock_mgr.release(resource, node_server.node_id)
    return web.json_response(res)

# Queue endpoints
@routes.post("/queue/produce")
async def produce(request):
    data = await request.json()
    topic = data.get("topic", "default")
    message = data.get("message", "")
    res = await node_server.queue.produce(topic, message)
    return web.json_response(res)

@routes.post("/queue/consume")
async def consume(request):
    data = await request.json()
    topic = data.get("topic", "default")
    res = await node_server.queue.consume_from(topic, timeout=2)
    return web.json_response(res)

# Cache endpoints
@routes.post("/cache/write")
async def cache_write(request):
    data = await request.json()
    key = data.get("key")
    value = data.get("value")
    res = await node_server.cache.write(key, value)
    return web.json_response(res)

@routes.post("/cache/read")
async def cache_read(request):
    data = await request.json()
    key = data.get("key")
    res = await node_server.cache.read(key)
    return web.json_response(res)

async def run():
    await node_server.start()

if __name__ == "__main__":
    asyncio.run(run())
