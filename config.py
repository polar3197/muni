from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class PostgreSQLConfig(BaseSettings):
    host: str
    port: int = 5432
    user: str
    name: str
    password: str

    model_config = SettingsConfigDict(
        env_prefix="DB_",
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )

    @property
    def connection_string(self) -> str:
        return f"postgresql+asyncpg://{user}:{password}@{self.host}:{self.port}/{self.name}"

class S3Config(BaseSettings):
    bucket: str
    region: str = "us-west-1"

    model_config = SettingsConfigDict(
        env_prefix="S3_",
        env_file=".env"
    )


