from os.path import join, dirname

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    BOT_TOKEN: SecretStr
    JWT_SECRET_TOKEN: SecretStr

    WEBAPP_URL: str = "https://rodjat.github.io/whdocbot"

    WEBHOOK_URL: str = "https://185.41.160.207"
    WEBHOOK_PATH: str = "/webhook"

    APP_HOST: str = "localhost"
    APP_PORT: int = 8000

    model_config = SettingsConfigDict(
        env_file=join(dirname(__file__), ".env"),
        env_file_encoding="utf-8"
    )

config = Config()
