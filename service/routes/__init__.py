from .dc import bp_dc
from .healthcheck import bp_hc
from .marvel import bp_marvel
from .swagger import bp_swagger, SWAGGER_URL


def init_app(app):
    app.register_blueprint(bp_dc)
    app.register_blueprint(bp_hc)
    app.register_blueprint(bp_marvel)
    app.register_blueprint(bp_swagger, url_prefix=SWAGGER_URL)
