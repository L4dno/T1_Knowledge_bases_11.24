from pydantic_settings import BaseSettings


class Config(BaseSettings):
    GEMINI_API_URL: str
    GEMINI_API_KEY: str
    CLICKHOUSE_HOST: str
    CLICKHOUSE_PORT: int

    class Config:
        env_file = ".env"

config = Config()
