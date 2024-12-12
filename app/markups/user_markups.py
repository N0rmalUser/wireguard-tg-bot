from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.markups import keyboard_factory
from app.markups.keyboard_factory import ConfigCallbackFactory
from app.misc.texts import Btn


def start():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=Btn.new_config, callback_data="new_config"),
            ],
            [
                InlineKeyboardButton(text=Btn.profile, callback_data="profile"),
            ],
        ]
    )


def profile(configs: list[list[str]]):
    builder = InlineKeyboardBuilder()
    for i in configs:
        builder.button(
            text=str(i[1]),
            callback_data=ConfigCallbackFactory(
                ip=i[0],
            ),
        )
    builder.adjust(3)
    rows = [len(row) for row in builder.as_markup().inline_keyboard]
    rows.append(1)
    builder.button(text=Btn.back, callback_data="back_to_start")
    builder.adjust(*rows)
    return builder.as_markup()


def config():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=Btn.new_name, callback_data="new_name"),
            ],
            [
                InlineKeyboardButton(text=Btn.add_port, callback_data="add_port"),
                InlineKeyboardButton(text=Btn.delete_port, callback_data="delete_port"),
            ],
            [
                InlineKeyboardButton(text=Btn.back, callback_data="back_to_profile"),
            ],
        ]
    )


def config_settings(ip: str):
    builder = InlineKeyboardBuilder()
    builder.button(text=Btn.back, callback_data=ConfigCallbackFactory(ip=ip))
    return builder.as_markup()
