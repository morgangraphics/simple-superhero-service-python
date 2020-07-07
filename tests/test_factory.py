import pytest
from service import create_app
from service.utils.error import InvalidUsage


def test_config():
    assert not create_app().testing
    assert create_app({"TESTING": True}).testing


def test_no_config_file():
    assert create_app(environment="foo").config.get("TEST_STRING") == "DEFAULT HELLO"


def test_config_file():
    assert (
        create_app(environment="production").config.get("TEST_STRING")
        == "PRODUCTION HELLO"
    )


def test_healthcheck(client):
    response = client.get("/healthcheck")
    assert response.status_code == 200
    assert response.data == b'{"status": "Ok"}'
