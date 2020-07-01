from flask import Blueprint
from flask import json

"""
Simple Health check route
"""
bp_hc = Blueprint("healthcheck", __name__)


@bp_hc.route("/healthcheck", methods=["GET"])
def healthcheck():
    return json.dumps({"status": "Ok"})
