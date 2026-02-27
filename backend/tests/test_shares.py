import io
import pytest
from unittest.mock import MagicMock
from app.files.router import get_storage_dep
from app.files.storage import StorageClient


@pytest.fixture
def mock_storage():
    storage = MagicMock(spec=StorageClient)
    storage.upload_file.return_value = "1/some-uuid/test.txt"
    storage.get_presigned_url.return_value = "https://storage.example.com/presigned"
    return storage


@pytest.fixture
def auth_client(client, mock_storage):
    from app.main import app
    app.dependency_overrides[get_storage_dep] = lambda: mock_storage
    res = client.post("/auth/register", json={"email": "owner@example.com", "password": "pass123"})
    token = res.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    yield client, mock_storage


@pytest.fixture
def uploaded_file(auth_client):
    client, _ = auth_client
    res = client.post(
        "/files/upload",
        files={"file": ("doc.txt", io.BytesIO(b"content"), "text/plain")},
    )
    return res.json()


def test_create_share(auth_client, uploaded_file):
    client, _ = auth_client
    res = client.post("/shares/", json={"file_id": uploaded_file["id"]})
    assert res.status_code == 200
    data = res.json()
    assert "token" in data
    assert "share_url" in data
    assert data["token"] in data["share_url"]


def test_create_share_file_not_found(auth_client):
    client, _ = auth_client
    res = client.post("/shares/", json={"file_id": 9999})
    assert res.status_code == 404


def test_public_download_redirects(auth_client, uploaded_file):
    client, _ = auth_client
    share_res = client.post("/shares/", json={"file_id": uploaded_file["id"]})
    token = share_res.json()["token"]
    # public endpoint — no auth header needed
    client.headers.pop("Authorization", None)
    res = client.get(f"/shares/{token}", follow_redirects=False)
    assert res.status_code in (302, 307)
    assert "presigned" in res.headers["location"]


def test_public_download_invalid_token(client, mock_storage):
    from app.main import app
    app.dependency_overrides[get_storage_dep] = lambda: mock_storage
    res = client.get("/shares/invalid-token-xyz", follow_redirects=False)
    assert res.status_code == 404


def test_delete_share(auth_client, uploaded_file):
    client, _ = auth_client
    share_res = client.post("/shares/", json={"file_id": uploaded_file["id"]})
    share_id = share_res.json()["id"]
    res = client.delete(f"/shares/{share_id}")
    assert res.status_code == 204
    # token should no longer work
    token = share_res.json()["token"]
    dl = client.get(f"/shares/{token}", follow_redirects=False)
    assert dl.status_code == 404


def test_delete_share_other_user(client, mock_storage, uploaded_file, auth_client):
    owner_client, _ = auth_client
    share_res = owner_client.post("/shares/", json={"file_id": uploaded_file["id"]})
    share_id = share_res.json()["id"]

    # register second user
    from app.main import app
    app.dependency_overrides[get_storage_dep] = lambda: mock_storage
    client.post("/auth/register", json={"email": "other@example.com", "password": "pass"})
    login_res = client.post("/auth/login", json={"email": "other@example.com", "password": "pass"})
    other_token = login_res.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {other_token}"})

    res = client.delete(f"/shares/{share_id}")
    assert res.status_code == 403


def test_create_share_requires_auth(client, mock_storage):
    from app.main import app
    app.dependency_overrides[get_storage_dep] = lambda: mock_storage
    # no auth header — plain client
    res = client.post("/shares/", json={"file_id": 1})
    assert res.status_code == 401
