import json
from typing import Optional, Any, Type, TypeVar
from pydantic import BaseModel, Field, ValidationError, validator
from decouple import config, UndefinedValueError

T = TypeVar('T')

def env_var(field_name: str, default = None, cast_type = str) -> T:
    try:
        value = config(field_name, default=default)
        return cast_type(value)
    except Exception:
        return default

class PostgresConfig(BaseModel):
    host: Optional[str] = Field(default_factory=lambda: env_var("POSTGRES_HOST", "localhost", str))
    port: Optional[int] = Field(default_factory=lambda: env_var("POSTGRES_PORT", 5432, int))
    user: Optional[str] = Field(default_factory=lambda: env_var("POSTGRES_USER", "postgres", str))
    password: Optional[str] = Field(default_factory=lambda: env_var("POSTGRES_PASSWORD", "password", str))
    database: Optional[str] = Field(default_factory=lambda: env_var("POSTGRES_DB", "database", str))
    url: Optional[str] = Field(default=None)
    db_timeout: Optional[int] = Field(default_factory=lambda: env_var("DB_TIMEOUT", 5, int))
    db_pool_size: Optional[int] = Field(default_factory=lambda: env_var("DB_POOL_SIZE", 100, int))
    db_max_pool_con: Optional[int] = Field(default_factory=lambda: env_var("DB_MAX_POOL_CON", 80, int))
    db_pool_overflow: Optional[int] = Field(default_factory=lambda: env_var("DB_POOL_OVERFLOW", 20, int))
    enable_db_echo_log: Optional[bool] = Field(default_factory=lambda: env_var("ENABLE_DB_ECHO_LOG", False, bool))
    enable_db_expire_on_commit: Optional[bool] = Field(default_factory=lambda: env_var("ENABLE_DB_EXPIRE_ON_COMMIT", False, bool))
    enable_db_force_rollback: Optional[bool] = Field(default_factory=lambda: env_var("ENABLE_DB_FORCE_ROLLBACK", True, bool))

    def __repr__(self) -> str:
        attributes = self.dict(exclude={"url"})
        attributes['url'] = self.async_url
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
