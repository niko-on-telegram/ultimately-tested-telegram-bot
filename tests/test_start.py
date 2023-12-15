import random
import string

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from main import (
    StartReply,
    process_start_request,
    DeleteReply,
    Action,
    ActionType,
    StartRequest,
)


def test_process_start_request():
    random_str = "".join(random.choices(string.ascii_uppercase, k=20))
    target_user_id = 100500
    target_msg_id = 123
    start_reply = StartReply(
        user_id=target_user_id,
        reply_text="Hello",
        keyboard=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text=random_str)]], resize_keyboard=True
        ),
    )
    delete_reply = DeleteReply(user_id=target_user_id, message_id=target_msg_id)
    target_actions = [
        Action(type=ActionType.SEND_MSG, reply_object=start_reply),
        Action(type=ActionType.DELETE_MSG, reply_object=delete_reply),
    ]
    assert target_actions == process_start_request(
        StartRequest(
            full_name=random_str, user_id=target_user_id, message_id=target_msg_id
        )
    )
