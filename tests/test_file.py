import pytest
from service.utils import ReadFile


@pytest.mark.parametrize(
    ("common_config", "error"),
    [
        (
            {"format": "json", "h": ["name", "year", "sex"], "universe": "dark_horse"},
            "Invalid Universe File",
        )
    ],
)
def test_get_data_missing_file(common_config, error):
    with pytest.raises(TypeError) as e:
        assert ReadFile(common_config).get_data()
    assert error == str(e.value)


@pytest.mark.parametrize(
    "common_config",
    [
        (
            {
                "format": "json",
                "h": ["name", "year", "sex"],
                "help": False,
                "limit": 10,
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
            }
        ),
        (
            {
                "format": "json",
                "h": ["name", "year", "sex"],
                "help": False,
                "limit": 250,
                "nulls": "first",
                "pretty": False,
                "prune": True,
                "random": False,
                "s": [
                    {"column": "name", "sort": True},
                    {"column": "year", "sort": False},
                ],
                "seed": True,
                "universe": "marvel",
            }
        ),
        (
            {
                "format": "json",
                "h": ["name", "year", "sex"],
                "help": False,
                "limit": 1000,
                "nulls": "first",
                "pretty": False,
                "prune": True,
                "random": True,
                "seed": True,
                "universe": "marvel",
            }
        ),
        (
            {
                "characters": {"some": ["spider-man"], "every": [], "exclude": []},
                "format": "json",
                "h": ["name", "year", "sex"],
                "help": False,
                "limit": 10,
                "nulls": "first",
                "pretty": False,
                "prune": True,
                "random": False,
                "seed": False,
                "universe": "marvel",
            }
        ),
    ],
)
def test_get_data(common_config):
    file = ReadFile(common_config).get_data()
    assert len(file) <= common_config.get("limit")


@pytest.mark.parametrize(
    ("config", "expected"),
    [
        (
            {
                "characters": {
                    "some": ["spider-man", "spiderman", "spider man"],
                    "every": [],
                    "exclude": [],
                },
                "format": "json",
                "h": ["name", "year", "sex"],
                "help": False,
                "limit": 3,
                "nulls": "first",
                "pretty": False,
                "prune": False,
                "universe": "marvel",
            },
            [
                {
                    "name": "spider-man (peter parker)",
                    "sex": "male characters",
                    "year": 1962,
                },
                {
                    "name": "vern (spider-man) (earth-616)",
                    "sex": "male characters",
                    "year": 2008,
                },
                {
                    "name": "spiderman (1940s) (earth-616)",
                    "sex": "male characters",
                    "year": 1946,
                },
            ],
        ),
        (
            {
                "characters": {"some": [], "every": ["spider", "616"], "exclude": []},
                "format": "json",
                "h": ["name", "year", "sex"],
                "help": False,
                "limit": 2,
                "nulls": "first",
                "pretty": False,
                "prune": False,
                "universe": "marvel",
            },
            [
                {
                    "name": "peter parker (spidercide) (earth-616)",
                    "sex": "male characters",
                    "year": 1995,
                },
                {
                    "name": "bride of nine spiders (earth-616)",
                    "sex": "female characters",
                    "year": 2007,
                },
            ],
        ),
        (
            {
                "characters": {
                    "some": ["spider-man", "spiderman", "spider man"],
                    "every": [],
                    "exclude": ["616"],
                },
                "format": "json",
                "h": ["name", "year", "sex"],
                "help": False,
                "limit": 2,
                "nulls": "first",
                "pretty": False,
                "prune": False,
                "universe": "marvel",
            },
            [
                {
                    "name": "spider-man (peter parker)",
                    "sex": "male characters",
                    "year": 1962,
                }
            ],
        ),
    ],
)
def test_filter_characters(config, expected):
    data = ReadFile(config).get_data()
    file = ReadFile(config).filter_characters(data)
    assert file == expected


@pytest.mark.parametrize(
    "config",
    [
        {
            "format": "json",
            "h": ["name", "year", "sex"],
            "help": False,
            "limit": 1,
            "nulls": "first",
            "pretty": False,
            "prune": False,
            "universe": "marvel",
        },
        {
            "format": "json",
            "h": ["name", "year", "sex"],
            "help": False,
            "limit": 3,
            "nulls": "first",
            "pretty": False,
            "prune": False,
            "universe": "marvel",
        },
    ],
)
def test_filter_limit(config, common_data):
    file = ReadFile(config).filter_limit(common_data)
    assert len(file) == config.get("limit")


@pytest.mark.parametrize(
    "config",
    [
        {
            "format": "json",
            "h": ["name", "year", "sex"],
            "help": False,
            "limit": 0,
            "nulls": "first",
            "pretty": False,
            "prune": False,
            "universe": "marvel",
        }
    ],
)
def test_filter_limit_unlimited(config, common_data):
    file = ReadFile(config).filter_limit(common_data)
    assert len(file) == len(common_data)


@pytest.mark.parametrize(
    ("config", "expected"),
    [
        (
            {
                "format": "json",
                "h": ["name", "year", "sex"],
                "help": False,
                "limit": 100,
                "nulls": "first",
                "pretty": False,
                "prune": False,
                "universe": "marvel",
                "s": [{"column": "name", "sort": False}],
            },
            "äkräs (earth-616)",
        ),
        (
            {
                "format": "json",
                "h": ["name", "year", "sex"],
                "help": False,
                "limit": 100,
                "nulls": "first",
                "pretty": False,
                "prune": False,
                "universe": "marvel",
                "s": [{"column": "name", "sort": True}],
            },
            'wolverine (james "logan" howlett)',
        ),
        (
            {
                "format": "json",
                "h": ["name", "year", "sex"],
                "help": False,
                "limit": 100,
                "nulls": "false",
                "pretty": False,
                "prune": False,
                "universe": "marvel",
                "s": [{"column": "year", "sort": False}],
            },
            "namor mckenzie (earth-616)",
        ),
    ],
)
def test_sort_results_name(config, expected, common_data):
    file = ReadFile(config).sort_results(common_data)
    assert file[0].get("name") == expected


@pytest.mark.parametrize(
    ("config", "data", "expected"),
    [
        (
            {
                "format": "json",
                "h": ["value"],
                "nulls": "first",
                "s": [{"column": "value", "sort": False}],
            },
            {"name": "Zero", "value": 0},
            (False, True, 0),
        ),
        (
            {
                "format": "json",
                "h": ["value"],
                "nulls": "first",
                "s": [{"column": "value", "sort": False}],
            },
            {"name": "Sort_False_None", "value": None},
            (True, True, None),
        ),
        (
            {
                "format": "json",
                "h": ["value"],
                "nulls": "last",
                "s": [{"column": "value", "sort": True}],
            },
            {"name": "Sort_True_None", "value": None},
            (False, True, None),
        ),
        (
            {
                "format": "json",
                "h": ["value"],
                "nulls": "first",
                "s": [{"column": "value", "sort": True}],
            },
            {"name": "Sort_True_Empty", "value": ""},
            (False, False, ""),
        ),
    ],
)
def test_sort_i18n_str(config, data, expected):
    file = ReadFile(config).sort_i18n_str(data, config.get("s")[0])
    assert file == expected
