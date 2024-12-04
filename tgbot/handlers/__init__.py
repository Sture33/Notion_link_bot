from aiogram import Router, F
from aiogram.filters import CommandStart

from .commands import start_command_handler, get_tokens_handler, add_token, setting_token_handler, main_page, \
    check_token, show_token, delete_token_handler, add_page, set_page, get_page_list, show_page, delete_page_handler, \
    add_table_to_page, set_tables_title, show_tables, tables_page_hnd, delete_table_hnd, add_category_hnd, \
    set_title_to_category, set_url, get_url_and_set_category, get_category_and_set_priority, \
    get_priority_and_create_data
from ..states.states import SetToken, SetPage, SetTable, SetCategory, SetRecord


def setup() -> Router:
    router = Router()

    router.message.register(start_command_handler, CommandStart())
    router.callback_query.register(get_tokens_handler, F.data == "get_tokens")
    router.callback_query.register(add_token, F.data == 'add_token')
    router.message.register(setting_token_handler, SetToken.token)
    router.callback_query.register(main_page, F.data == 'to_main')
    router.callback_query.register(check_token, F.data == 'check_token')
    router.callback_query.register(show_token, F.data.func(lambda data: data.startswith('tokens_id_')))
    router.callback_query.register(delete_token_handler, F.data.func(lambda data: data.startswith('delete_token_')))
    router.callback_query.register(add_page, F.data.func(lambda data: data.startswith('add_page_')))
    router.message.register(set_page, SetPage.page)
    router.callback_query.register(get_page_list, F.data.func(lambda data: data.startswith('get_page_list_')))
    router.callback_query.register(show_page, F.data.func(lambda data: data.startswith('pages_id_')))
    router.callback_query.register(delete_page_handler, F.data.func(lambda data: data.startswith('delete_page_')))
    router.callback_query.register(add_table_to_page, F.data.func(lambda data: data.startswith('add_table_to_page_')))
    router.message.register(set_tables_title, SetTable.title)
    router.callback_query.register(show_tables, F.data.func(lambda data: data.startswith('pages_tables_')))
    router.callback_query.register(tables_page_hnd, F.data.func(lambda data: data.startswith('table_id_')))
    router.callback_query.register(delete_table_hnd, F.data.func(lambda data: data.startswith('delete_table_')))
    router.callback_query.register(add_category_hnd, F.data.func(lambda data: data.startswith('add_categories_')))
    router.message.register(set_title_to_category, SetCategory.title)
    router.callback_query.register(set_url, F.data.func(lambda data: data.startswith('add_tables_data_')))
    router.message.register(get_url_and_set_category, SetRecord.url)
    router.message.register(get_category_and_set_priority, SetRecord.category)
    router.message.register(get_priority_and_create_data, SetRecord.priority)

    return router