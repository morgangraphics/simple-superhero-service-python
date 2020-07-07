import pytest
from service.utils import InvalidUsage


@pytest.mark.parametrize(
    "error_msg", ["This is an error"],
)
def test_invalid_usage_message(error_msg):
    err = InvalidUsage("This is an error")
    assert err.message == error_msg


@pytest.mark.parametrize(
    "error_msg, status_code",
    [("This is an error", 404), ("This is another error", 503)],
)
def test_invalid_usage_message_with_code(error_msg, status_code):
    err = InvalidUsage(error_msg, status_code=status_code)
    assert err.message == error_msg
    assert err.status_code == status_code


@pytest.mark.parametrize(
    "error", [({"message": "This is another error"})],
)
def test_invalid_usage_to_dict(error):
    err = InvalidUsage("This is another error").to_dict()
    assert err == error
