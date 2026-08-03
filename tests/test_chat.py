def _get_token(client, email="chatuser@example.com"):
    client.post(
        "/api/auth/register",
        json={"name": "Chat User", "email": email, "password": "Secret123"},
    )
    resp = client.post("/api/auth/login", json={"email": email, "password": "Secret123"})
    return resp.json()["access_token"]


def test_chat_requires_auth(client):
    resp = client.post(
        "/api/tutor/chat",
        json={"session_id": "abc123", "message": "Explain photosynthesis"},
    )
    assert resp.status_code == 401


def test_chat_history_empty_for_new_session(client):
    token = _get_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.get("/api/tutor/history/never-used-session", headers=headers)
    assert resp.status_code == 200
    assert resp.json() == []
