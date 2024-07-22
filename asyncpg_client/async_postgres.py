import contextlib
import threading
from typing import Dict, Optional

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)

from .exceptions import PGConnectionError, PGSessionCreationError, PGEngineInitializationError


class AsyncPostgres:
    _instances: Dict[str, 'AsyncPostgres'] = {}
    _locks: Dict[str, threading.Lock] = {}

    def __new__(cls, url: str, *args, **kwargs) -> 'AsyncPostgres':
        if url not in cls._locks:
            cls._locks[url] = threading.Lock()
        with cls._locks[url]:
            if url not in cls._instances:
                instance = super().__new__(cls)
                cls._instances[url] = instance
            return cls._instances[url]

    def __init__(self, url: str, echo: bool = False, expire_on_commit: bool = False):
        if not hasattr(self, 'initialized'):
            self.url = url
            self.echo = echo
            self.expire_on_commit = expire_on_commit
            self._async_engine: Optional[AsyncEngine] = None
            self._async_session_maker: Optional[async_sessionmaker] = None
            self.initialized = True

    async def init(self) -> None:
        if self._async_engine is None:
            self._async_engine = self._create_async_engine()
            self._async_session_maker = self._create_async_session_maker()

    def _create_async_engine(self) -> AsyncEngine:
        return create_async_engine(
            url=self.url,
            echo=self.echo,
        )

    def _create_async_session_maker(self) -> async_sessionmaker:
        if not self._async_engine:
            raise PGEngineInitializationError(url=self.url)
        return async_sessionmaker(
            bind=self._async_engine,
            expire_on_commit=self.expire_on_commit,
            class_=AsyncSession,
        )

    @contextlib.asynccontextmanager
    async def get_or_create_session(self) -> AsyncSession:
        await self.init()
        session = self._async_session_maker()
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise PGSessionCreationError(url=self.url, message=str(e))
        finally:
            await session.close()

    async def connect(self) -> None:
        await self.init()
        try:
            async with self._async_engine.begin() as connection:
                await connection.run_sync(lambda conn: None)
        except Exception as e:
            raise PGConnectionError(url=self.url, message=str(e))

    async def disconnect(self) -> None:
        if self._async_engine:
            await self._async_engine.dispose()
