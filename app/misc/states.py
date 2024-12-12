from aiogram.fsm.state import State, StatesGroup


class BroadcastStates(StatesGroup):
    waiting = State()
    sending = State()
    cancel = State()


class NameStates(StatesGroup):
    waiting = State()
    canceled = State()


class PortStates(StatesGroup):
    waiting = State()
    canceled = State()
