import asyncio
import httpx
import hashlib

class HTTPProbe:
    def __init__(self, urls, concurrency=10, headers=None, timeout=10):
        self.urls = urls
        self.concurrency = concurrency
        self.headers = headers or {}
        self.timeout = timeout

    async def fetch(self, client, url):
        try:
            response = await client.get(url, timeout=self.timeout)
            content_hash = hashlib.md5(response.content).hexdigest()
            return {
                "url": url,
                "status_code": response.status_code,
                "content_length": len(response.content),
                "content_type": response.headers.get("Content-Type", ""),
                "hash": content_hash,
            }
        except Exception as e:
            return {"url": url, "error": str(e)}

    async def run(self):
        async with httpx.AsyncClient(headers=self.headers) as client:
            tasks = [self.fetch(client, url) for url in self.urls]
            return await asyncio.gather(*tasks)
