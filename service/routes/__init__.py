from fastapi import FastAPI

from .dc import bp_dc
from .healthcheck import bp_hc
from .marvel import bp_marvel


def init_app(app: FastAPI) -> None:
    app.include_router(bp_dc)
    app.include_router(bp_hc)
    app.include_router(bp_marvel)

