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
    res = client.post("/auth/register", json={"email": "user@example.com", "password": "pass123"})
    token = res.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    yield client, mock_storage
    # get_storage_dep override cleared by client fixture's app.dependency_overrides.clear()


def _upload(client, filename="test.txt", content=b"hello", content_type="text/plain"):
    return client.post(
        "/files/upload",
        files={"file": (filename, io.BytesIO(content), content_type)},
    )


def test_upload_success(auth_client):
    client, storage = auth_client
    res = _upload(client)
    assert res.status_code == 200
    data = res.json()
    assert data["filename"] == "test.txt"
    assert data["size"] == 5
    storage.upload_file.assert_called_once()


def test_upload_file_too_large(auth_client):
    client, storage = auth_client
    # free plan file_size_limit = 100MB; send 101MB
    big = b"x" * (100 * 1024 * 1024 + 1)
    res = _upload(client, content=big)
    assert res.status_code == 400
    assert "too large" in res.json()["detail"].lower()


def test_upload_quota_exceeded(auth_client, db):
    client, storage = auth_client
    # set storage_used to near limit (5GB - 1 byte)
    from app.core.models import User
    user = db.query(User).filter(User.email == "user@example.com").first()
    user.storage_used = 5 * 1024 ** 3 - 4  # only 4 bytes left, send 5
    db.commit()
    res = _upload(client, content=b"hello")  # 5 bytes
    assert res.status_code == 400
    assert "quota" in res.json()["detail"].lower()


def test_list_files_empty(auth_client):
    client, _ = auth_client
    res = client.get("/files/")
    assert res.status_code == 200
    assert res.json() == {"files": [], "total": 0}


def test_list_files_after_upload(auth_client):
    client, _ = auth_client
    _upload(client, filename="a.txt")
    _upload(client, filename="b.txt")
    res = client.get("/files/")
    assert res.status_code == 200
    assert res.json()["total"] == 2


def test_delete_file(auth_client):
    client, storage = auth_client
    upload_res = _upload(client)
    file_id = upload_res.json()["id"]
    res = client.delete(f"/files/{file_id}")
    assert res.status_code == 204
    storage.delete_file.assert_called_once()
    # file no longer in list
    list_res = client.get("/files/")
    assert list_res.json()["total"] == 0


def test_delete_file_not_found(auth_client):
    client, _ = auth_client
    res = client.delete("/files/9999")
    assert res.status_code == 404


def test_download_redirects(auth_client):
    client, storage = auth_client
    upload_res = _upload(client)
    file_id = upload_res.json()["id"]
    res = client.get(f"/files/{file_id}/download", follow_redirects=False)
    assert res.status_code in (302, 307)
    assert "presigned" in res.headers["location"]


def test_download_not_found(auth_client):
    client, _ = auth_client
    res = client.get("/files/9999/download", follow_redirects=False)
    assert res.status_code == 404


def test_upload_requires_auth(client):
    res = _upload(client)
    assert res.status_code == 401
