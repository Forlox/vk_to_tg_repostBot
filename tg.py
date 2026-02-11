import os
import asyncio
from aiogram import Bot
from aiogram.types import FSInputFile, InputMediaPhoto
import json

TG_TIMINGS = {
    'DELAY_BETWEEN_REQUESTS': 1,  # Задержка между запросами к API Telegram (сек)
    'DELAY_BETWEEN_MESSAGES': 1,  # Задержка между отправкой сообщений (сек)
    'CONNECTION_TIMEOUT': 30,  # Таймаут подключения (сек)
}

with open('API_KEYS.json', 'r', encoding='utf-8') as f:
    API = json.load(f)

API_TOKEN = API['tg']['API_TOKEN']
CHANNEL_ID = API['tg']['CHANNEL_ID']

bot = Bot(token=API_TOKEN)


async def post(folder_path):
    bot = Bot(token=API_TOKEN)

    try:
        text_file_path = os.path.join(folder_path, "text")
        with open(text_file_path, 'r', encoding='utf-8') as f:
            caption_text = f.read()

        all_files = os.listdir(folder_path)

        media_files = [
            f for f in all_files
            if f not in ["media", "text"]
               and os.path.isfile(os.path.join(folder_path, f))
        ]

        if media_files:
            media_group = []

            for i, filename in enumerate(media_files):
                file_path = os.path.join(folder_path, filename)

                if i == 0:
                    media_group.append(
                        InputMediaPhoto(
                            media=FSInputFile(file_path),
                            caption=caption_text
                        )
                    )
                else:
                    media_group.append(
                        InputMediaPhoto(
                            media=FSInputFile(file_path)
                        )
                    )

            await asyncio.sleep(TG_TIMINGS['DELAY_BETWEEN_REQUESTS'])
            await bot.send_media_group(
                chat_id=CHANNEL_ID,
                media=media_group,
                request_timeout=TG_TIMINGS['CONNECTION_TIMEOUT']
            )
            await asyncio.sleep(TG_TIMINGS['DELAY_BETWEEN_MESSAGES'])

        else:
            await asyncio.sleep(TG_TIMINGS['DELAY_BETWEEN_REQUESTS'])
            await bot.send_message(
                chat_id=CHANNEL_ID,
                text=caption_text,
                request_timeout=TG_TIMINGS['CONNECTION_TIMEOUT']
            )
            await asyncio.sleep(TG_TIMINGS['DELAY_BETWEEN_MESSAGES'])

    finally:
        await bot.session.close()