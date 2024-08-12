import pytest
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock

from unittest.mock import AsyncMock, patch, MagicMock, PropertyMock
from sqlalchemy.exc import SQLAlchemyError

from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, AsyncConnection
from asyncpg_client.config import PostgresConfig
from asyncpg_client.client import AsyncPostgres
from asyncpg_client.exceptions import PGConnectionError, PGSessionCreationError, PGEngineInitializationError



@pytest.fixture
def postgres_config():
    return PostgresConfig(
        async_url="postgresql+asyncpg://user:password@localhost/dbname",
        echo_log=False,
        pool_size=5,
        pool_overflow=10,
        timeout=30,
        expire_on_commit=False,
        autoflush=True
    )

@pytest.mark.asyncio
@patch.object(AsyncPostgres, '_initialize_connection', new_callable=AsyncMock)
async def test_create_instance(mock_initialize_connection, postgres_config):
    instance = await AsyncPostgres.create(config=postgres_config)
    assert isinstance(instance, AsyncPostgres)
    assert instance.url == postgres_config.async_url
    mock_initialize_connection.assert_awaited_once()

@pytest.mark.asyncio
async def test_engine_and_session_creation(postgres_config):
    instance = await AsyncPostgres.create(config=postgres_config)

    with patch.object(instance, '_create_async_engine', return_value=AsyncMock()) as mock_engine, \
         patch.object(instance, '_create_async_session_maker', return_value=AsyncMock()) as mock_session_maker:

        await instance._init_engine_and_session()

        mock_engine.assert_called_once()
        mock_session_maker.assert_called_once()

@pytest.mark.asyncio
async def test_get_or_create_session_success(postgres_config):
    instance = await AsyncPostgres.create(config=postgres_config)

    session_mock = AsyncMock()
    with patch.object(instance, 'get_or_create_session', return_value=AsyncMock(__aenter__=AsyncMock(return_value=session_mock), __aexit__=AsyncMock())) as mock_session_context:
        async with instance.get_or_create_session() as session:
            assert session == session_mock

        mock_session_context.assert_called_once()

@pytest.mark.asyncio
async def test_disconnect(postgres_config):
    instance = await AsyncPostgres.create(config=postgres_config)

    with patch.object(instance, '_async_engine', AsyncMock()) as mock_engine:
        await instance.disconnect()
        mock_engine.dispose.assert_awaited_once()

@pytest.mark.asyncio
async def test_reconnect(postgres_config):
    instance = await AsyncPostgres.create(config=postgres_config)

    with patch.object(instance, 'disconnect', new_callable=AsyncMock) as mock_disconnect, \
         patch.object(instance, '_initialize_connection', new_callable=AsyncMock) as mock_initialize:

        await instance.reconnect()
        mock_disconnect.assert_awaited_once()
        mock_initialize.assert_awaited_once()