import json
from typing import Optional, Any, Type, TypeVar, Callable

from decouple import config, UndefinedValueError
from pydantic import BaseModel, Field, ValidationError, validator

T = TypeVar('T')

def env_var(field_name: str, default: Any = None, cast_type: Callable[[str], T] = str) -> T:
    try:
        value = config(field_name, default=default)
        if value is None:
            return default
        return cast_type(value)
    except UndefinedValueError:
        return default
    except (TypeError, ValueError) as e:
        raise ValueError(f"Failed to cast environment variable {field_name} to {cast_type.__name__}") from e

class PostgresConfig(BaseModel):
    host: Optional[str] = Field(default_factory=lambda: env_var("POSTGRES_HOST", "localhost", str))
    port: Optional[int] = Field(default_factory=lambda: env_var("POSTGRES_PORT", 5432, int))
    user: Optional[str] = Field(default_factory=lambda: env_var("POSTGRES_USER", "postgres", str))
    password: Optional[str] = Field(default_factory=lambda: env_var("POSTGRES_PASSWORD", "password", str))
    database: Optional[str] = Field(default_factory=lambda: env_var("POSTGRES_DB", "database", str))
    url: Optional[str] = Field(default=None)
    timeout: Optional[int] = Field(default_factory=lambda: env_var("TIMEOUT", 5, int))
    pool_size: Optional[int] = Field(default_factory=lambda: env_var("POOL_SIZE", 100, int))
    max_pool_con: Optional[int] = Field(default_factory=lambda: env_var("MAX_POOL_CON", 80, int))
    pool_overflow: Optional[int] = Field(default_factory=lambda: env_var("POOL_OVERFLOW", 20, int))
    echo_log: Optional[bool] = Field(default_factory=lambda: env_var("ECHO_LOG", False, bool))
    expire_on_commit: Optional[bool] = Field(default_factory=lambda: env_var("EXPIRE_ON_COMMIT", True, bool))
    autoflush: Optional[bool] = Field(default_factory=lambda: env_var("AUTO_FLUSH", True, bool))

    def __repr__(self) -> str:
        attributes = self.dict(exclude={"url"})
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
