from pydantic import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "IA API"
    APP_VERSION: str = "0.1.0"
    OPENAI_API_KEY: str | None = None

    class Config:
        env_file = ".env"


settings = Settings()
