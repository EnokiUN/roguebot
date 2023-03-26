from __future__ import annotations

from collections.abc import Coroutine, Generator
from typing import Any, Protocol, TypeVar

T = TypeVar("T")


class MariaDBPool(Protocol):
    def acquire(self) -> MariaDBContextManager[MariaDBConnection]:
        ...


class MariaDBConnection(Protocol):
    def cursor(self) -> MariaDBContextManager[MariaDBCursor]:
        ...

    async def __aenter__(self) -> MariaDBConnection:
        ...

    async def __aexit__(self, *_): # noqa: ANN002
        ...

    async def commit(self):
        ...

    async def close(self):
        ...


class MariaDBCursor(Protocol):
    async def execute(
        self, query: str, params: tuple[Any, ...] | None = None
    ):
        ...

    async def fetchone(self) -> tuple[Any, ...]:
        ...

    async def fetchall(self) -> list[tuple[Any, ...]]:
        ...

    async def close(self):
        ...


class MariaDBContextManager(Coroutine[Any, Any, T]):
    async def __aenter__(self) -> T:
        ...

    async def __aexit__(self, *_): # noqa: ANN002
        ...

    def __await__(self) -> Generator[Any, Any, T]:
        ...
