from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

admin_menu = [
    [
        KeyboardButton(text="/log"),
        KeyboardButton(text="/track start"),
        KeyboardButton(text="/track stop"),
    ],
    [KeyboardButton(text="/dump"), KeyboardButton(text="/info")],
]

cancel_sending = [[InlineKeyboardButton(text="❌ Отменить отправку", callback_data="cancel_sending")]]

admin_menu = ReplyKeyboardMarkup(keyboard=admin_menu, resize_keyboard=True)
cancel_sending = InlineKeyboardMarkup(inline_keyboard=cancel_sending)
