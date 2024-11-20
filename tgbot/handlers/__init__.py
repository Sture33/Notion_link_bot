from aiogram import Router, F
from aiogram.filters import CommandStart

from .commands import start_command_handler, get_tokens_handler, add_token, setting_token_handler, main_page, \
    check_token, show_token, delete_token_handler, add_page, set_page, get_page_list, show_page, delete_page_handler, \
    set_state_for_set_data, get_state_title_and_set_state_url, get_state_url_and_set_state_category, \
    get_state_category_adn_set_state_priority, get_finish
from ..states.states import SetToken, SetPage, SetData


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
    router.callback_query.register(set_state_for_set_data, F.data.func(lambda data: data.startswith('add_data_to_page_')))
    router.message.register(get_state_title_and_set_state_url, SetData.title)
    router.message.register(get_state_url_and_set_state_category, SetData.url)
    router.message.register(get_state_category_adn_set_state_priority, SetData.category)
    router.message.register(get_finish, SetData.priority)

    return router
