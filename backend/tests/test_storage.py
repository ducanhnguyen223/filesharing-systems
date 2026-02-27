import io
import os
import pytest
import boto3
from moto import mock_aws
from app.files.storage import StorageClient


FAKE_SETTINGS_ENV = {
    "DATABASE_URL": "sqlite:///./test.db",
    "SECRET_KEY": "test-secret",
    "SPACES_KEY": "test-key",
    "SPACES_SECRET": "test-secret-key",
    "SPACES_BUCKET": "test-bucket",
    "SPACES_REGION": "us-east-1",
    "SPACES_ENDPOINT": "http://localhost:9000",
}


class FakeSettings:
    SPACES_KEY = "test-key"
    SPACES_SECRET = "test-secret-key"
    SPACES_BUCKET = "test-bucket"
    SPACES_REGION = "us-east-1"
    SPACES_ENDPOINT = None  # moto intercepts, no real endpoint needed


@pytest.fixture
def storage(monkeypatch):
    with mock_aws():
        # moto requires no custom endpoint_url to intercept properly
        client = StorageClient(settings=FakeSettings())
        yield client


def test_ensure_bucket_creates_if_not_exists(storage):
    s3 = boto3.client("s3", region_name="us-east-1")
    buckets = [b["Name"] for b in s3.list_buckets()["Buckets"]]
    assert "test-bucket" in buckets


def test_upload_file(storage):
    data = b"hello world"
    key = storage.upload_file(io.BytesIO(data), "test/hello.txt", "text/plain")
    assert key == "test/hello.txt"


def test_download_file(storage):
    data = b"download me"
    storage.upload_file(io.BytesIO(data), "test/dl.txt")
    body = storage.download_file("test/dl.txt")
    assert body.read() == data


def test_delete_file(storage):
    storage.upload_file(io.BytesIO(b"bye"), "test/del.txt")
    storage.delete_file("test/del.txt")
    s3 = boto3.client("s3", region_name="us-east-1")
    response = s3.list_objects_v2(Bucket="test-bucket", Prefix="test/del.txt")
    assert response.get("KeyCount", 0) == 0


def test_get_presigned_url(storage):
    storage.upload_file(io.BytesIO(b"presign"), "test/presign.txt")
    url = storage.get_presigned_url("test/presign.txt", expires=60)
    assert "test/presign.txt" in url
    assert "X-Amz-Expires=60" in url or "Expires" in url
