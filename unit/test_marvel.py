import pytest


@pytest.mark.parametrize(
    ("endpoint", "response_code"), [("/marvel", 307)],
)
def test_no_trailing_slash(client, endpoint, response_code):
    response = client.get(endpoint, follow_redirects=False)
    assert response.status_code == response_code


@pytest.mark.parametrize(
    ("endpoint", "response_code"), [("/marvel/", 200)],
)
def test_trailing_slash(client, endpoint, response_code):
    response = client.get(endpoint)
    data = response.json()
    assert response.status_code == response_code
    assert len(data) == 100


@pytest.mark.parametrize(
    ("endpoint", "error_msg"), [("/marvel/", "Invalid Universe File")],
)
def test_get_data_missing_file(client, endpoint, error_msg):
    response = client.get(f"{endpoint}?universe=foo")
    data = response.json()
    assert data.get("message") == error_msg


@pytest.mark.parametrize(
    "endpoint", ["/marvel/spider-man"],
)
def test_get_data_with_character(client, endpoint):
    response = client.get(endpoint, follow_redirects=True)
    data = response.json()
    assert len(data) != 0


@pytest.mark.parametrize(
    ("endpoint", "character"), [("/marvel", "spider-man")],
)
def test_get_help(client, endpoint, character):
    response = client.get(f"{endpoint}/{character}/?help")
    data = response.text
    assert character in data


@pytest.mark.parametrize(
    ("endpoint", "character"), [("/marvel/", "spider-man")],
)
def test_get_pretty(client, endpoint, character):
    response = client.get(f"{endpoint}?pretty")
    assert "application/json" in response.headers["Content-Type"]



@pytest.mark.parametrize(
    ("endpoint", "payload", "expected"),
    [("/marvel/", {"characters": "spider man"}, "spider-man (peter parker)")],
)
def test_post_endpoint(client, endpoint, payload, expected):
    response = client.post(f"{endpoint}", json=payload)
    data = response.json()
    assert data[0].get("name") == expected


@pytest.mark.parametrize(
    ("endpoint", "params"),
    [
        ("/marvel/", {"limit": "5"}),
        ("/marvel/", {"h": "name,appearances"}),
        ("/marvel/", {"s": "name:asc"}),
        ("/marvel/", {"nulls": "last"}),
        ("/marvel/", {"format": "json"}),
    ],
)
def test_get_query_params(client, endpoint, params):
    response = client.get(endpoint, params=params)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
