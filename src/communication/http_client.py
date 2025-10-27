# src/communication/http_client.py
import aiohttp
import asyncio
import json

async def post(host, port, path, data=None, timeout=5):
    url = f"http://{host}:{port}{path}"
    try:
        async with aiohttp.ClientSession() as sess:
            async with sess.post(url, json=data or {}, timeout=timeout) as resp:
                return await resp.json()
    except Exception as e:
        return {"error": str(e)}
