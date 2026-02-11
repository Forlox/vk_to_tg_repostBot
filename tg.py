import os
import asyncio
from aiogram import Bot
from aiogram.types import FSInputFile, InputMediaPhoto
import json
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

            await bot.send_media_group(
                chat_id=CHANNEL_ID,
                media=media_group
            )

        else:
            await bot.send_message(
                chat_id=CHANNEL_ID,
                text=caption_text
            )

    finally:
        await bot.session.close()