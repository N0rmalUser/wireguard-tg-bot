import logging

from aiogram.exceptions import TelegramForbiddenError
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.markups import admin_markups
from app.misc.states import BroadcastStates

from . import filters, middlewares, states
from .texts import Text


def create_progress_bar(completed: int, total: int) -> str:
    total_blocks = 20
    filled_blocks = int((completed / total) * total_blocks)
    bar = "■" * filled_blocks + "□" * (total_blocks - filled_blocks)
    return f"[{bar}]"


async def send_broadcast_message(msg: Message, state: FSMContext, message_id: int):
    from asyncio import sleep

    from app.database import all_user_ids
    from app.database.user import UserDatabase

    user_ids = all_user_ids()

    sent_count = 0
    total_users = len(user_ids)
    try:
        for user_id in user_ids:
            if await state.get_state() == BroadcastStates.cancel.state:
                await msg.edit_text(text=f"Отправка отменена на {sent_count} из {total_users}")
                break
            if not UserDatabase(user_id).blocked:
                try:
                    await msg.bot.copy_message(
                        chat_id=user_id,
                        from_chat_id=msg.chat.id,
                        message_id=message_id,
                    )
                    sent_count += 1
                    await msg.edit_text(
                        text=f"Отправлено {sent_count} из {total_users} сообщений\n{create_progress_bar(sent_count, total_users)}",
                        reply_markup=admin_markups.cancel_sending,
                    )
                    await sleep(5)
                except TelegramForbiddenError as e:
                    logging.error(f"Пользователь {user_id} заблокировал бота")
                    UserDatabase(user_id).blocked = True
                except Exception as e:
                    logging.error(f"Не удалось отправить сообщение пользователю {user_id}: {e}")
        logging.info(f"Отправлено сообщение {sent_count} пользователям")
        await msg.edit_text(
            f"Рассылка завершена! {sent_count} сообщений прислал пользователям. {total_users - sent_count} заблокировали бота"
        )
    except Exception as e:
        logging.error(e)
        await msg.edit_text(f"Ошибка при отправке сообщения! {sent_count} из {total_users}")
