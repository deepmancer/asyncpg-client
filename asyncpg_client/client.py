import contextlib
import asyncio
from typing import Dict, Optional

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.exc import SQLAlchemyError

from .exceptions import PGConnectionError, PGSessionCreationError, PGEngineInitializationError
from .config import PostgresConfig

class AsyncPostgres:
    _instances: Dict[str, 'AsyncPostgres'] = {}
    _locks: Dict[str, asyncio.Lock] = {}

    def __new__(cls, config: PostgresConfig, *args, **kwargs) -> 'AsyncPostgres':
        url = config.async_url
        if url not in cls._locks:
            cls._locks[url] = asyncio.Lock()
        return cls._instances.get(url, None) or super().__new__(cls)

    def __init__(self, config: PostgresConfig) -> None:
        if not hasattr(self, '_initialized') or not self._initialized:
            self._config = config
            self._async_engine: Optional[AsyncEngine] = None
            self._async_session_maker: Optional[async_sessionmaker] = None
            self._initialized = True

    @classmethod
    async def create(
        cls,
        config: Optional[PostgresConfig] = None,
        **kwargs,
    ) -> 'AsyncPostgres':
        if config is None:
            config = PostgresConfig(**kwargs)

        url = config.async_url
        if url not in cls._instances:
            cls._locks[url] = asyncio.Lock()
            async with cls._locks[url]:
                if url not in cls._instances:
                    pg_instance = cls(config)
                    await pg_instance.connect()
                    cls._instances[url] = pg_instance

        return cls._instances[url]

    @property
    def url(self) -> str:
        return self._config.async_url

    async def init(self) -> None:
        if self._async_engine is None:
            self._async_engine = self._create_async_engine()
            self._async_session_maker = self._create_async_session_maker()

    def _create_async_engine(self) -> AsyncEngine:
        return create_async_engine(
            url=self.url,
            echo=self._config.echo_log,
            pool_size=self._config.pool_size,
            max_overflow=self._config.pool_overflow,
            pool_timeout=self._config.timeout,
        )

    def _create_async_session_maker(self) -> async_sessionmaker:
        if not self._async_engine:
            raise PGEngineInitializationError(url=self.url)
        return async_sessionmaker(
            bind=self._async_engine,
            expire_on_commit=self._config.expire_on_commit,
            class_=AsyncSession,
            autoflush=self._config.autoflush,
        )

    @contextlib.asynccontextmanager
    async def get_or_create_session(self) -> AsyncSession:
        await self.init()
        async with self._async_session_maker() as session:
            try:
                yield session
                await session.commit()
            except SQLAlchemyError as e:
                await session.rollback()
                raise PGSessionCreationError(url=self.url, message=str(e))
            finally:
                await session.close()

    async def connect(self) -> None:
        await self.init()
        try:
            async with self._async_engine.begin() as connection:
                await connection.run_sync(lambda conn: None)
        except SQLAlchemyError as e:
            raise PGConnectionError(url=self.url, message=str(e))

    async def disconnect(self) -> None:
        if self._async_engine:
            await self._async_engine.dispose()
            self._async_engine = None
