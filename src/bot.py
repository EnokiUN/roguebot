from os import getenv
from typing import cast

from aiomysql import create_pool
from disnake.ext import commands
from redis.asyncio import ConnectionPool

from .aiomysql_patches import MariaDBPool


class Bot(commands.InteractionBot):
    db_pool: MariaDBPool
    cache: ConnectionPool

    async def start(
        self,
        token: str,
        *,
        reconnect: bool = True,
        ignore_session_start_limit: bool = False,
    ) -> None:
        # mysql://(user):(password)@(host):(port)/(db)
        if not (db := getenv("DB")):
            raise ValueError("Could not find DB environment variable")
        user, host = db[8:].split("@")
        user, password = user.split(":")
        host, db = host.split("/")
        host, port = host.split(":") if ":" in host else (host, "3306")
        self.db_pool = cast(
            MariaDBPool,
            await create_pool(
                host=host,
                port=int(port),
                user=user,
                password=password,
                db=db,
                autocommit=True,
            ),
        )

        # redis://(host):(port)/(db)
        if not (cache := getenv("CACHE")):
            raise ValueError("Could not find CACHE environment variable")
        url = cache[8:]
        host, db = url.split("/") if "/" in url else (url, None)
        host, port = host.split(":") if ":" in host else (host, "6379")
        self.cache = ConnectionPool(
            host=host, port=int(port), db=(int(db) if db is not None else None)
        )
        return await super().start(
            token,
            reconnect=reconnect,
            ignore_session_start_limit=ignore_session_start_limit,
        )
