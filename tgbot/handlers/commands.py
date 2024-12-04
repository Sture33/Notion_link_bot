from aiogram import types
from aiogram.fsm.context import FSMContext

from tgbot import data
from tgbot.data.config import TELEGRAM_CHANNEL_ID
from tgbot.database.requests import set_user, get_users_tokens, set_token, is_uniq_token, get_token, delete_token, \
    is_page, get_pages, add_page_command, get_page_from_id, delete_page, get_page_token_from_id, add_database_to_page, \
    get_pages_tables, get_table, delete_table, add_category, get_categories, get_token_from_database_id
import tgbot.keyboards.keyboards as kb
from tgbot.notion_requests.requests import is_valid_notion_token, check_page_access, create_table, add_record
from tgbot.states.states import SetToken, SetPage, SetTable, SetCategory, SetRecord
from tgbot.third_dir.third_funcs import is_url, fetch_title_from_url, send_message_to_channel, get_source


async def start_command_handler(message: types.Message):
    user_id = message.from_user.id

    if await set_user(user_id):
        await message.answer('С возвращением, выберите действие.', reply_markup=kb.main)
    else:
        await set_user(user_id)
        await message.answer("Привет, выберите действие.", reply_markup=kb.main)


async def get_tokens_handler(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    await callback.answer('')

    tokens = await get_users_tokens(user_id)
    if len(tokens) == 0:
        await callback.message.edit_text('У вас нету токенов', reply_markup=kb.only_add)
    else:
        ans = ['\n'.join(("token's id: " + str(x[0]), "token: " + x[1])) for x in tokens]
        await callback.message.edit_text('\n\n'.join(ans), reply_markup=kb.add_check_token)


async def add_token(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer("")
    await state.set_state(SetToken.token)
    await callback.message.edit_text("Введите токен", reply_markup=kb.stopping_add_token)


async def setting_token_handler(message: types.Message, state: FSMContext):
    await state.update_data(token=message.text)
    await state.update_data(user_id=message.from_user.id)
    data = await state.get_data()
    if await is_uniq_token(data['token'], data['user_id']):
        if await is_valid_notion_token(data['token']):
            await set_token(data['token'], data['user_id'])
            await state.clear()
            await message.answer('Токен успешно добавлен', reply_markup=kb.to_main)
        else:
            await message.answer("Ваш токен инвалид!!\nПожалуйста введите токен снова",
                                 reply_markup=kb.stopping_add_token)
            await state.set_state(SetToken.token)
    else:
        await message.answer("Пожалуйста следите чтобы токены не повторялись\nПожалуйста введите токен снова",
                             reply_markup=kb.stopping_add_token)
        await state.set_state(SetToken.token)


async def main_page(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(None)
    await callback.answer('')

    await callback.message.edit_text('Выберите действие.', reply_markup=kb.main)


async def check_token(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    await callback.answer('')
    tokens = await get_users_tokens(user_id)
    ans = ['\n'.join(("token's id: " + str(x[0]), "token: " + x[1])) for x in tokens]
    await callback.message.edit_text(f'{'\n\n'.join(ans)}\nВыберите токена по его id',
                                     reply_markup=await kb.build_tokens_id(user_id))


async def show_token(callback: types.CallbackQuery):
    await callback.answer('')
    id = callback.data
    token = await get_token(int(id.replace('tokens_id_', '')))
    await callback.message.edit_text(f'token: {token}', reply_markup=await kb.delete_token_and_add_page(token))


async def delete_token_handler(callback: types.CallbackQuery):
    await callback.answer('')
    data = callback.data
    token = data.replace('delete_token_', '')
    result = await delete_token(token)
    if result:
        await callback.message.edit_text('Успешно удалено', reply_markup=kb.to_main)
    else:
        await callback.message.edit_text('!Успешно удалено', reply_markup=kb.to_main)


async def add_page(callback: types.CallbackQuery, state: FSMContext):
    data = callback.data
    token = data.replace('add_page_', '')
    await state.update_data(token=token)
    await state.set_state(SetPage.page)
    await callback.message.edit_text('Введите id страницы', reply_markup=await kb.token_page(token))


async def set_page(message: types.Message, state: FSMContext):
    await state.update_data(page=message.text)
    data = await state.get_data()
    page_check = await check_page_access(data['token'], data['page'])
    if page_check == True:
        if await is_page(data['page']):
            await message.answer("Пожалуйста следите чтобы токены не повторялись\nПожалуйста введите id снова",
                                 reply_markup=await kb.token_page(data['token']))
            await state.set_state(SetPage.page)
        else:
            await add_page_command(data['token'], data['page'])
            await state.clear()
            await message.answer('Страница успешно добавлено', reply_markup=await kb.token_page(data['token']))
    elif page_check == '404':
        await message.answer('Такой страницы не существует или это не страница!!!\nПожалуйста введите id снова',
                             reply_markup=await kb.token_page(data['token']))
        await state.set_state(SetPage.page)
    elif page_check == '403':
        await message.answer('Это не ваша страница!!!\nПожалуйста введите id снова',
                             reply_markup=await kb.token_page(data['token']))
        await state.set_state(SetPage.page)
    elif page_check == '400':
        await message.answer('Введите корректный id страницы!!!\nПожалуйста введите id снова',
                             reply_markup=await kb.token_page(data['token']))
        await state.set_state(SetPage.page)


async def get_page_list(callback: types.CallbackQuery):
    await callback.answer('')
    token = callback.data.replace('get_page_list_', '')
    pages = await get_pages(token)
    if len(pages) == 0:
        await callback.message.edit_text('Подключенных страниц пока что нету!', reply_markup=await kb.token_page(token))
    else:
        ans = ['\n'.join(("page's id: " + str(x[0]), "page api: " + x[1])) for x in pages]
        await callback.message.edit_text(f'{'\n\n'.join(ans)}\nВыберите страницы по его id',
                                         reply_markup=await kb.build_pages_id(token))


async def show_page(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer('')
    id = callback.data.replace('pages_id_', '')
    page = await get_page_from_id(int(id))
    await callback.message.edit_text(f'id: {page[0][0]}\npage id: {page[0][1]}',
                                     reply_markup=await kb.page_delete(int(id)))


async def delete_page_handler(callback: types.CallbackQuery):
    await callback.answer('')
    id = callback.data.replace('delete_page_', '')
    result = await delete_page(int(id))
    if result:
        await callback.message.edit_text('Успешно удалено', reply_markup=kb.to_main)
    else:
        await callback.message.edit_text('!Успешно удалено', reply_markup=kb.to_main)


async def add_table_to_page(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer('')
    page_id = callback.data.replace('add_table_to_page_', '')
    page = await get_page_from_id(int(page_id))
    await state.set_state(SetTable.title)
    await state.update_data(page_id=page)
    await callback.message.edit_text('Введите title для таблицы', reply_markup=kb.to_main)


async def set_tables_title(message: types.Message, state: FSMContext):
    title = message.text
    await state.update_data(title=title)
    data = await state.get_data()
    token, page = await get_page_token_from_id(data['page_id'][0][0])
    database_id = await create_table(page, token, title)
    await add_database_to_page(title, data['page_id'][0][0], database_id)
    await state.clear()
    await message.answer('Успех наверное', reply_markup=await kb.to_page_main(data['page_id'][0][0]))


async def show_tables(callback: types.CallbackQuery):
    page_id = callback.data.replace('pages_tables_', '')
    tables = await get_pages_tables(int(page_id))
    if len(tables) == 0:
        await callback.message.edit_text('Подключенных таблиц пока что нету!',
                                         reply_markup=await kb.to_page_main(int(page_id)))
    else:
        ans = ['\n'.join(("tables's id: " + str(x[0]), "table id from notion: " + x[1])) for x in tables]
        await callback.message.edit_text(f'{'\n\n'.join(ans)}\nВыберите таблицу по его id',
                                         reply_markup=await kb.build_tables_id(int(page_id)))


async def tables_page_hnd(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer('')
    await state.clear()
    table_id = callback.data.replace('table_id_', '')
    table = await get_table(int(table_id))
    await callback.message.edit_text(text=f'table id: {table[0][0]}\ntable id from notion: {table[0][1]}',
                                     reply_markup=await kb.tables_kbs(table[0][0], table[0][2]))


async def delete_table_hnd(callback: types.CallbackQuery):
    await callback.answer('')
    id = callback.data.replace('delete_table_', '')
    page_id = await get_table(int(id))
    await delete_table(int(id))
    await callback.message.edit_text(text='Удалено', reply_markup=await kb.to_page_main(page_id[0][2]))


async def add_category_hnd(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(SetCategory.title)
    await callback.answer('')
    id = callback.data.replace('add_categories_', '')
    await state.update_data(database_id=id)
    await callback.message.edit_text(text='Введите название', reply_markup=await kb.to_table_main(id))


async def set_title_to_category(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    data = await state.get_data()
    await add_category(int(data['database_id']), data['title'])
    await state.clear()
    await message.answer(text='Вроде успех', reply_markup=await kb.to_table_main(data['database_id']))


async def set_url(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer('')
    await state.clear()
    id = callback.data.replace('add_tables_data_', '')
    await state.update_data(database_id=id)
    cats = await get_categories(int(id))
    if len(cats) > 0:
        await state.set_state(SetRecord.url)
        await callback.message.edit_text(text='Введите url', reply_markup=await kb.to_table_main(id))
    else:
        await callback.message.edit_text(text='Сначало добавьте несколько category',
                                         reply_markup=await kb.to_table_main(id))


async def get_url_and_set_category(message: types.Message, state: FSMContext):
    m = message.text
    isurl = await is_url(m)
    print(isurl)
    id = await state.get_data()

    if isurl:
        await state.update_data(url=m)
        await state.set_state(SetRecord.category)
        await message.answer('Введите category', reply_markup=await kb.cat_builder(id['database_id']))
    else:
        await message.answer('Введите корректный url.\nВведите url снова',
                             reply_markup=await kb.to_table_main(id['database_id']))
        await state.set_state(SetRecord.url)


async def get_category_and_set_priority(message: types.Message, state: FSMContext):
    m = message.text
    id = await state.get_data()
    cats = [x[1] for x in await get_categories(int(id['database_id']))]
    if m in cats:
        await state.update_data(category=m)
        await state.set_state(SetRecord.priority)
        await message.answer('Введите priority', reply_markup=kb.priority_kbs)
    else:
        await message.answer('Введите корректный category.\nВведите category снова',
                             reply_markup=await kb.to_table_main(id['database_id']))
        await state.set_state(SetRecord.category)


async def get_priority_and_create_data(message: types.Message, state: FSMContext):
    m = message.text
    id = await state.get_data()
    priorities = ['Low', 'Medium', 'High']
    bot = message.bot
    if m in priorities:
        await state.update_data(priority=m)
        data = await state.get_data()
        print(await state.get_data())
        token = await get_token_from_database_id(int(data['database_id']))
        database_id = await get_table(int(data['database_id']))
        title = await fetch_title_from_url(data['url'])
        source = await get_source(data['url'])
        page = await add_record(token[0][0], database_id[0][1], title, data['url'], data['category'], data['priority'],
                                source)
        await send_message_to_channel(page, bot, TELEGRAM_CHANNEL_ID)
        if page is not None:
            await message.answer('Вроде успех, наверное.', reply_markup=await kb.to_table_main(data['database_id']))
    else:
        await message.answer('Введите корректный priority.\nВведите priority снова',
                             reply_markup=await kb.to_table_main(id['database_id']))
        await state.set_state(SetRecord.priority)
