import pytest
from asyncpg_client import PostgresConfig

@pytest.fixture
def set_env(monkeypatch):
    # Set up environment variables
    monkeypatch.setenv("POSTGRES_HOST", "test_host")
    monkeypatch.setenv("POSTGRES_PORT", "5433")
    monkeypatch.setenv("POSTGRES_USER", "test_user")
    monkeypatch.setenv("POSTGRES_PASSWORD", "test_password")
    monkeypatch.setenv("POSTGRES_DB", "test_db")
    monkeypatch.setenv("TIMEOUT", "10")
    monkeypatch.setenv("POOL_SIZE", "50")
    monkeypatch.setenv("MAX_POOL_CON", "60")
    monkeypatch.setenv("POOL_OVERFLOW", "15")
    monkeypatch.setenv("ECHO_LOG", "True")
    monkeypatch.setenv("EXPIRE_ON_COMMIT", "False")
    monkeypatch.setenv("AUTO_FLUSH", "False")

@pytest.fixture
def clear_env(monkeypatch):
    # Clear environment variables
    monkeypatch.delenv("POSTGRES_HOST", raising=False)
    monkeypatch.delenv("POSTGRES_PORT", raising=False)
    monkeypatch.delenv("POSTGRES_USER", raising=False)
    monkeypatch.delenv("POSTGRES_PASSWORD", raising=False)
    monkeypatch.delenv("POSTGRES_DB", raising=False)
    monkeypatch.delenv("TIMEOUT", raising=False)
    monkeypatch.delenv("POOL_SIZE", raising=False)
    monkeypatch.delenv("MAX_POOL_CON", raising=False)
    monkeypatch.delenv("POOL_OVERFLOW", raising=False)
    monkeypatch.delenv("ECHO_LOG", raising=False)
    monkeypatch.delenv("EXPIRE_ON_COMMIT", raising=False)
    monkeypatch.delenv("AUTO_FLUSH", raising=False)

def test_default_values(clear_env):
    # Test the default configuration
    config = PostgresConfig()
    assert config.host == "localhost"
    assert config.port == 5432
    assert config.user == "postgres"
    assert config.password == "password"
    assert config.database == "database"
    assert config.timeout == 5
    assert config.pool_size == 100
    assert config.max_pool_con == 80
    assert config.pool_overflow == 20
    assert config.echo_log is False
    assert config.expire_on_commit is True
    assert config.autoflush is True

def test_custom_values(set_env):
    # Test the configuration with custom environment variables
    config = PostgresConfig()
    assert config.host == "test_host"
    assert config.port == 5433
    assert config.user == "test_user"
    assert config.password == "test_password"
    assert config.database == "test_db"
    assert config.timeout == 10
    assert config.pool_size == 50
    assert config.max_pool_con == 60
    assert config.pool_overflow == 15
    assert config.echo_log is True
    assert config.expire_on_commit is False
    assert config.autoflush is False

def test_async_url_generation(set_env):
    config = PostgresConfig()
    expected_url = "postgresql+asyncpg://test_user:test_password@test_host:5433/test_db"
    assert config.async_url == expected_url

def test_sync_url_generation(set_env):
    config = PostgresConfig()
    expected_url = "postgresql://test_user:test_password@test_host:5433/test_db"
    assert config.sync_url == expected_url

def test_custom_url_override(set_env):
    custom_url = "postgresql://custom_user:custom_password@custom_host:5432/custom_db"
    config = PostgresConfig(url=custom_url)
    assert config.url == custom_url
    assert config.sync_url == custom_url
    assert config.async_url == custom_url

def test_invalid_port_type(monkeypatch):
    # Test invalid port type casting
    monkeypatch.setenv("POSTGRES_PORT", "invalid_port")
    with pytest.raises(ValueError):
        PostgresConfig()

def test_invalid_bool_type(monkeypatch):
    # Test invalid boolean type casting
    monkeypatch.setenv("ECHO_LOG", "invalid_bool")
    with pytest.raises(ValueError):
        PostgresConfig()

def test_repr_output(set_env):
    config = PostgresConfig()
    repr_str = repr(config)
    assert "PostgresConfig" in repr_str
    assert "test_host" in repr_str
    assert "test_user" in repr_str

