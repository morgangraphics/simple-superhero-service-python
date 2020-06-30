import os
from flask import Flask
from flask import jsonify
from pathlib import Path
from .utils import InvalidUsage


def create_app(test_config=None, **kwargs):
    """
    Flask Service Entry Point/Initialization
    :param test_config:
    :return:
    """
    # create and configure the app
    app = Flask(__name__, instance_relative_config=False)

    @app.errorhandler(InvalidUsage)
    def handle_invalid_usage(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    default_yaml_path = (
        Path(__file__).resolve().parent.parent / "config" / "default.cfg"
    )
    environment_yaml_path = ""
    environment = (
        kwargs.get("environment")
        if kwargs.get("environment")
        else os.environ.get("FLASK_ENV")
    )
    path = Path(__file__).resolve().parent.parent / "config" / f"{environment}.cfg"

    if path.is_file():
        environment_yaml_path = path

    if test_config is None:
        # Will load Environment Variables from .env file
        app.config.from_pyfile("settings.py", silent=False)
        # Will load default application variables
        app.config.from_pyfile(default_yaml_path, silent=False)
        # Will override default application variables depending on environment
        app.config.from_pyfile(environment_yaml_path, silent=True)

    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from service import routes

    routes.init_app(app)

    return app
