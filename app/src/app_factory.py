from fastapi import FastAPI
from settings import settings  # noqa
from logger import configure_logger


def app_factory():
    configure_logger()
    app = FastAPI(title="VideoStreamer",)
    from api.api_v1.api import api_router

    app.include_router(api_router)
    return app
