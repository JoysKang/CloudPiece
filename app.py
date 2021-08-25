import os

from fastapi import FastAPI
from pydantic import BaseModel, Field
from aiogram import Bot
from aiogram.dispatcher import Dispatcher

from utils.write import write


app = FastAPI()

environ = os.environ
API_TOKEN = environ.get("token")
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


class Message(BaseModel):
    message_id: int
    from_field: dict = Field(alias='from')
    chat: dict
    date: int
    text: str


@app.post("/echo")
async def echo(message: Message):
    write(message.text)
    await bot.send_message(message.chat.get("id"), "已存储")

    return {"message": "Success"}


@app.get("/")
def root():
    return {"message": "Success"}
