from aiogram import types
from aiogram.fsm.context import FSMContext
from tgbot.database.requests import set_user, get_users_tokens, set_token, is_uniq_token, get_token, delete_token, \
    is_page, get_pages, add_page_command, get_page_from_id, delete_page, get_page_token_from_id
import tgbot.keyboards.keyboards as kb
from tgbot.notion_requests.requests import is_valid_notion_token, check_page_access, add_data
from tgbot.states.states import SetToken, SetPage, SetData


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
    await callback.message.edit_text('Введите api страницы', reply_markup=await kb.token_page(token))


async def set_page(message: types.Message, state: FSMContext):
    await state.update_data(page=message.text)
    data = await state.get_data()
    page_check = await check_page_access(data['token'], data['page'])
    if page_check == True:
        if await is_page(data['page']):
            await message.answer("Пожалуйста следите чтобы токены не повторялись\nПожалуйста введите api снова",
                                 reply_markup=await kb.token_page(data['token']))
            await state.set_state(SetPage.page)
        else:
            await add_page_command(data['token'], data['page'])
            await state.clear()
            await message.answer('Страница успешно добавлено', reply_markup=await kb.token_page(data['token']))
    elif page_check == '404':
        await message.answer('Такой страницы не существует или это не страница!!!\nПожалуйста введите api снова',
                             reply_markup=await kb.token_page(data['token']))
        await state.set_state(SetPage.page)
    elif page_check == '403':
        await message.answer('Это не ваша страница!!!\nПожалуйста введите api снова',
                             reply_markup=await kb.token_page(data['token']))
        await state.set_state(SetPage.page)
    elif page_check == '400':
        await message.answer('Введите корректный api страницы!!!\nПожалуйста введите api снова',
                             reply_markup=await kb.token_page(data['token']))
        await state.set_state(SetPage.page)


async def get_page_list(callback: types.CallbackQuery):
    await callback.answer('')
    token = callback.data.replace('get_page_list_', '')
    pages = await get_pages(token)
    await callback.message.edit_text('da')
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
    await callback.message.edit_text(f'id: {page[0][0]}\napi: {page[0][1]}', reply_markup=await kb.page_delete(int(id)))


async def delete_page_handler(callback: types.CallbackQuery):
    await callback.answer('')
    id = callback.data.replace('delete_page_', '')
    result = await delete_page(int(id))
    if result:
        await callback.message.edit_text('Успешно удалено', reply_markup=kb.to_main)
    else:
        await callback.message.edit_text('!Успешно удалено', reply_markup=kb.to_main)


async def set_state_for_set_data(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer('')
    id = callback.data.replace('add_data_to_page_', '')
    token, page_api = await get_page_token_from_id(int(id))
    await state.update_data(token=token)
    await state.update_data(page_api=page_api)
    await state.set_state(SetData.title)
    await callback.message.edit_text('Пожалуйста введите заголовок: ')


async def get_state_title_and_set_state_url(message: types.Message, state: FSMContext):
    await state.set_state(SetData.url)
    await state.update_data(title=message.text)
    await message.answer('Пожалуйста введите url: ')


async def get_state_url_and_set_state_category(message: types.Message, state: FSMContext):
    await state.set_state(SetData.category)
    await state.update_data(url=message.text)
    await message.answer('Пожалуйста введите категорию: ')


async def get_state_category_adn_set_state_priority(message: types.Message, state: FSMContext):
    await state.set_state(SetData.priority)
    await state.update_data(category=message.text)
    await message.answer('Пожалуйста введите приоритет: ')


async def get_finish(message: types.Message, state: FSMContext):
    await state.update_data(priority=message.text)
    data = await state.get_data()
    finish = await add_data([data['title'],data['url'],data['category'],data['priority']], data['page_api'], data['token'])
    if finish:
        await message.answer('Успех')
    else:
        await message.answer('!!!Успех')
    await state.clear()
