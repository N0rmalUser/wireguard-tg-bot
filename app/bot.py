import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, Message, ReplyKeyboardMarkup

from app.config import ADMIN_CHAT_ID, BOT_TOKEN
from app.database.user import UserDatabase
from app.handlers import admin, user
from app.markups import admin_markups as kb
from app.misc import middlewares


async def main() -> None:
    session = AiohttpSession()
    from aiogram.enums import ParseMode

    bot = Bot(
        token=BOT_TOKEN,
        session=session,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_routers(
        user.status.router,
        user.callback.router,
        user.message.router,
        admin.message.router,
        admin.callback.router,
    )

    dp.update.middleware(middlewares.BanUsersMiddleware())
    dp.update.middleware(middlewares.TopicCreatorMiddleware())
    dp.callback_query.middleware(middlewares.CallbackTelegramErrorsMiddleware())

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types(), polling_timeout=60)


async def topic_create(msg: Message) -> None:
    user = UserDatabase(msg.from_user.id)
    if msg.from_user.username:
        topic_name = f"{msg.from_user.username} {msg.from_user.id}"
    else:
        topic_name = f"{msg.from_user.full_name} {msg.from_user.id}"
    result = await msg.bot.create_forum_topic(ADMIN_CHAT_ID, topic_name)
    user.topic_id = result.message_thread_id
    user_info = (
        f"Пользователь: <code>{msg.from_user.full_name}</code>\n"
        f"ID: <code>{msg.from_user.id}</code>\n"
        f"Username: @{msg.from_user.username}"
    )
    user.tracking = True
    await process_track(user=user, text=user_info, bot=msg.bot, keyboard=kb.admin_menu)
    user.tracking = False
    logging.info(f"Создан топик имени {msg.from_user.id} @{msg.from_user.username}")


async def process_track(
    user: UserDatabase,
    text: str,
    bot: Bot,
    keyboard: ReplyKeyboardMarkup | InlineKeyboardMarkup | None = None,
    parse_mode: str = "HTML",
) -> None:
    try:
        if user.tracking:
            await bot.send_message(
                ADMIN_CHAT_ID,
                message_thread_id=user.topic_id,
                text=text,
                reply_markup=keyboard,
                parse_mode=parse_mode,
            )
    except Exception as e:
        logging.error("Ошибка при трекинге:\n" + str(e))
