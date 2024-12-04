# Notion Link Bot
## Описание
Notion Link Bot — это Telegram-бот, который позволяет добавлять ссылки и другие данные в вашу базу данных Notion через Telegram. Бот получает ссылки, проверяет их и сохраняет в Notion. Он также может обрабатывать различные типы ссылок из популярных социальных сетей, таких как Telegram, Facebook, Instagram и другие.
___
## Технологии
Проект использует следующие технологии:

- Python 3.8+ — основной язык программирования.
- Aiogram — библиотека для взаимодействия с Telegram API.
- Notion API — API для взаимодействия с базой данных Notion.
- Aiohttp — асинхронные HTTP-запросы.
- BetterLogging — для удобного и цветного логирования.
- Orjson — для быстрой сериализации/десериализации JSON.
___

## Установка зависимостей
Создайте виртуальное окружение и установите зависимости:

```
python -m venv venv
source venv/bin/activate  # Для Linux/MacOS
venv\Scripts\activate     # Для Windows
pip install -r requirements.txt
```
___
## Запуск бота
```
python run.py
```
