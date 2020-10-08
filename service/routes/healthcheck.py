"""
Simple Health check route
"""

from flask import Blueprint
from flask import json


bp_hc = Blueprint("healthcheck", __name__)


@bp_hc.route("/healthcheck", methods=["GET"])
def healthcheck():
    """
    Simple health check endpoint
    :return:
    """
    return json.dumps({"status": "Ok"})
