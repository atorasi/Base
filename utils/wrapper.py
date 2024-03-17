import asyncio

from .logger_file import logger

from config import ATTEMPTS_COUNT

def script_exceptions(func):
    async def wrapper(*args, **kwargs):
        try_counter = 0
        while try_counter < ATTEMPTS_COUNT:
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logger.error(f"An error was occured {str(e)}")
                await asyncio.sleep(45)
                logger.info(f"Sleeping 45 seconds and try again. Try counter: {try_counter}")
                try_counter += 1

    return wrapper