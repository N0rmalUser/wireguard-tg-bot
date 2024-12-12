import asyncio
import logging

from aiogram import Router
from aiogram.exceptions import TelegramRetryAfter
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from app.config import ADMIN_CHAT_ID
from app.database.user import UserDatabase
from app.markups import user_markups as kb
from app.misc.filters import ChatTypeIdFilter
from app.misc.texts import Err, Text

router = Router()


@router.message(CommandStart(), ChatTypeIdFilter(chat_type=["private"]))
async def start_handler(msg: Message):
    from app.bot import topic_create

    user = UserDatabase(msg.from_user.id)

    if user.allowed:
        return await msg.answer(Text.start, reply_markup=kb.start())

    await msg.answer(Text.not_allowed)
    if not user.topic_id:
        user.username = f"@{msg.from_user.username}"
        user.fullname = msg.from_user.full_name
        try:
            await topic_create(msg)
        except TelegramRetryAfter as e:
            retry_after = e.retry_after
            logging.warning(Err.retry_after.format(retry_after))
            await asyncio.sleep(retry_after)
            return await topic_create(msg)


@router.message(Command("admin"), ChatTypeIdFilter(chat_type=["private"]))
async def admin_handler(msg: Message) -> None:
    from app.bot import process_track

    user = UserDatabase(msg.from_user.id)
    user.tracking = True

    logging.warning(Err.help.format(msg.from_user.id, msg.from_user.username))
    await process_track(
        user=user,
        text=Err.help.format(msg.from_user.id, msg.from_user.username),
        bot=msg.bot,
    )
    await msg.forward(chat_id=ADMIN_CHAT_ID, message_thread_id=user.topic_id)
    await msg.answer(Text.admin)


@router.message(ChatTypeIdFilter(chat_type=["private"]))
async def handler(msg: Message) -> None:
    user = UserDatabase(msg.from_user.id)
    if user.tracking:
        await msg.forward(ADMIN_CHAT_ID, message_thread_id=user.topic_id)
