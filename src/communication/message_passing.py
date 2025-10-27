import aiohttp
import asyncio
import json
from typing import Optional

async def post_json(host: str, port: int, path: str, payload: dict, timeout: float = 3.0, retries: int = 2):
    """POST JSON helper with simple retry/backoff. Returns dict or {'error': ...}."""
    url = f"http://{host}:{port}{path}"
    backoff = 0.5
    for attempt in range(retries + 1):
        try:
            async with aiohttp.ClientSession() as sess:
                async with sess.post(url, json=payload, timeout=timeout) as resp:
                    text = await resp.text()
                    try:
                        return json.loads(text)
                    except Exception:
                        return {"status": resp.status, "text": text}
        except Exception as e:
            if attempt == retries:
                return {"error": str(e)}
            await asyncio.sleep(backoff)
            backoff *= 2

async def get_json(host: str, port: int, path: str, timeout: float = 3.0):
    url = f"http://{host}:{port}{path}"
    try:
        async with aiohttp.ClientSession() as sess:
            async with sess.get(url, timeout=timeout) as resp:
                text = await resp.text()
                try:
                    return json.loads(text)
                except Exception:
                    return {"status": resp.status, "text": text}
    except Exception as e:
        return {"error": str(e)}
