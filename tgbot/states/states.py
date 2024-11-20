from aiogram.fsm.state import StatesGroup, State


class SetToken(StatesGroup):
    user_id = State()
    token = State()


class SetPage(StatesGroup):
    token = State()
    page = State()

class SetData(StatesGroup):
    page_api = State()
    token = State()
    title = State()
    url = State()
    category = State()
    priority = State()
