import asyncio
import logging
from enum import Enum, auto
from typing import Any

from aiogram import Bot, Dispatcher, types, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from pydantic import BaseModel


class ActionType(Enum):
    DELETE_MSG = auto()
    SEND_MSG = auto()


class Action(BaseModel):
    type: ActionType
    reply_object: Any


class DeleteReply(BaseModel):
    user_id: int
    message_id: int


class StartReply(BaseModel):
    reply_text: str
    user_id: int
    keyboard: ReplyKeyboardMarkup


class StartRequest(BaseModel):
    full_name: str
    user_id: int
    message_id: int


async def process_actions(bot: Bot, actions: list[Action]):
    for action in actions:
        reply = action.reply_object
        logging.info(f"Started processing {action.type}")
        match action.type:
            case ActionType.SEND_MSG:
                reply: StartReply
                await bot.send_message(
                    reply.user_id, reply.reply_text, reply_markup=reply.keyboard
                )
            case ActionType.DELETE_MSG:
                reply: DeleteReply
                try:
                    await bot.delete_message(reply.user_id, reply.message_id)
                except TelegramBadRequest:
                    logging.exception("Bad request on delete")
            case _:
                raise RuntimeError("Unexpected")
        logging.info(f"Ended processing {action.type}")


def process_start_request(start_request: StartRequest) -> list[Action]:
    kbd = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=start_request.full_name)]], resize_keyboard=True
    )
    return [
        Action(
            type=ActionType.SEND_MSG,
            reply_object=StartReply(
                user_id=start_request.user_id, reply_text="Hello", keyboard=kbd
            ),
        ),
        Action(
            type=ActionType.DELETE_MSG,
            reply_object=DeleteReply(
                user_id=start_request.user_id, message_id=start_request.message_id
            ),
        ),
    ]


router = Router()


@router.message(CommandStart)
async def start_handler(message: types.Message, bot: Bot):
    logging.info("Got /start in bot")
    start_request = StartRequest(
        full_name=message.from_user.full_name,
        user_id=message.from_user.id,
        message_id=message.message_id,
    )
    reply = process_start_request(start_request)
    await process_actions(bot, reply)
    logging.info("start handler ended")


async def setup_dispatcher(token: str):
    bot = Bot(token)
    storage = MemoryStorage()
    dispatcher = Dispatcher(storage=storage)
    dispatcher.include_router(router)

    return bot, dispatcher


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s: "
               "%(filename)s: "
               "%(levelname)s: "
               "%(funcName)s(): "
               "%(lineno)d:\t"
               "%(message)s",
    )
    bot, dispatcher = await setup_dispatcher("6406671740:AAEDXJHoEnc_ipvuwL5CzsJePEcJFm5Vee8")
    await dispatcher.start_polling(bot)


def run_main():
    asyncio.run(main())


if __name__ == "__main__":
    run_main()
