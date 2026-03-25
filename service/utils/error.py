class InvalidUsage(Exception):
    """
    InvalidUsage
    Normalizes application errors into a JSON-serialisable dictionary.
    """

    status_code = 400

    def __init__(self, message: object, status_code: int | None = None, payload: object = None) -> None:
        """
        :param message: Human-readable error description.
        :param status_code: HTTP status code to return (default 400).
        :param payload: Optional extra data to include in the response body.
        """
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self) -> dict[str, object]:
        """Return the error as a plain dictionary."""
        rv = dict(self.payload or ())
        rv["message"] = str(self.message)
        return rv
