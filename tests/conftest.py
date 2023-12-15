import asyncio
import logging
import random

import pytest
import pytest_asyncio
from telethon import TelegramClient
from telethon.errors import PhoneNumberUnoccupiedError

from src.main import setup_dispatcher, router as main_router

api_id = 23685185
api_hash = "7304bafcae249c221ac64eccdbdf1dae"


def raise_(ex):
    raise ex


class PasswordExc(RuntimeError):
    pass


@pytest_asyncio.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def telethon_client() -> TelegramClient:
    while True:
        # noinspection PyTypeChecker
        client = TelegramClient(None, api_id, api_hash)
        # noinspection PyUnresolvedReferences
        client.session.set_dc(1, "149.154.175.10", 80)

        number = "999661" + str(random.randint(1000, 9999))

        try:
            logging.info(f"client trying to start...")

            # noinspection PyTypeChecker
            await asyncio.wait_for(client.start(
                phone=number,
                code_callback=lambda: "1" * 5,
                password=lambda: raise_(PasswordExc()),
            ), 7)
            logging.info(f"client started: {number=}")

            yield client

            await client.disconnect()
            await client.disconnected
            logging.info("Telethon shutdown")
            break
        except (PhoneNumberUnoccupiedError, PasswordExc, TimeoutError) as e:
            logging.info(f"Skipped due to {type(e)}")
            await client.disconnect()
            await client.disconnected
            pass


@pytest.fixture(name="dispatcher", scope="session")
async def dispatcher_fixture():
    dispatcher = create_dispatcher(config=config)
    return dispatcher


@pytest_asyncio.fixture(scope="function", autouse=True)
async def bot_run():
    bot, dispatcher = await setup_dispatcher(
        "5000392029:AAHErtm4OzRPeboQUxDEh1bjLGVxVBYnA1Q/test"
    )
    task = asyncio.create_task(dispatcher.start_polling(bot))
    logging.info("Created task with bot")
    yield
    logging.info("Starting bot shutdown")
    await dispatcher.stop_polling()
    await task
    logging.info("End bot shutdown")
