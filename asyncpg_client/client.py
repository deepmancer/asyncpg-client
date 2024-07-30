import contextlib
import asyncio
from typing import Dict, Optional, AsyncIterator

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
        url: str = config.async_url
        if url not in cls._locks:
            cls._locks[url] = asyncio.Lock()
        if url not in cls._instances:
            cls._instances[url] = super().__new__(cls)
        return cls._instances[url]

    def __init__(self, config: PostgresConfig) -> None:
        if not hasattr(self, '_initialized') or not self._initialized:
            self._config: PostgresConfig = config
            self._async_engine: Optional[AsyncEngine] = None
            self._async_session_maker: Optional[async_sessionmaker[AsyncSession]] = None
            self._initialized: bool = True

    @classmethod
    async def create(cls, config: Optional[PostgresConfig] = None, **kwargs) -> 'AsyncPostgres':
        if config is None:
            config = PostgresConfig(**kwargs)
        url: str = config.async_url
        async with cls._locks[url]:
            if url not in cls._instances:
                instance = cls(config)
                await instance._initialize_connection()
                cls._instances[url] = instance
        return cls._instances[url]

    async def _initialize_connection(self) -> None:
        await self._init_engine_and_session()
        await self._test_connection()

    async def _init_engine_and_session(self) -> None:
        if self._async_engine is None:
            self._async_engine = self._create_async_engine()
            self._async_session_maker = self._create_async_session_maker()

    def _create_async_engine(self) -> AsyncEngine:
        return create_async_engine(
            url=self._config.async_url,
            echo=self._config.echo_log,
            pool_size=self._config.pool_size,
            max_overflow=self._config.pool_overflow,
            pool_timeout=self._config.timeout,
        )

    def _create_async_session_maker(self) -> async_sessionmaker[AsyncSession]:
        if not self._async_engine:
            raise PGEngineInitializationError(url=self._config.async_url)
        return async_sessionmaker(
            bind=self._async_engine,
            expire_on_commit=self._config.expire_on_commit,
            class_=AsyncSession,
            autoflush=self._config.autoflush,
        )

    @contextlib.asynccontextmanager
    async def get_or_create_session(self) -> AsyncIterator[AsyncSession]:
        await self._init_engine_and_session()
        if not self._async_session_maker:
            raise PGSessionCreationError(url=self._config.async_url)

        async with self._async_session_maker() as session:
            try:
                yield session
                if session.in_transaction():
                    await session.commit()
            except SQLAlchemyError as e:
                await session.rollback()
                raise PGSessionCreationError(url=self._config.async_url, message=str(e))
            finally:
                await session.close()

    async def _test_connection(self) -> None:
        try:
            async with self._async_engine.begin() as connection:
                await connection.run_sync(lambda conn: None)
        except SQLAlchemyError as e:
            raise PGConnectionError(url=self._config.async_url, message=str(e))

    async def disconnect(self) -> None:
        if self._async_engine:
            await self._async_engine.dispose()
            self._async_engine = None

    async def reconnect(self) -> None:
        await self.disconnect()
        await self._initialize_connection()

    @property
    def url(self) -> str:
        return self._config.async_url
