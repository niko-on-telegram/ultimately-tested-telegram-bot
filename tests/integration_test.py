import logging
from asyncio import Event

import pytest
import pytest_asyncio
from telethon import TelegramClient, types, events
from telethon.tl.custom.message import Message


@pytest_asyncio.fixture
async def signal(telethon_client: TelegramClient):
    stopped_signal = Event()

    logging.info("Setting message handler")

    @telethon_client.on(events.MessageDeleted())
    async def on_msg_delete(event: events.MessageDeleted.Event):
        stopped_signal.set()
        logging.info(f"got on_msg_delete:{event.deleted_ids}, stopped_signal set")

    yield stopped_signal

    logging.info("Removing message handler")

    telethon_client.remove_event_handler(on_msg_delete)


@pytest.mark.asyncio
async def test_start_command(telethon_client: TelegramClient, signal):
    logging.info("Starting test")
    me = await telethon_client.get_me()

    name = me.first_name
    if me.last_name:
        name = f"{me.first_name} {me.last_name}"
    async with telethon_client.conversation("@Endtoendtestbot", timeout=60) as conv:
        logging.info("Sending /start...")
        await conv.send_message("/start")
        resp: Message = await conv.get_response()
        logging.info("Got response!")
        assert "Hello" in resp.raw_text
        target_keyboard = types.ReplyKeyboardMarkup(
            rows=[types.KeyboardButtonRow(buttons=[types.KeyboardButton(text=name)])],
            resize=True,
            persistent=False,
            selective=False,
            single_use=False
        )
        assert resp.reply_markup == target_keyboard
        logging.info("Waiting for signal")
        await signal.wait()
        logging.info("Test finished")
