import pytest
from service import create_app
from urllib.parse import urlparse, parse_qsl


def normalize_url(url, universe="marvel"):
    url_dict = dict(parse_qsl(urlparse(url).query, keep_blank_values=True))
    if universe is not None:
        url_dict["universe"] = universe
    return url_dict


@pytest.fixture
def app():
    app = create_app({"TESTING": True})
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


@pytest.fixture
def common_data():
    return [
        {"name": "spider-man (peter parker)", "sex": "male characters", "year": 1962},
        {
            "name": "captain america (steven rogers)",
            "sex": "male characters",
            "year": 1941,
        },
        {
            "name": 'wolverine (james "logan" howlett)',
            "sex": "male characters",
            "year": 1974,
        },
        {
            "name": 'iron man (anthony "tony" stark)',
            "sex": "male characters",
            "year": 1963,
        },
        {"name": "thor (thor odinson)", "sex": "male characters", "year": 1950},
        {"name": "benjamin grimm (earth-616)", "sex": "male characters", "year": 1961},
        {"name": "äkräs (earth-616)", "sex": "male characters", "year": 2009},
        {"name": "alexander aaron (earth-616)", "sex": "male characters", "year": 2006},
        {"name": "namor mckenzie (earth-616)", "sex": "male characters", "year": None},
    ]


@pytest.fixture
def common_config():
    return {
        "format": "json",
        "h": ["name", "year", "sex"],
        "help": False,
        "limit": 5,
        "nulls": "first",
        "pretty": False,
        "prune": True,
        "random": True,
        "s": [{"column": "name", "sort": True}, {"column": "year", "sort": False}],
        "seed": True,
        "universe": "marvel",
    }


@pytest.fixture
def common_config_options(request):
    # args,universe,expected
    data = dict()
    data["configuration"] = [
        (
            normalize_url(
                "https://localhost:5000/marvel/?format=json&limit=250&random&seed&s=name:desc,year:asc&h=name,year,sex"
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
    ]
    val = []
    if request is not None and data.get(request.param):
        val = data[request.param]
    return val
