import pytest_asyncio
import fakeredis.aioredis


@pytest_asyncio.fixture
async def fake_redis(monkeypatch):
    client = fakeredis.aioredis.FakeRedis(decode_responses=True)
    monkeypatch.setattr("app.bot.handlers.get_redis", lambda: client)
    yield client
    await client.flushall()