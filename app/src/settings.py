from typing import Optional, Dict, Any
from pydantic import BaseSettings, PostgresDsn, validator, constr  # noqa
from dependency_injector import providers


class Settings(BaseSettings):
    # Video Source
    RTSP_SOURCE: str
    VIDEO_READER_QUEUE_SIZE: int = 10

    # Run Mode
    DEBUG: Optional[bool] = False
    TESTING: Optional[bool] = False

    # LOGGER
    LOG_LEVEL = "INFO"
    LOG_FILE = "app.log"


settings = Settings()
