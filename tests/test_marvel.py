import pytest
import json


def bytes_to_json(response):
    return json.loads(response.data.decode("utf8").replace("'", '"'))


@pytest.mark.parametrize(
    ("endpoint", "response_code"), [("/marvel", 308)],
)
def test_no_trailing_slash(client, endpoint, response_code):
    response = client.get(endpoint)
    assert response.status_code == response_code


@pytest.mark.parametrize(
    ("endpoint", "response_code"), [("/marvel/", 200)],
)
def test_trailing_slash(client, endpoint, response_code):
    response = client.get(endpoint)
    data = bytes_to_json(response)
    assert response.status_code == response_code
    assert len(data) == 100


@pytest.mark.parametrize(
    ("endpoint", "error_msg"), [("/marvel/", "Invalid Universe File")],
)
def test_get_data_missing_file(client, endpoint, error_msg):
    response = client.get(f"{endpoint}?universe=foo")
    data = bytes_to_json(response)
    assert data.get("message") == error_msg


@pytest.mark.parametrize(
    "endpoint", ["/marvel/spider-man"],
)
def test_get_data_with_character(client, endpoint):
    response = client.get(endpoint, follow_redirects=True)
    data = bytes_to_json(response)
    assert len(data) != 0


@pytest.mark.parametrize(
    ("endpoint", "character"), [("/marvel", "spider-man")],
)
def test_get_help(client, endpoint, character):
    response = client.get(f"{endpoint}/{character}/?help")
    data = response.data.decode("utf8")
    assert character in data


@pytest.mark.parametrize(
    ("endpoint", "character"), [("/marvel/", "spider-man")],
)
def test_get_pretty(client, endpoint, character):
    response = client.get(f"{endpoint}?pretty")
    assert response.headers["Content-Type"] == "application/json"


@pytest.mark.parametrize(
    ("endpoint", "payload", "expected"),
    [("/marvel/", {"characters": "spider man"}, "spider-man (peter parker)")],
)
def test_post_endpoint(client, endpoint, payload, expected):
    response = client.post(f"{endpoint}", json=payload)
    data = bytes_to_json(response)
    assert data[0].get("name") == expected
