import pytest
from httpx import AsyncClient, ASGITransport
import sys, pathlib, os
from datetime import datetime

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")

from main import app  # type: ignore

import sqlalchemy.ext.asyncio as _sa_async
_sa_async.create_async_engine = lambda *a, **k: None  # type: ignore


@pytest.mark.asyncio
async def test_list_teams_empty(monkeypatch):
    """GET /teams должен возвращать пустой список, если команд нет."""

    async def fake_get_teams(db, skip=0, limit=100):
        return []

    monkeypatch.setattr("crud.team.get_teams", fake_get_teams)

    transport = ASGITransport(app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/teams")

    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_get_team_not_found(monkeypatch):
    """GET /teams/{id} должен вернуть 404, если команда не найдена."""

    async def fake_get_team_by_id(db, team_id):
        return None

    monkeypatch.setattr("crud.team.get_team_by_id", fake_get_team_by_id)

    transport = ASGITransport(app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/teams/999")

    assert resp.status_code == 404
    assert resp.json()["detail"] == "Команда не найдена"


@pytest.mark.asyncio
async def test_create_team(monkeypatch):
    """POST /teams должен создавать команду и отдавать 201."""

    async def fake_create_team(db, team_in):
        return {
            "id": 1,
            "name": team_in.name,
            "code": team_in.code,
            "created_at": datetime.utcnow(),
        }

    monkeypatch.setattr("crud.team.create_team", fake_create_team)

    transport = ASGITransport(app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.post("/teams/", json={"name": "Team A", "code": "TA"})

    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Team A"
    assert data["code"] == "TA" 