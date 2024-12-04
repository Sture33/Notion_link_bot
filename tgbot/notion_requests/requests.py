import asyncio

from notion_client import AsyncClient
from notion_client.errors import APIResponseError


async def is_valid_notion_token(token):
    notion = AsyncClient(auth=token)
    try:
        await notion.users.me()
        return True
    except APIResponseError as e:
        return False


async def create_table(page_id, token, title):
    notion = AsyncClient(auth=token)
    database_data = {
        "parent": {"type": "page_id", "page_id": page_id},
        "title": [{"type": "text", "text": {"content": f"{title}"}}],
        "properties": {
            "Title": {"title": {}},
            "Url": {"url": {}},
            "Category": {"rich_text": {}},
            "Source": {"rich_text": {}},
            "Priority": {
                "select": {
                    "options": [
                        {"name": "Low", "color": "gray"},
                        {"name": "Medium", "color": "yellow"},
                        {"name": "High", "color": "red"}
                    ]
                }
            }
        },
    }
    database = await notion.databases.create(**database_data)
    database_id = database["id"]
    return database_id


async def check_page_access(token, page_id):
    notion = AsyncClient(auth=token)

    try:
        response = await notion.pages.retrieve(page_id=page_id)
        return True
    except APIResponseError as e:
        if e.status == 404:
            return '404'
        elif e.status == 403:
            return '403'
        elif e.status == 400:
            return '400'
    finally:
        await notion.aclose()


async def add_record(token, database_id, title, url, category, priority, source):
    notion = AsyncClient(auth=token)
    page_data = {
        "parent": {"database_id": database_id},
        "properties": {
            "Title": {"title": [{"type": "text", "text": {"content": title}}]},
            "Url": {"url": url},
            "Category": {"rich_text": [{"type": "text", "text": {"content": category}}]},
            "Source": {"rich_text": [{"type": "text", "text": {"content": source}}]},
            "Priority": {"select": {"name": priority}},
        },
    }
    page = await notion.pages.create(**page_data)
    return page
