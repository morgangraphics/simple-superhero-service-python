import pytest
from fastapi.testclient import TestClient
from service import create_app
from service.config import Settings, get_settings
from service.utils.error import InvalidUsage


def test_config():
    app = create_app()
    assert app is not None


def test_healthcheck(client):
    response = client.get("/healthcheck")
    assert response.status_code == 200
    assert response.json() == {"status": "Ok"}


def test_settings_defaults():
    settings = Settings()
    assert settings.host == "127.0.0.1"
    assert settings.port == 8000
    assert isinstance(settings.debug, bool)


def test_get_settings_cached():
    get_settings.cache_clear()
    s1 = get_settings()
    s2 = get_settings()
    assert s1 is s2

