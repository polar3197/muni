from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class PostgreSQLConfig(BaseSettings):
    host: str
    port: int = 5432
    user: str = ""
    name: str
    password: str = ""

    model_config = SettingsConfigDict(
        env_prefix="DB_",
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )

    @property
    def connection_string(self, asynch=True) -> str:
        from urllib.parse import quote_plus
        
        if asynch:
            # If no user, connect without credentials (peer auth)
            if not self.user or self.user == "":
                return f"postgresql+asyncpg://{self.host}:{self.port}/{self.name}"
            
            # If user but no password
            if not self.password or self.password == "":
                return f"postgresql+asyncpg://{self.user}@{self.host}:{self.port}/{self.name}"
            
            # Full credentials
            return f"postgresql+asyncpg://{self.user}:{quote_plus(self.password)}@{self.host}:{self.port}/{self.name}"
        else:
             # If no user, connect without credentials (peer auth)
            if not self.user or self.user == "":
                return f"postgresql://{self.host}:{self.port}/{self.name}"
            
            # If user but no password
            if not self.password or self.password == "":
                return f"postgresql://{self.user}@{self.host}:{self.port}/{self.name}"
            
            # Full credentials
            return f"postgresql://{self.user}:{quote_plus(self.password)}@{self.host}:{self.port}/{self.name}"

class S3Config(BaseSettings):
    bucket_name: str
    region: str = "us-west-1"

    model_config = SettingsConfigDict(
        env_prefix="S3_",
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )

class AWSConfig(BaseSettings):
    access_key_id: str
    secret_access_key: str

    model_config = SettingsConfigDict(
        env_prefix="AWS_",
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )

class GTFSConfig(BaseSettings):
    api_key: str

    model_config = SettingsConfigDict(
        env_prefix="GTFS_",
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )


