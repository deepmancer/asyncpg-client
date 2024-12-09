# 📚 Async Postgres Client

<p align="center">
    <img src="https://img.shields.io/badge/PostgreSQL-4169E1.svg?style=for-the-badge&logo=PostgreSQL&logoColor=white" alt="PostgreSQL">
    <img src="https://img.shields.io/badge/SQLAlchemy-D71F00.svg?style=for-the-badge&logo=SQLAlchemy&logoColor=white" alt="SQLAlchemy">
    <img src="https://img.shields.io/badge/Pydantic-E92063.svg?style=for-the-badge&logo=Pydantic&logoColor=white" alt="Pydantic">
    <img src="https://img.shields.io/badge/PyPI-3775A9.svg?style=for-the-badge&logo=PyPI&logoColor=white" alt="PyPI">
    <img src="https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54" alt="Python">
    <img src="https://img.shields.io/badge/license-Apache%202.0-blue.svg?style=for-the-badge" alt="License">
</p>

**`asyncpg-client`** is a powerful Python package designed for seamless asynchronous interactions with PostgreSQL, leveraging SQLAlchemy. It ensures efficient, thread-safe operations with its singleton-based connection pooling mechanism, making database management easier and faster.

---

| **Source Code** | **Website** |
|:-----------------|:------------|
| <a href="https://github.com/deepmancer/asyncpg-client" target="_blank">github.com/deepmancer/asyncpg-client</a> | <a href="https://deepmancer.github.io/asyncpg-client/" target="_blank">deepmancer.github.io/asyncpg-client</a> |

---

## ✨ Features

- ⚡ **Asynchronous Operations**: Asynchronous database connections using SQLAlchemy for high performance.
- 🛠️ **Singleton Pattern**: Efficiently manage database connections using a singleton design.
- 🔄 **Context Manager Support**: Simplify database session management with context managers.
- 🔧 **Easy Configuration**: Configure your database effortlessly with `PostgresConfig`.

## 📦 Installation

Get started quickly by installing `asyncpg-client` with pip:

```sh
pip install git+https://github.com/deepmancer/asyncpg-client.git
```

## 📝 Usage Guide

### 🔧 Configuration

Start by creating a configuration object with `PostgresConfig`:

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

### 🏗️ Creating an AsyncPostgres Instance

Next, create an instance of `AsyncPostgres` using your configuration:

```python
from asyncpg_client import AsyncPostgres

async def main():
    pg_client = await AsyncPostgres.create(config=config)
    print(pg_client.async_url)
    print(pg_client.sync_url)
```

### ⚙️ Managing Database Sessions

Interact with your PostgreSQL database using the context manager from `get_or_create_session`:

```python
from asyncpg_client import AsyncPostgres

async def main():
    pg_client = await AsyncPostgres.create(config=config)

    async with pg_client.get_or_create_session() as session:
        # Interact with your database here
        pass

    await pg_client.disconnect()
```

### 🔍 Example Usage

Here's a basic example to demonstrate how `asyncpg-client` works:

```python
import asyncio
from asyncpg_client import AsyncPostgres, PostgresConfig

async def main():
    config = PostgresConfig(
        host='localhost',
        port=5432,
        user='your_user',
        password='your_password',
        database='your_database'
    )
    pg_client = await AsyncPostgres.create(config=config)

    async with pg_client.get_or_create_session() as session:
        # Perform your database operations here
        pass

    await pg_client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
```

### 🛡️ Error Handling

Handle various database-related errors gracefully with custom exceptions:

- `PGConnectionError`
- `PGSessionCreationError`
- `PGEngineInitializationError`

### 🛑 Disconnecting

Ensure a clean disconnect from your PostgreSQL database:

```python
await pg_client.disconnect()
```

## 📄 License

This project is licensed under the Apache License 2.0. See the [LICENSE](https://github.com/deepmancer/asyncpg-client/blob/main/LICENSE) file for full details.
