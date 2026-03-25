from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from .utils import InvalidUsage


_DESCRIPTION = """I needed a self-contained data service (no Database) for testing a number of different \
scenarios with a diverse and robust dataset that also contains some sparseness.

Service runs on Python and FastAPI.

The service itself and the data contained within service is useful for testing:

1. CORS configuration
1. Server configuration
1. Bandwidth
1. Form population
1. Data visualization
1. Stubbing out UI components
...

Data is the comic book character dataset from \
[fivethrityeight](https://datahub.io/five-thirty-eight/comic-characters#readme)"""


def create_app() -> FastAPI:
    """
    FastAPI application factory.
    """
    app = FastAPI(
        title="Simple Superhero Service API Documentation",
        version="2.0.0",
        description=_DESCRIPTION,
        contact={"name": "MORGANGRAPHICS", "url": "https://github.com/morgangraphics"},
        docs_url="/swagger",
        redoc_url=None,
        openapi_url="/openapi.json",
    )

    # Mount the static directory for any static assets
    static_path = Path(__file__).resolve().parent / "static"
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

    @app.exception_handler(InvalidUsage)
    async def handle_invalid_usage(request: Request, error: InvalidUsage) -> JSONResponse:
        return JSONResponse(status_code=error.status_code, content=error.to_dict())

    from service import routes

    routes.init_app(app)

    return app
