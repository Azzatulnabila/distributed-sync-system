# src/app.py
import asyncio
from fastapi import FastAPI, Request
from src.nodes.base_node import NodeServer  
import os

app = FastAPI()

# Config environment
node_id = os.getenv("NODE_ID", "node1")
all_nodes = os.getenv("NODES", "node1,node2,node3").split(",")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")

# Instantiate NodeServer
node = NodeServer()

# ===== Startup Event =====
@app.on_event("startup")
async def startup_event():
    # Jalankan NodeServer di background
    asyncio.create_task(node.start())
    print(f"[{node.node_id}] NodeServer starting in background...")

# ===== Lock Routes =====
@app.post("/lock/acquire")
async def acquire_lock(req: Request):
    data = await req.json()
    res = await node.lock_mgr.acquire(
        data.get("resource"),
        node.node_id,
        mode=data.get("mode", "exclusive")
    )
    return {"result": res}

@app.post("/lock/release")
async def release_lock(req: Request):
    data = await req.json()
    res = await node.lock_mgr.release(data.get("resource"), node.node_id)
    return {"result": res}

# ===== Queue Routes =====
@app.post("/queue/produce")
async def queue_produce(req: Request):
    data = await req.json()
    res = await node.queue.push(data.get("topic", "default"), data.get("message", ""))
    return {"result": res}

@app.post("/queue/consume")
async def queue_consume(req: Request):
    data = await req.json()
    res = await node.queue.pop(data.get("topic", "default"), timeout=2)
    return {"result": res}

# ===== Cache Routes =====
@app.post("/cache/write")
async def cache_write(req: Request):
    data = await req.json()
    res = await node.cache.write(data.get("key"), data.get("value"))
    return {"result": res}

@app.post("/cache/read")
async def cache_read(req: Request):
    data = await req.json()
    key = data.get("key")
    value = await node.cache.read(key)
    return {"value": value}


