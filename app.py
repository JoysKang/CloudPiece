import os

from fastapi import FastAPI

from utils.write import write
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher

app = FastAPI()

environ = os.environ
API_TOKEN = environ.get("token")
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# webhook settings
WEBHOOK_HOST = environ.get("domain")
WEBHOOK_PATH = environ.get("path")
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"


@app.get("/startup")
async def startup():
    await bot.set_webhook(WEBHOOK_URL)
    return {"message": "Success"}


@app.get("/shutdown")
async def shutdown():
    await bot.delete_webhook()

    await dp.storage.close()
    await dp.storage.wait_closed()

    return {"message": "Success"}


@dp.message_handler()
async def echo(message: types.Message):
    write(message.text)
    await message.answer(message.text)

    return {"message": "Success"}


@app.get("/")
def root():
    return {"message": "Success"}
