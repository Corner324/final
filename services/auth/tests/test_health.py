import pytest
from httpx import AsyncClient, ASGITransport
import sys, pathlib
import os

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")

from main import app  # type: ignore
import sqlalchemy.ext.asyncio as _sa_async

_sa_async.create_async_engine = lambda *a, **k: None


@pytest.mark.asyncio
async def test_health_ok():
    """/health должен возвращать 200 и {'status': 'ok'}"""
    transport = ASGITransport(app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
