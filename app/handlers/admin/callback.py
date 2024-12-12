from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from app.misc.states import BroadcastStates

router = Router()


@router.callback_query(F.data == "cancel_send")
async def confirm_send(callback_query: CallbackQuery):
    await callback_query.answer("Отправка отменена.")
    await callback_query.message.delete()


@router.callback_query(F.data == "cancel_sending")
async def cancel_sending(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BroadcastStates.cancel)
    await callback.answer("Отправка будет остановлена.")
    await callback.message.delete_reply_markup()
