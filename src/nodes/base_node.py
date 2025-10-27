import asyncio
from aiohttp import web
import aioredis
from src.utils.config import NODE_ID, PORT, REDIS_HOST, REDIS_PORT, NODES
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
        print(f"[{self.node_id}] HTTP server listening on {PORT}")

    async def subscriber(self):
        res = await self.pubsub.subscribe("cache_invalidation")
        ch = res[0]
        while await ch.wait_message():
            msg = await ch.get(encoding="utf-8")
            await self.cache.handle_invalidation(msg)

node_server = NodeServer()

@routes.post("/raft/heartbeat")
async def raft_heartbeat(request):
    data = await request.json()
    return web.json_response(await node_server.raft.handle_heartbeat(data.get("term"), data.get("leader")))

@routes.post("/raft/request_vote")
async def raft_vote(request):
    data = await request.json()
    return web.json_response(await node_server.raft.handle_vote_request(data.get("term"), data.get("candidate")))

@routes.post("/lock/acquire")
async def lock_acquire(request):
    data = await request.json()
    res = await node_server.lock_mgr.acquire(data.get("resource"), node_server.node_id, mode=data.get("mode","exclusive"))
    return web.json_response(res)

@routes.post("/lock/release")
async def lock_release(request):
    data = await request.json()
    res = await node_server.lock_mgr.release(data.get("resource"), node_server.node_id)
    return web.json_response(res)

@routes.post("/queue/produce")
async def queue_produce(request):
    data = await request.json()
    return web.json_response(await node_server.queue.push(data.get("topic","default"), data.get("message","")))

@routes.post("/queue/consume")
async def queue_consume(request):
    data = await request.json()
    return web.json_response(await node_server.queue.pop(data.get("topic","default"), timeout=2))

@routes.post("/cache/write")
async def cache_write(request):
    data = await request.json()
    return web.json_response(await node_server.cache.write(data.get("key"), data.get("value")))

@routes.post("/cache/read")
async def cache_read(request):
    data = await request.json()
    return web.json_response(await node_server.cache.read(data.get("key")))

async def run():
    await node_server.start()

if __name__ == "__main__":
    asyncio.run(run())
