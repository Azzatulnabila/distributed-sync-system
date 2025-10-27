# Deployment Guide - Docker Online (Play-with-Docker)

## Prasyarat
- Akun Docker Hub (untuk Play-with-Docker login)
- Repo GitHub: https://github.com/Azzatulnabila/distributed-sync-system

## Langkah cepat (Play-with-Docker)
1. Buka https://labs.play-with-docker.com/ → Login
2. Start new session → Add new instance (minimal 1)
3. Di terminal instance:
   ```bash
   git clone https://github.com/Azzatulnabila/distributed-sync-system.git
   cd distributed-sync-system/docker
   docker-compose up --build

4. Jika docker-compose bermasalah di PWD, gunakan:
   ```bash
   docker build -t ds-node -f Dockerfile.node ..
   docker run -d --name redis redis:6-alpine
   docker run -d --name node1 --env NODE_ID=node1 --env NODES=node1,node2,node3 --env REDIS_HOST=redis ds-node
   docker run -d --name node2 --env NODE_ID=node2 --env NODES=node1,node2,node3 --env REDIS_HOST=redis ds-node
   docker run -d --name node3 --env NODE_ID=node3 --env NODES=node1,node2,node3 --env REDIS_HOST=redis ds-node

5. Cek logs:
   ```bash
   docker ps
   docker logs -f node1
   docker logs -f node2

6. Demo commands (dijalankan di container dengan akses network ke service):
   ```bash
   curl -X POST http://node1:5000/lock/acquire -H "Content-Type: application/json" -d '{"resource":"r1","mode":"exclusive"}'
   curl -X POST http://node2:5000/queue/produce -H "Content-Type: application/json" -d '{"topic":"t","message":"hello"}'
   curl -X POST http://node3:5000/queue/consume -H "Content-Type: application/json" -d '{"topic":"t"}'
   curl -X POST http://node2:5000/cache/write -H "Content-Type: application/json" -d '{"key":"k1","value":"v1"}'

7. Screenshot logs & docker ps untuk bukti.

Catatan
- Jika environment Play-with-Docker menyediakan host mapping berbeda, sesuaikan alamat host di curl.
- Simpan screenshot dan rekam layar untuk video demonstrasi.


---

# 📁 benchmarks/load_test_scenarios.py
(simple asyncio load simulator — versi kamu)
```python
# benchmarks/load_test_scenarios.py
"""
Simple load generator to simulate producers and consumers via HTTP endpoints.
Not a production load-test tool, but useful for demo and quick benchmarking.
"""
import asyncio
import aiohttp
import time
import random

async def produce_one(session, url, topic, msg):
    try:
        async with session.post(url, json={"topic": topic, "message": msg}) as resp:
            return await resp.text()
    except Exception as e:
        return str(e)

async def run_producers(base_url, n=50, concurrency=5):
    sem = asyncio.Semaphore(concurrency)
    async with aiohttp.ClientSession() as sess:
        async def worker(i):
            async with sem:
                return await produce_one(sess, f"{base_url}/queue/produce", "load", f"msg-{i}")
        tasks = [asyncio.create_task(worker(i)) for i in range(n)]
        results = await asyncio.gather(*tasks)
        return results

if __name__ == "__main__":
    base = "http://localhost:5000"  # adjust per node when testing in docker online
    start = time.time()
    res = asyncio.run(run_producers(base, n=200, concurrency=20))
    print("Produced:", len(res))
    print("Elapsed:", time.time() - start)





