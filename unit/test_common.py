import pytest

from service.utils import ServiceUtils


@pytest.mark.parametrize(
    ("direction", "expected"), (("asc", False), ("desc", True), ("", True),),
)
def test_direction(direction, expected):
    api = ServiceUtils.direction(direction)
    assert expected == api


@pytest.mark.parametrize(
    "param",
    (
        ["this is a list"],
        "this is a string",
        "this is a string,and another string",
        dict([("key", "this is a dict")]),
        {"key": "some value"},
    ),
)
def test_handle_param_type(param):
    api = ServiceUtils.handle_param_types(param)
    assert isinstance(api, list)


@pytest.mark.parametrize(
    ("name", "expected"),
    (
        ("iron man", ["iron man", "iron-man", "ironman"]),
        (
            "spider-man,captain america",
            [
                "spider-man",
                "spider man",
                "spiderman",
                "captain america",
                "captain-america",
                "captainamerica",
            ],
        ),
        ("superman", ["superman"]),
        ("spider-man,spider-man", ["spider-man", "spider man", "spiderman"],),
    ),
)
def test_permutate(name, expected):
    api = ServiceUtils.permutate(ServiceUtils.handle_param_types(name))
    assert all(item in expected for item in api)
