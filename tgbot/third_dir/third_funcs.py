import logging
import re
from datetime import datetime
from urllib.parse import urlparse

import aiohttp
from bs4 import BeautifulSoup

url_regex = re.compile(
    r'^(https?:\/\/)'
    r'(([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,})'
    r'(\/[^\s]*)?$',
    re.IGNORECASE
)


async def is_url(url: str):
    return bool(url_regex.match(url))


async def fetch_title_from_url(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    domain = urlparse(url).hostname
                    return f"{domain} - HTTP {response.status}"

                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                title = soup.title.string.strip() if soup.title else None

                if title:
                    return title
                else:
                    domain = urlparse(url).hostname
                    return f"{domain} - Заголовок не найден"
    except Exception as e:
        domain = urlparse(url).hostname
        return f"{domain} - Ошибка: {e}"


async def send_message_to_channel(msg, bot, channel_id):
    try:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"Дата отправки: {current_time}\n{msg}"
        await bot.send_message(chat_id=channel_id, text=message)
    except Exception as e:
        logging.error(f"Ошибка при отправке сообщения: {e}")


def get_source_from_url(url):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.lower()

    if 't.me' in domain or 'telegram.me' in domain:
        return "Telegram"
    elif 'facebook.com' in domain:
        return "Facebook"
    elif 'instagram.com' in domain:
        return "Instagram"
    elif 'twitter.com' in domain:
        return "Twitter"
    elif 'youtube.com' in domain:
        return "YouTube"
    else:
        return "Unknown"


def get_telegram_source(url):
    if 't.me' in url or 'telegram.me' in url:
        match = re.search(r't.me/([a-zA-Z0-9_]+)', url)
        if match:
            return match.group(1)
    return "Unknown"


def get_source(url):
    source = get_source_from_url(url)

    if source == "Telegram":
        telegram_source = get_telegram_source(url)
        return f"Telegram - {telegram_source}"

    return source
