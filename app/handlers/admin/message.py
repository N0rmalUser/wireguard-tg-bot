import logging

from aiogram import F, Router
from aiogram.enums import ContentType
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile, Message
from pytz import timezone as tz

from app.config import ADMIN_CHAT_ID, LOG_FILE, TIME_FORMAT, TIMEZONE, USERS_DB
from app.database import get_all_users_info, get_tracked_users, tracking_manage, user_info
from app.database.user import UserDatabase
from app.markups import admin_markups as kb
from app.misc import Text, send_broadcast_message
from app.misc.filters import ChatTypeIdFilter

router = Router()


@router.message(
    Command("menu"),
    ChatTypeIdFilter(chat_type=["group", "supergroup"], chat_id=ADMIN_CHAT_ID),
)
async def handle_topic_command_track(msg: Message) -> None:
    await msg.answer("Меню админа", reply_markup=kb.admin_menu)


@router.message(
    Command("ban"),
    ChatTypeIdFilter(chat_type=["group", "supergroup"], chat_id=ADMIN_CHAT_ID),
)
async def ban_command_handler(msg: Message) -> None:
    user = UserDatabase(topic_id=msg.message_thread_id)
    user.banned = True
    user.allowed = False
    await msg.answer("Мы его забанили!!!")
    await msg.bot.send_message(user.tg_id(), "За нарушение правил, тебя забанили")
    logging.info(f"Забанен юзверь {user.tg_id()}")


@router.message(
    Command("unban"),
    ChatTypeIdFilter(chat_type=["group", "supergroup"], chat_id=ADMIN_CHAT_ID),
)
async def ban_command_handler(msg: Message) -> None:
    user = UserDatabase(topic_id=msg.message_thread_id)
    user.banned = False
    await msg.answer("Мы его разбанили!!!")
    await msg.bot.send_message(user.tg_id(), "Амнистия! Тебя разбанили")
    logging.info(f"Разбанен юзверь {user.tg_id()}")


@router.message(
    Command("dump"),
    ChatTypeIdFilter(chat_type=["group", "supergroup"], chat_id=ADMIN_CHAT_ID),
)
async def dump_handler(msg: Message) -> None:
    try:
        await msg.answer_document(FSInputFile(LOG_FILE), caption="Вот ваш лог")
        open(LOG_FILE, "w").write("")
        logging.info("Выгружены и отчищены логи")
    except Exception as e:
        logging.error("Ошибка при отчистке логов", e)
    try:
        await msg.answer_document(FSInputFile(USERS_DB), caption="Вот ваша база данных")
        logging.info("Выгружена база данных пользователей")
    except Exception as e:
        logging.error("Ошибка при выгрузке базы данных пользователей", e)


@router.message(
    Command("log"),
    ChatTypeIdFilter(chat_type=["group", "supergroup"], chat_id=ADMIN_CHAT_ID),
)
async def dump_handler(msg: Message) -> None:
    try:
        await msg.answer_document(FSInputFile(LOG_FILE), caption="Вот ваши логи")
        open(LOG_FILE, "w").write("")
        logging.info("Выгружены и отчищены логи")
    except Exception as e:
        logging.error("Ошибка при выгрузке логов", e)


@router.message(
    Command("track"),
    ChatTypeIdFilter(chat_type=["group", "supergroup"], chat_id=ADMIN_CHAT_ID),
)
async def handle_topic_command_track(msg: Message, command: CommandObject) -> None:
    if command.args is None:
        await msg.answer("Ошибка: не переданы аргументы")
        return

    command = str(command.args).lower()
    start = await msg.answer("Подождите...")

    if start.message_thread_id:
        user = UserDatabase(topic_id=msg.message_thread_id)
        if command == "start":
            user.tracking = True
        elif command == "stop":
            user.tracking = False
        elif command == "status":
            pass
        await start.edit_text(f"Трекинг {'включен' if user.tracking else 'выключен'}")
    else:
        if command == "start":
            await tracking_manage(True)
            await start.edit_text("Трекинг включен для всех пользователей")
        elif command == "stop":
            await tracking_manage(False)
            await start.edit_text("Трекинг выключен для всех пользователей")
        elif command == "status":
            users = await get_tracked_users()
            tracked = "\n".join([str(user) for user in users])
            await start.edit_text(f"Трекаются: \n" + tracked if users else "Никто не трекается")


@router.message(
    Command("info"),
    ChatTypeIdFilter(chat_type=["group", "supergroup"], chat_id=ADMIN_CHAT_ID),
)
async def handle_topic_command_info(msg: Message, command: CommandObject = None) -> None:
    start = await msg.answer(text="Собираю статистику")
    if command.args is None:
        if start.message_thread_id:
            await start.edit_text(text=await user_info(UserDatabase(topic_id=msg.message_thread_id)))
        else:
            await start.edit_text(text=get_all_users_info())
    else:
        await start.edit_text(await user_info(UserDatabase(int(command.args))))


@router.message(
    Command("allow"),
    ChatTypeIdFilter(chat_type=["group", "supergroup"], chat_id=ADMIN_CHAT_ID),
)
async def handle_topic_command_info(msg: Message) -> None:
    user = UserDatabase(topic_id=msg.message_thread_id)
    user.allowed = True
    await msg.bot.send_message(user.tg_id(), Text.allowed)
    user.start_date = msg.date.astimezone(tz(TIMEZONE)).strftime(TIME_FORMAT)
    await msg.answer(Text.user_allowed)


@router.message(
    ChatTypeIdFilter(chat_type=["group", "supergroup"], chat_id=ADMIN_CHAT_ID),
    F.content_type.in_(
        {
            ContentType.TEXT,
            ContentType.PHOTO,
            ContentType.VIDEO,
            ContentType.AUDIO,
            ContentType.VOICE,
            ContentType.DOCUMENT,
            ContentType.STICKER,
            ContentType.VIDEO_NOTE,
            ContentType.STORY,
        }
    ),
)
async def handle_topic_message(msg: Message, state: FSMContext) -> None:
    if msg.from_user.is_bot:
        return

    if msg.text and msg.text.startswith("/"):
        await msg.answer("Нет такой команды, но я тебя спас, не бойся")
        return

    if msg.message_thread_id is not None:
        chat_id = UserDatabase(topic_id=msg.message_thread_id).tg_id()
        await msg.bot.copy_message(
            chat_id=chat_id,
            from_chat_id=msg.chat.id,
            message_id=msg.message_id,
        )
        await msg.bot.send_message(chat_id=chat_id, text=msg.text)
    else:
        await send_broadcast_message(msg, state, msg.message_id)
