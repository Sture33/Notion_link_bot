from tgbot.models.models import async_session, User, NotionToken, Page, Table, Category
from sqlalchemy import select, delete


async def set_user(user_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.user_id == user_id))

        if not user:
            session.add(User(user_id=user_id))
            await session.commit()
        else:
            return True


async def is_uniq_token(token, user_id):
    async with async_session() as session:
        tokens = await session.scalar(select(NotionToken.token).where(NotionToken.token == token))
        if tokens is None:
            return True
        else:
            return False


async def set_token(token, user_id):
    async with async_session() as session:
        id = await session.scalar(select(User.id).where(User.user_id == user_id))
        session.add(NotionToken(token=token, user_id=id))
        await session.commit()


async def get_users_tokens(user_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.user_id == user_id))
        tokens = await session.execute(select(NotionToken.id, NotionToken.token).where(NotionToken.user_id == user.id))

        return tokens.all()


async def get_tokens_id(user_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.user_id == user_id))
        ids = await session.execute(select(NotionToken.id).where(NotionToken.user_id == user.id))

        return ids.all()


async def get_token(id):
    async with async_session() as session:
        token = await session.scalar(select(NotionToken.token).where(NotionToken.id == id))
        return token


async def get_token_id(token):
    async with async_session() as session:
        id = await session.scalar(select(NotionToken.id).where(NotionToken.token == token))
        return id


async def delete_token(token):
    async with async_session() as session:
        istoken = await session.execute(select(NotionToken.token).where(NotionToken.token == token))
        if istoken:
            await session.execute(delete(NotionToken).where(NotionToken.token == token))
            await session.commit()
            return True
        else:
            return False


async def add_page_command(token, page_api):
    async with async_session() as session:
        token_id = await session.scalar(select(NotionToken.id).where(NotionToken.token == token))
        session.add(Page(token=token_id, page_api=page_api))
        await session.commit()


async def is_page(page_api):
    async with async_session() as session:
        res = await session.scalar(select(Page.page_api == page_api))
        if res:
            return True
        else:
            return False


async def get_pages(token):
    async with async_session() as session:
        token_id = await session.scalar(select(NotionToken.id).where(NotionToken.token == token))
        pages = await session.execute(select(Page.id, Page.page_api).where(Page.token == token_id))
        return pages.all()


async def get_pages_id(token):
    async with async_session() as session:
        token_id = await session.scalar(select(NotionToken.id).where(NotionToken.token == token))
        pages = await session.execute(select(Page.id).where(Page.token == token_id))
        return pages.all()


async def get_page_from_id(id):
    async with async_session() as session:
        page = await session.execute(select(Page.id, Page.page_api).where(Page.id == id))
        return page.all()


async def get_page_token_from_id(id):
    async with async_session() as session:
        page_api = await session.scalar(select(Page.page_api).where(Page.id == id))
        token = await session.scalar(select(NotionToken.token).where(
            NotionToken.id == await session.scalar(select(Page.token).where(Page.id == id))))
        return token, page_api


async def delete_page(id):
    async with async_session() as session:
        ispage = await session.execute(select(Page.id).where(Page.id == id))
        if ispage:
            await session.execute(delete(Page).where(Page.id == id))
            await session.commit()
            return True
        else:
            return False


async def add_database_to_page(title, page_id, database_id):
    async with async_session() as session:
        session.add(Table(title=title, page_id=page_id, database_id=database_id))
        await session.commit()


async def get_pages_tables(page_id):
    async with async_session() as session:
        tables = await session.execute(select(Table.id, Table.database_id).where(Table.page_id == page_id))
        return tables.all()


async def get_pages_tables_id(page_id):
    async with async_session() as session:
        tables = await session.execute(select(Table.id).where(Table.page_id == page_id))
        return tables.all()


async def get_table(id):
    async with async_session() as session:
        table = await session.execute(select(Table.id, Table.database_id, Table.page_id).where(Table.id == id))
        return table.all()


async def delete_table(id):
    async with async_session() as session:
        istable = await session.execute(select(Table.id).where(Table.id == id))
        if istable:
            await session.execute(delete(Table).where(Table.id == id))
            await session.commit()
            return True
        else:
            return False


async def add_category(database_id, title):
    async with async_session() as session:
        session.add(Category(database_id=database_id, title=title))
        await session.commit()


async def get_categories(database_id):
    async with async_session() as session:
        cats = await session.execute(select(Category.id, Category.title).where(Category.database_id == database_id))
        return cats.all()


async def get_token_from_database_id(id):
    async with async_session() as session:
        page_id = await session.execute(select(Table.page_id).where(Table.id == id))
        token_id = await session.execute(select(Page.token).where(Page.id == page_id.all()[0][0]))
        token = await session.execute(select(NotionToken.token).where(NotionToken.id == token_id.all()[0][0]))
        return token.all()
