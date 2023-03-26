import logging
from asyncio import run
from os import getenv

from dotenv import load_dotenv

from .bot import Bot
from .logging import setup_logger

logger = logging.getLogger(__name__)


async def main():
    bot = Bot()

    @bot.event
    async def on_ready(): # pyright: ignore
        logger.info("Started as %s", bot.user)

    load_dotenv()

    if not (token := getenv("TOKEN")):
        raise ValueError("Could not find TOKEN environment variable")

    setup_logger()

    bot.load_extensions("./src/plugins")

    await bot.start(token)


if __name__ == "__main__":
    run(main())
