def test_register_and_login(client):
    resp = client.post(
        "/api/auth/register",
        json={"name": "Test User", "email": "test1@example.com", "password": "Secret123"},
    )
    assert resp.status_code == 201
    assert "access_token" in resp.json()

    resp = client.post(
        "/api/auth/login",
        json={"email": "test1@example.com", "password": "Secret123"},
    )
    assert resp.status_code == 200
    token = resp.json()["access_token"]

    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["email"] == "test1@example.com"


def test_login_wrong_password(client):
    client.post(
        "/api/auth/register",
        json={"name": "User2", "email": "test2@example.com", "password": "Secret123"},
    )
    resp = client.post(
        "/api/auth/login",
        json={"email": "test2@example.com", "password": "WrongPass"},
    )
    assert resp.status_code == 401


def test_protected_route_requires_token(client):
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401
