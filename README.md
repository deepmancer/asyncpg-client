# asyncpg-client

`asyncpg-client` is a Python package that provides an asynchronous PostgreSQL client using SQLAlchemy. It also offers a singleton-based connection pooling mechanism, ensuring efficient and thread-safe database operations.

# Features

- Asynchronous database connections using SQLAlchemy.
- Singleton design pattern to manage database connections.
- Context manager support for database sessions.
- Easy configuration using `PostgresConfig`.

## Installation

To install `asyncpg-client`, use pip:

```sh
pip install git+https://github.com/deepmancer/asyncpg-client.git
```
# Usage

Here's a basic example of how to use the `AsyncPostgres` class in your project:

## Configuration

First, create a configuration object using `PostgresConfig`:

```python
from asyncpg_client import PostgresConfig

config = PostgresConfig(
    host='localhost',
    port=5432,
    user='your_user',
    password='your_password',
    database='your_database',
    url=None,  # Optional: Direct database URL
    enable_db_echo_log=False,
    enable_db_expire_on_commit=False
)
```

## Creating an AsyncPostgres Instance
You can create an instance of AsyncPostgres using the configuration:

```python
from asyncpg_client import AsyncPostgres

async def main():
    pg_client = await AsyncPostgres.create(config=config)
    print(pg_client.async_url)
    print(pg_client.sync_url)
```

## Using Database Sessions
To interact with the database, use the context manager provided by get_or_create_session:

```python
from asyncpg_client import AsyncPostgres

async def main():
    pg_client = await AsyncPostgres.create(config=config)

    async with pg_client.get_or_create_session() as session:
        # Use `session` to interact with your database
        pass

    await pg_client.disconnect()
```

## Error Handling
The package provides custom exceptions to handle various database-related errors:

- `PGConnectionError`
- `PGSessionCreationError`
- `PGEngineInitializationError`

## Disconnecting
To gracefully disconnect from the database:

```python
await pg_client.disconnect()
```

# License
This project is licensed under the Apache License 2.0. See the [LICENSE](https://github.com/deepmancer/asyncpg-client/blob/main/LICENSE) file for more details.
