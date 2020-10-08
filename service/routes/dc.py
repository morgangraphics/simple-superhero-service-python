"""
DC Comic Book Character Routing Setup
"""

from flask import Blueprint
from flask import json
from flask import request
from flask import Response
from markupsafe import escape
from ..utils import ApiUtils
from ..utils import ReadFile
from ..utils import InvalidUsage

bp_dc = Blueprint("dc", __name__, url_prefix="/dc")


@bp_dc.route("/", methods=["GET", "POST"])
@bp_dc.route("/<characters>/", methods=["GET"])
def dc(characters=None):
    """
    DC endpoint. Flask defaults to trailing slash which works for
    both dc/badman and /dc/batman/

    :param characters: (str) String representation of DC characters to search/filter by e.g batman
    """
    api = ApiUtils()
    options = dict().copy()
    options.update(request.args)

    if request.method == "GET" and characters is not None:
        options.update({"characters": escape(characters)})

    if request.method == "POST":
        options.update(request.json)

    if not request.args.get("universe"):
        options.update({"universe": "dc"})

    config = api.handle_config(options)

    if request.args.get("help") or request.args.get("help") == "":
        return Response(api.show_help(), mimetype="text/plain")

    else:

        try:
            data = ReadFile(config).get_data()
        except (TypeError, InvalidUsage) as error:
            raise InvalidUsage(error)

        if config.get("pretty"):
            response = json.dumps(
                data,
                indent=4,
                separators=(",", ": "),
                sort_keys=False,
                ensure_ascii=False,
            ).encode("utf-8")
        else:
            response = json.dumps(data, sort_keys=False, ensure_ascii=False)

        return Response(response, mimetype="application/json")
