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


async def add_data(datas, page_api, token):
    notion = AsyncClient(auth=token)

    async def prepare_page_block(fields, page_id):
        return {
            "parent": {"page_id": page_id},
            "children": [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": fields[0],
                                    "link": {"url": fields[1]},
                                },
                            }
                        ]
                    },
                },
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {"content": f"    Category: {fields[2]}"},
                            }
                        ]
                    },
                },
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {"content": f"    Priority: {fields[3]}"},
                            }
                        ]
                    },
                },
            ],
        }

    data_to_save = await prepare_page_block(datas, page_api)
    try:
        response = await notion.blocks.children.append(block_id=page_api, children=data_to_save['children'])
        return True
    except Exception as e:

        return False

