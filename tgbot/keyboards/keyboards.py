from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from tgbot.database.requests import get_tokens_id, get_token_id, get_pages_id

main = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Мои токены', callback_data='get_tokens')]])
add_check_token = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text='Добавить токен', callback_data='add_token')],
                     [InlineKeyboardButton(text='Выбрать токен', callback_data='check_token')]])
only_add = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text='Добавить токен', callback_data='add_token')]])
stopping_add_token = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text='Остановить добавление токена', callback_data='to_main')]])
to_main = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="В главную", callback_data='to_main')]])


async def delete_token_and_add_page(token):
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text='Удалить токен', callback_data=f'delete_token_{token}'),
                          InlineKeyboardButton(text="В главную", callback_data='to_main'),
                          InlineKeyboardButton(text='Добавить страницу', callback_data=f'add_page_{token}')],
                         [InlineKeyboardButton(text='Все подключенные страницы',
                                               callback_data=f'get_page_list_{token}')]])


async def build_tokens_id(user_id):
    keyboard = InlineKeyboardBuilder()
    ids = await get_tokens_id(user_id)
    for i in ids:
        keyboard.add(InlineKeyboardButton(text=str(i[0]), callback_data=f'tokens_id_{i[0]}'))
    keyboard.add(InlineKeyboardButton(text="В главную", callback_data='to_main'))
    return keyboard.adjust(3).as_markup(resize_keyboard=True)


async def token_page(token):
    id = await get_token_id(token)
    to_token_page = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text='Назад', callback_data=f'tokens_id_{id}')]])
    return to_token_page


async def build_pages_id(token):
    keyboard = InlineKeyboardBuilder()
    id = await get_token_id(token)
    ids = await get_pages_id(token)
    for i in ids:
        keyboard.add(InlineKeyboardButton(text=str(i[0]), callback_data=f'pages_id_{i[0]}'))
    keyboard.add(InlineKeyboardButton(text="В главную", callback_data=f'tokens_id_{id}'))
    return keyboard.adjust(3).as_markup(resize_keyboard=True)


async def page_delete(id):
    to_delete_page = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text='Удалить', callback_data=f'delete_page_{id}'),InlineKeyboardButton(text="Добавить запись", callback_data=f'add_data_to_page_{id}')]])
    return to_delete_page
