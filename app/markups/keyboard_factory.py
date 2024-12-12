from typing import Optional

from aiogram.filters.callback_data import CallbackData


class ConfigCallbackFactory(CallbackData, prefix="cnf"):
    ip: Optional[str] = None
