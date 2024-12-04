from aiogram.fsm.state import StatesGroup, State


class SetToken(StatesGroup):
    user_id = State()
    token = State()


class SetPage(StatesGroup):
    token = State()
    page = State()


class SetTable(StatesGroup):
    title = State()
    page_id = State()


class SetCategory(StatesGroup):
    title = State()
    database_id = State()


class SetRecord(StatesGroup):
    database_id = State()
    title = State()
    url = State()
    category = State()
    source = State()
    priority = State()
