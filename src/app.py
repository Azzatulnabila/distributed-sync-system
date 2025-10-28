# src/app.py
import asyncio
from fastapi import FastAPI, Request
from src.nodes.base_node import Node

import uvicorn
import os

app = FastAPI()
node_id = os.getenv("NODE_ID", "node1")
all_nodes = os.getenv("NODES", "node1,node2,node3").split(",")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")

node = Node(node_id=node_id, nodes=all_nodes, redis_host=REDIS_HOST)

# ======= Lock Routes =======
@app.post("/lock/acquire")
async def acquire_lock(req: Request):
    data = await req.json()
    result = await node.lock_acquire(data["resource"], data["mode"])
    return {"result": result}

@app.post("/lock/release")
async def release_lock(req: Request):
    data = await req.json()
    result = await node.lock_release(data["resource"])
    return {"result": result}

# ======= Queue Routes =======
@app.post("/queue/produce")
async def queue_produce(req: Request):
    data = await req.json()
    result = await node.queue_produce(data["topic"], data["message"])
    return {"result": result}

@app.post("/queue/consume")
async def queue_consume(req: Request):
    data = await req.json()
    result = await node.queue_consume(data["topic"])
    return {"result": result}

# ======= Cache Routes =======
@app.post("/cache/write")
async def cache_write(req: Request):
    data = await req.json()
    result = await node.cache_write(data["key"], data["value"])
    return {"result": result}

@app.get("/cache/read")
async def cache_read(key: str):
    value = await node.cache_read(key)
    return {"value": value}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
