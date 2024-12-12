import asyncio
import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.exceptions import TelegramBadRequest, TelegramNetworkError, TelegramRetryAfter
from aiogram.types import Message, Update

from app.database.user import UserDatabase


class BanUsersMiddleware(BaseMiddleware):
    """Мидлварь, игнорящий все updates для забаненных пользователей"""

    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any],
    ) -> Any:
        user = UserDatabase(data["event_from_user"].id)
        if user.tg_id():
            if not user.banned:
                return await handler(event, data)
        else:
            return await handler(event, data)


class TopicCreatorMiddleware(BaseMiddleware):
    """Мидлварь, создающий топик пользователя, если он не создан"""

    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any],
    ) -> Any:
        user = UserDatabase(data["event_from_user"].id)
        if (event.message and not event.message.from_user.is_bot) or (
            event.callback_query and not event.callback_query.from_user.is_bot
        ):
            if not user.topic_id:
                from app.bot import topic_create

                if msg := (event.message or event.callback_query):
                    try:
                        await topic_create(msg)
                    except TelegramRetryAfter as e:
                        retry_after = e.retry_after
                        logging.warning(f"Превышен лимит запросов. Повторите попытку через {retry_after} секунд.")
                        await asyncio.sleep(retry_after)
                        return await topic_create(msg)

            return await handler(event, data)
        return


class CallbackTelegramErrorsMiddleware(BaseMiddleware):
    """Мидлварь, обрабатывающая ошибки, возникающие при отправке колбеков в телеграмме"""

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        try:
            await handler(event, data)
        except TelegramBadRequest as e:
            logging.error("TelegramBadRequest")
            if not any(err in str(e) for err in ["message is not modified", "query is too old"]):
                logging.exception(e)
        except TelegramNetworkError as e:
            logging.error("TelegramNetworkError")
