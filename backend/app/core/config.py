from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Milk Tea Loyalty API"
    database_url: str = "data/loyalty.db"
    cors_origins: list[str] = [
        f"http://localhost:{port}"
        for port in range(5173, 5190)
    ] + [
        f"http://127.0.0.1:{port}"
        for port in range(5173, 5190)
    ]

    model_config = SettingsConfigDict(env_file=".env", env_prefix="LOYALTY_")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
