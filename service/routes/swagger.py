from pathlib import Path

from flask_swagger_ui import get_swaggerui_blueprint


swagger_path = Path(__file__).resolve().parent.parent.parent / "static" / "swagger.json"
print(swagger_path)

SWAGGER_URL = "/swagger"
API_URL = "/static/swagger.json"

bp_swagger = get_swaggerui_blueprint(SWAGGER_URL, API_URL)
