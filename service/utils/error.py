class InvalidUsage(Exception):
    """
        InvalidUsage Class
        Handles Error messaging normalization for Flask
    """
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        """
        Normalizes Flask Error code is JSON
        https://flask.palletsprojects.com/en/master/errorhandling/#returning-api-errors-as-json

        :param message:
        :param status_code:
        :param payload:
        """
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        """
        Normalizes the error message in a dictionary

        :return:
        """
        rv = dict(self.payload or ())
        rv["message"] = str(self.message)

        return rv
