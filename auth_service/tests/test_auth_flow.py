import pytest


@pytest.mark.asyncio
async def test_full_flow(client):
    r = await client.post("/auth/register", json={"email": "a@b.com", "password": "secret1"})
    assert r.status_code == 201

    r = await client.post(
        "/auth/login",
        data={"username": "a@b.com", "password": "secret1"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert r.status_code == 200
    token = r.json()["access_token"]

    r = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["email"] == "a@b.com"


@pytest.mark.asyncio
async def test_duplicate_register(client):
    await client.post("/auth/register", json={"email": "a@b.com", "password": "secret1"})
    r = await client.post("/auth/register", json={"email": "a@b.com", "password": "secret1"})
    assert r.status_code == 409


@pytest.mark.asyncio
async def test_wrong_password(client):
    await client.post("/auth/register", json={"email": "a@b.com", "password": "secret1"})
    r = await client.post(
        "/auth/login",
        data={"username": "a@b.com", "password": "wrong"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_me_requires_token(client):
    r = await client.get("/auth/me")
    assert r.status_code == 401

@pytest.mark.asyncio
async def test_me_invalid_token(client):
    r = await client.get("/auth/me", headers={"Authorization": "Bearer not-a-real-token"})
    assert r.status_code == 401