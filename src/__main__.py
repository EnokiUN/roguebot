from asyncio import run
from os import getenv

from dotenv import load_dotenv

from .bot import Bot
from .logging import setup_logger


async def main():
    bot = Bot()

    load_dotenv()

    if not (token := getenv("TOKEN")):
        raise ValueError("Could not find TOKEN environment variable")

    setup_logger()

    bot.load_extensions("./src/plugins")

    await bot.start(token)


if __name__ == "__main__":
    run(main())
