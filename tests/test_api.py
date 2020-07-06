import pytest
from urllib.parse import urlparse, parse_qsl
from service.utils import ApiUtils


def normalize_url(url, universe="marvel"):
    url_dict = dict(parse_qsl(urlparse(url).query, keep_blank_values=True))
    if universe is not None:
        url_dict["universe"] = universe
    return url_dict


@pytest.mark.parametrize(
    ("characters", "expected"),
    (
        (
            "iron man",
            {"some": ["iron man", "iron-man", "ironman"], "every": [], "exclude": []},
        ),
        ("spider+man", {"some": [], "every": ["spider", "man"], "exclude": []}),
        (
            "spider man,wolverine+woman,-earth-616",
            {
                "some": ["spider man", "spider-man", "spiderman"],
                "every": ["wolverine", "woman"],
                "exclude": ["earth616"],
            },
        ),
    ),
)
def test_character_search_dict(characters, expected):
    api = ApiUtils().character_search_dict(characters)
    assert expected == api


@pytest.mark.parametrize(
    "args,universe,expected",
    [
        (
            dict(
                parse_qsl(
                    urlparse(
                        "https://localhost:5000/marvel/?format=json&limit=250&random&seed&s=name:desc,year:asc&h=name,year,sex"
                    ).query,
                    keep_blank_values=True,
                ),
                universe="marvel",
            ),
            "marvel",
            {
                "format": "json",
                "h": ["name", "year", "sex"],
                "help": False,
                "limit": 250,
                "nulls": "first",
                "pretty": False,
                "prune": False,
                "random": True,
                "s": [
                    {"column": "name", "sort": True},
                    {"column": "year", "sort": False},
                ],
                "seed": True,
                "universe": "marvel",
            },
        ),
        (
            {"format": "json", "limit": 10, "universe": "marvel"},
            "marvel",
            {
                "format": "json",
                "help": False,
                "limit": 10,
                "nulls": "first",
                "pretty": False,
                "prune": False,
                "universe": "marvel",
            },
        ),
        (
            {"format": "json", "limit": 0, "universe": "dc", "pretty": "", "prune": ""},
            "dc",
            {
                "format": "json",
                "help": False,
                "limit": 0,
                "nulls": "first",
                "pretty": True,
                "prune": True,
                "universe": "dc",
            },
        ),
        (
            {
                "characters": "man,-woman",
                "h": ["name", "year", "sex"],
                "s": [
                    {"column": "name", "sort": "desc"},
                    {"column": "year", "sort": "asc"},
                ],
                "universe": "marvel",
            },
            "marvel",
            {
                "characters": {"some": ["man"], "every": [], "exclude": ["woman"]},
                "format": "json",
                "h": ["name", "year", "sex"],
                "help": False,
                "limit": 100,
                "nulls": "first",
                "pretty": False,
                "prune": False,
                "s": [
                    {"column": "name", "sort": True},
                    {"column": "year", "sort": False},
                ],
                "universe": "marvel",
            },
        ),
    ],
)
def test_handle_config(args, universe, expected):
    api = ApiUtils().handle_config(args)
    assert api.get("universe") == universe
    assert isinstance(api.get("help"), bool)
    assert isinstance(api.get("pretty"), bool)
    assert isinstance(api.get("prune"), bool)
    assert expected == api


@pytest.mark.parametrize("common_config_options", ["configuration"], indirect=True)
def test_handle_config_two(common_config_options):
    for test in common_config_options:
        args, universe, expected = test
        api = ApiUtils().handle_config(args)
        assert api.get("universe") == universe
        assert isinstance(api.get("help"), bool)
        assert isinstance(api.get("pretty"), bool)
        assert isinstance(api.get("prune"), bool)
        assert expected == api


@pytest.mark.parametrize(
    ("universe", "character"),
    (
        ("marvel", "iron man"),
        ("marvel", "spider-man"),
        ("dc", "superman"),
        ("dc", "batman"),
    ),
)
def test_help_search(universe, character):
    api = ApiUtils().help_search(universe)
    assert character in api

@pytest.mark.parametrize(
        ("endpoint", "expected"), [("/marvel", "nulls"), ("/dc", "help")],
    )
def test_show_help_no_characters(client, endpoint, expected):
    response = client.get(f"{endpoint}/?help")
    data = response.data.decode("utf8")
    assert expected in data

@pytest.mark.parametrize(
    ("endpoint", "character"), [("/marvel/", "spider-man"), ("/dc/", "batman")],
)
def test_show_help_with_characters(client, endpoint, character):
    response = client.get(f"{endpoint}/{character}/?help")
    data = response.data.decode("utf8")
    assert character in data

@pytest.mark.parametrize(
    ("sort_str", "expected"),
    (
        ("name", [{"column": "name", "sort": False}]),
        ("name:desc", [{"column": "name", "sort": True}]),
        (
            "name,year:desc",
            [{"column": "name", "sort": False}, {"column": "year", "sort": True}],
        ),
        (
            "name:asc,sex:desc,year:asc",
            [
                {"column": "name", "sort": False},
                {"column": "sex", "sort": True},
                {"column": "year", "sort": False},
            ],
        ),
    ),
)
def test_sort_dict(sort_str, expected):
    api = ApiUtils().sort_dict(sort_str)
    assert expected == api
