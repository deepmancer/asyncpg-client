import json
from typing import Optional

from decouple import config
from pydantic import BaseModel, Field


class PostgresConfig(BaseModel):
    host: str = Field(default_factory=lambda: config("POSTGRES_HOST", "localhost"))
    port: int = Field(default_factory=lambda: int(config("POSTGRES_PORT", 5432)))
    user: str = Field(default_factory=lambda: config("POSTGRES_USER", "postgres"))
    password: Optional[str] = Field(default_factory=lambda: config("POSTGRES_PASSWORD", "password"))
    database: str = Field(default_factory=lambda: config("POSTGRES_DB", "database"))
    timeout: int = Field(default_factory=lambda: int(config("TIMEOUT", 5)))
    pool_size: int = Field(default_factory=lambda: int(config("POOL_SIZE", 100)))
    max_pool_con: int = Field(default_factory=lambda: int(config("MAX_POOL_CON", 80)))
    pool_overflow: int = Field(default_factory=lambda: int(config("POOL_OVERFLOW", 20)))
    echo_log: bool = Field(default_factory=lambda: config("ECHO_LOG", False, cast=bool))
    expire_on_commit: bool = Field(default_factory=lambda: config("EXPIRE_ON_COMMIT", True, cast=bool))
    autoflush: bool = Field(default_factory=lambda: config("AUTO_FLUSH", True, cast=bool))
    url: Optional[str] = Field(default=None)

    def __repr__(self) -> str:
        attributes = self.model_dump(exclude={"url"})
        attributes['async_url'] = self.async_url
        attributes['sync_url'] = self.sync_url        
        attributes_str = json.dumps(attributes, indent=4)[1:-1]
        return f"{self.__class__.__name__}({attributes_str})"

    def __str__(self) -> str:
        return self.__repr__()

    @property
    def async_url(self) -> str:
        return self.url or f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
    
    @property
    def sync_url(self) -> str:
        return self.url or f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
