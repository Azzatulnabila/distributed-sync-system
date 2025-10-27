"""
Benchmark Scenarios for Distributed Sync System
Author: Azzatul Nabila
Description:
Simulasi sederhana untuk mengukur performa sistem terdistribusi
pada operasi lock, queue, dan cache.
"""

import asyncio
import aiohttp
import time
import statistics

BASE_URLS = ["http://localhost:5000", "http://localhost:5001", "http://localhost:5002"]

async def measure_latency(session, url, payload):
    start = time.time()
    try:
        async with session.post(url, json=payload) as resp:
            await resp.text()
            return time.time() - start
    except Exception:
        return None

async def run_scenario():
    async with aiohttp.ClientSession() as session:
        latencies = []

        print("\n[🔒] Testing Lock Acquire/Release latency...")
        for node in BASE_URLS:
            lock_time = await measure_latency(session, f"{node}/lock/acquire", {"resource": "test", "mode": "exclusive"})
            if lock_time:
                latencies.append(lock_time)
                await session.post(f"{node}/lock/release", {"resource": "test"})

        print("\n[📦] Testing Queue Produce/Consume throughput...")
        for node in BASE_URLS:
            await session.post(f"{node}/queue/produce", {"topic": "bench", "message": "ping"})
            consume_time = await measure_latency(session, f"{node}/queue/consume", {"topic": "bench"})
            if consume_time:
                latencies.append(consume_time)

        print("\n[🧠] Testing Cache Write/Read response time...")
        for node in BASE_URLS:
            await session.post(f"{node}/cache/write", {"key": "k1", "value": "v1"})
            read_time = await measure_latency(session, f"{node}/cache/read", {"key": "k1"})
            if read_time:
                latencies.append(read_time)

        avg_latency = statistics.mean(latencies) * 1000
        print(f"\n📊 Rata-rata latency: {avg_latency:.2f} ms untuk {len(latencies)} operasi.")
        print("✅ Benchmark selesai.\n")

if __name__ == "__main__":
    asyncio.run(run_scenario())
