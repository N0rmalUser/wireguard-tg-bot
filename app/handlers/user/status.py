import logging

from aiogram import Router
from aiogram.filters.chat_member_updated import KICKED, MEMBER, ChatMemberUpdatedFilter
from aiogram.types import ChatMemberUpdated

from app.bot import process_track
from app.database.user import UserDatabase

router = Router()


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=KICKED))
async def user_blocked_bot(event: ChatMemberUpdated):
    """Хендлер для считывания блокировки бота пользователем."""

    user = UserDatabase(event.from_user.id)
    user.blocked = True
    await process_track(
        user=user,
        text=f"Пользователь @{event.from_user.username} заблокировал бота",
        bot=event.bot,
    )
    logging.info(f"Пользователь @{event.from_user.username} заблокировал бота")


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=MEMBER))
async def user_unblocked_bot(event: ChatMemberUpdated):
    """Хендлер для считывания разблокировки бота пользователем."""

    user = UserDatabase(event.from_user.id)
    user.blocked = False
    await process_track(
        user=user,
        text=f"Пользователь @{event.from_user.username} разблокировал бота",
        bot=event.bot,
    )
    logging.info(f"Пользователь @{event.from_user.username} разблокировал бота")
