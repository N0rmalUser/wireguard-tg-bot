from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile

from app.config import CONF_PATH, MAX_CONFIGS
from app.database import get_new_ip
from app.database.config import ConfigDatabase
from app.database.user import UserDatabase
from app.markups import user_markups as kb
from app.markups.keyboard_factory import ConfigCallbackFactory
from app.misc.states import NameStates, PortStates
from app.misc.texts import Text
from app.wireguard import append_to_server_config, create_config

router = Router()


@router.callback_query(F.data == "ignore")
async def ignore_handler(callback: CallbackQuery) -> None:
    await callback.answer()


@router.callback_query(F.data == "back_to_start")
async def back_to_start_handler(callback: CallbackQuery) -> None:
    await callback.message.edit_text(Text.start, reply_markup=kb.start())


@router.callback_query(F.data == "new_config")
async def new_config_handler(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id
    configs = UserDatabase(user_id).configs
    conf_count = len(configs) if configs else 0
    if conf_count >= MAX_CONFIGS:
        await callback.answer(Text.max_config_number.format(MAX_CONFIGS))
    else:
        config = ConfigDatabase(get_new_ip())
        config.user_id = user_id
        create_config(config)
        append_to_server_config(config)
        config.name = Text.default_config_name.format(config.ip, user_id)
        await callback.message.answer_document(FSInputFile(str(CONF_PATH / str(user_id) / f"{config.ip}.conf")))
        await callback.answer()
        del config


@router.callback_query(ConfigCallbackFactory.filter(F.data == "new_name"))
async def new_name(callback: CallbackQuery, callback_data: ConfigCallbackFactory, state: FSMContext):
    await state.set_state(NameStates.waiting)
    await callback.message.edit_text(Text.new_config_name, reply_markup=kb.config_settings(callback_data.ip))


@router.callback_query(F.data == "back_to_config")
async def back_to_config_handler(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(NameStates.canceled)
    await callback.answer()


@router.callback_query(F.data.in_(["profile", "back_to_profile"]))
async def profile_handler(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id
    user = UserDatabase(user_id)
    configs = user.configs
    await callback.message.edit_text(
        Text.profile.format(user_id, user.start_date, len(configs), MAX_CONFIGS, MAX_CONFIGS*5, 1, 1),
        reply_markup=kb.profile(configs),
    )
    await callback.answer()


@router.callback_query(ConfigCallbackFactory.filter(F.data == "add_port"))
async def add_port(callback: CallbackQuery, callback_data: ConfigCallbackFactory, state: FSMContext) -> None:
    await state.set_state(PortStates.waiting)
    await callback.message.edit_text(Text.ports, reply_markup=kb.config_settings(callback_data.ip))


@router.callback_query(ConfigCallbackFactory.filter())
async def config_handler(callback: CallbackQuery, callback_data: ConfigCallbackFactory, state: FSMContext) -> None:
    ip = callback_data.ip
    config = ConfigDatabase(ip)
    await state.update_data(ip=ip)
    await callback.message.edit_text(
        Text.config.format(config.name, ip, config.creation_date, 1), reply_markup=kb.config()
    )
    await callback.answer()
