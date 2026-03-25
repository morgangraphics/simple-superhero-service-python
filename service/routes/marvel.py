"""
Marvel Comic Book Character Routing Setup
"""

import json
import re
from typing import Annotated, Optional

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse, PlainTextResponse, Response

from ..models import CharacterSearchBody
from ..utils import ApiUtils, InvalidUsage, ReadFile

bp_marvel = APIRouter(prefix="/marvel")

_TF_TEXT = "No default value is required, presence equates to true"

_BASE_DESCRIPTION = """Returns an array of JSON objects of Marvel Character Universe Biographical \
Information as found from https://datahub.io/five-thirty-eight/comic-characters dataset

Shorthand query syntax is available for help, pretty, prune, random and seed. \
Meaning their presence equates to true

e.g. `?pretty&random` and `?pretty=true&random=true` are functionally equivalent

\\* Swagger parameter functionality below only allows for `?pretty=true|false` \
formatting for "Try it out" button"""

_CHAR_DESCRIPTION = """Returns an array of JSON objects of Marvel Character Biographical \
Information as found from https://datahub.io/five-thirty-eight/comic-characters dataset

Shorthand query syntax is available for help, pretty, and prune. \
Meaning their presence equates to true

e.g. `?pretty` and `?pretty=true` are functionally equivalent

**character: character filters can used like:**

`{keyword1},{keyword2}` e.g. iron man,spider-man will search for each character individually

`{keyword1}+{keyword2}` e.g. spider+man will search for a character name with both \
'spider' AND 'man' in it

`{keyword1},-{keyword2}` e.g. iron man,earth-616 will search for character names \
containing 'iron man' EXCLUDING results with earth-616 in it"""

_POST_DESCRIPTION = _CHAR_DESCRIPTION + """

---

**characters: characters can be a string, or an array of strings (preferred)** e.g.

```json
{ "characters": "spider-man,iron man" }
```
OR
```json
{ "characters": ["spider-man", "iron man"] }
```

**h: h can be a string, or an array (preferred)** e.g.

```json
{ "h": "name,appearances,year" }
```
OR
```json
{ "h": ["name", "appearances", "year"] }
```

**s: can be a string, an object, array of strings, or an array of objects (preferred)** e.g.

```json
{ "s": "name:asc,appearances:desc" }
```
OR
```json
{ "s": { "column": "name", "sort": "asc" } }
```
OR
```json
{ "s": ["name:asc", "appearances:desc"] }
```
OR
```json
{ "s": [{ "column": "name", "sort": "asc" }, { "column": "appearances", "sort": "desc" }] }
```"""


def _sanitize(value: str) -> str:
    """Strip characters that are not URL/name safe from a path parameter."""
    return re.sub(r"[^\w\s.,+:@-]", "", value)


def _build_options(
    characters: Optional[str],
    format: Optional[str],
    h: Optional[str],
    help: Optional[str],
    limit: Optional[str],
    nulls: Optional[str],
    pretty: Optional[str],
    prune: Optional[str],
    random: Optional[str],
    s: Optional[str],
    seed: Optional[str],
    universe: str,
) -> dict:
    options: dict = {"universe": universe}
    if characters is not None:
        options["characters"] = characters
    for key, val in {
        "format": format,
        "h": h,
        "limit": limit,
        "nulls": nulls,
        "s": s,
    }.items():
        if val is not None:
            options[key] = val
    # Presence-style flags: key present (even empty string) means True
    for key, val in {
        "help": help,
        "pretty": pretty,
        "prune": prune,
        "random": random,
        "seed": seed,
    }.items():
        if val is not None:
            options[key] = val
    return options


def _respond(api: ApiUtils, config: dict):
    if config.get("help"):
        return PlainTextResponse(api.show_help())

    try:
        data = ReadFile(config).get_data()
    except (TypeError, InvalidUsage) as error:
        if isinstance(error, InvalidUsage):
            # Preserve original InvalidUsage, including its status_code and payload
            raise
        raise InvalidUsage(error)

    if config.get("pretty"):
        body = json.dumps(
            data,
            indent=4,
            separators=(",", ": "),
            sort_keys=False,
            ensure_ascii=False,
        )
        return Response(content=body, media_type="application/json")

    return JSONResponse(content=data)


@bp_marvel.get(
    "/",
    tags=["marvel"],
    summary="Filterable response of Marvel Character Universe Biographical information",
    description=_BASE_DESCRIPTION,
)
def marvel_get_base(
    characters: Annotated[Optional[str], Query(description="Character(s) to search for as a string value (e.g. a single name or a comma-separated list).")] = None,
    format: Annotated[Optional[str], Query(description="Output format (currently only JSON)")] = None,
    h: Annotated[Optional[str], Query(description="Headers to display as a string value (e.g. a single header or a comma-separated list).")] = None,
    help: Annotated[Optional[str], Query(description=f"List available options. {_TF_TEXT}")] = None,
    limit: Annotated[Optional[str], Query(description="Limit result set. '0' for no limit")] = None,
    nulls: Annotated[Optional[str], Query(description=f"Sort null values first or last in order. {_TF_TEXT}")] = None,
    pretty: Annotated[Optional[str], Query(description=f"Pretty print the result set. {_TF_TEXT}")] = None,
    prune: Annotated[Optional[str], Query(description=f"Remove keys with null values. {_TF_TEXT}")] = None,
    random: Annotated[Optional[str], Query(description=f"Returns array of random superheros based on limit. {_TF_TEXT}")] = None,
    s: Annotated[Optional[str], Query(description="Columns to sort on.")] = None,
    seed: Annotated[Optional[str], Query(description=f"Keep the same random characters on multiple requests. {_TF_TEXT}")] = None,
    universe: Annotated[Optional[str], Query(include_in_schema=False)] = None,
):
    api = ApiUtils()
    options = _build_options(
        characters=characters,
        format=format,
        h=h,
        help=help,
        limit=limit,
        nulls=nulls,
        pretty=pretty,
        prune=prune,
        random=random,
        s=s,
        seed=seed,
        universe=universe or "marvel",
    )
    config = api.handle_config(options)
    return _respond(api, config)


@bp_marvel.get(
    "/{characters}",
    tags=["marvel"],
    summary="Search for specific Marvel Universe Character(s)",
    description=_CHAR_DESCRIPTION,
)
def marvel_get_by_character(
    characters: str,
    format: Annotated[Optional[str], Query(description="Output format (currently only JSON)")] = None,
    h: Annotated[Optional[str], Query(description="Headers to display. Either a string or Array of strings")] = None,
    help: Annotated[Optional[str], Query(description=f"List available options. {_TF_TEXT}")] = None,
    limit: Annotated[Optional[str], Query(description="Limit result set. '0' for no limit")] = None,
    nulls: Annotated[Optional[str], Query(description=f"Sort null values first or last in order. {_TF_TEXT}")] = None,
    pretty: Annotated[Optional[str], Query(description=f"Pretty print the result set. {_TF_TEXT}")] = None,
    prune: Annotated[Optional[str], Query(description=f"Remove keys with null values. {_TF_TEXT}")] = None,
    s: Annotated[Optional[str], Query(description="Columns to sort on.")] = None,
):
    api = ApiUtils()
    safe_chars = _sanitize(characters)
    options = _build_options(
        characters=safe_chars,
        format=format,
        h=h,
        help=help,
        limit=limit,
        nulls=nulls,
        pretty=pretty,
        prune=prune,
        random=None,
        s=s,
        seed=None,
        universe="marvel",
    )
    config = api.handle_config(options)
    return _respond(api, config)


@bp_marvel.post(
    "/",
    tags=["marvel"],
    summary="Search for specific Marvel Universe Character(s)",
    description=_POST_DESCRIPTION,
)
def marvel_post(body: CharacterSearchBody):
    api = ApiUtils()
    options = body.model_dump(exclude_none=True)
    options.setdefault("universe", "marvel")
    config = api.handle_config(options)
    return _respond(api, config)

