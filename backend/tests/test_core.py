import os
import pytest
from app.core.config import Settings

def test_settings_loads_from_env():
    os.environ["DATABASE_URL"] = "postgresql://test:test@localhost/test"
    os.environ["SECRET_KEY"] = "test-secret"
    os.environ["SPACES_KEY"] = "key"
    os.environ["SPACES_SECRET"] = "secret"
    os.environ["SPACES_BUCKET"] = "bucket"
    os.environ["SPACES_REGION"] = "nyc3"
    os.environ["SPACES_ENDPOINT"] = "https://nyc3.digitaloceanspaces.com"

    settings = Settings()
    assert settings.DATABASE_URL == "postgresql://test:test@localhost/test"
    assert settings.SECRET_KEY == "test-secret"
