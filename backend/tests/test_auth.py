def test_register_success(client):
    res = client.post("/auth/register", json={"email": "test@example.com", "password": "password123"})
    assert res.status_code == 200
    assert "access_token" in res.json()

def test_register_duplicate_email(client):
    client.post("/auth/register", json={"email": "test@example.com", "password": "pass"})
    res = client.post("/auth/register", json={"email": "test@example.com", "password": "pass"})
    assert res.status_code == 400

def test_login_success(client):
    client.post("/auth/register", json={"email": "test@example.com", "password": "password123"})
    res = client.post("/auth/login", json={"email": "test@example.com", "password": "password123"})
    assert res.status_code == 200
    assert "access_token" in res.json()

def test_login_wrong_password(client):
    client.post("/auth/register", json={"email": "test@example.com", "password": "password123"})
    res = client.post("/auth/login", json={"email": "test@example.com", "password": "wrong"})
    assert res.status_code == 401

def test_me_requires_auth(client):
    res = client.get("/auth/me")
    assert res.status_code == 401

def test_me_returns_user(client):
    res = client.post("/auth/register", json={"email": "test@example.com", "password": "pass"})
    token = res.json()["access_token"]
    res = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["email"] == "test@example.com"
    assert res.json()["plan_name"] == "free"
