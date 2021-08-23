import json
import asyncio

from aiogram import Bot

from utils.conf import load_json

conf = load_json("./conf.json")
BOT_TOKEN = conf.get("telegram_token")


async def main():
    bot = Bot(token=BOT_TOKEN)

    try:
        me = await bot.get_me()
        print(f"🤖 Hello, I'm {me.first_name}.\nHave a nice Day!")
    finally:
        await bot.close()

asyncio.run(main())
