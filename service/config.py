from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parent.parent / "config" / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Server
    host: str = "127.0.0.1"
    port: int = 8000
    debug: bool = False
    ssl_cert: str | None = None
    ssl_key: str | None = None
    secret_key: str = "changeme"

    # Custom / tests
    test_string: str = "DEFAULT HELLO"


@lru_cache
def get_settings() -> Settings:
    return Settings()
