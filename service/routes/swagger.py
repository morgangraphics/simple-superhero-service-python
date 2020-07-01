from flask_swagger_ui import get_swaggerui_blueprint

SWAGGER_URL = "/swagger"
API_URL = "/static/swagger.json"

bp_swagger = get_swaggerui_blueprint(SWAGGER_URL, API_URL)
