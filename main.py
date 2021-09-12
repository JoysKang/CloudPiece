import logging
import base64

import requests
from aiohttp import web
from aiogram import Bot, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.webhook import SendMessage
from aiogram.utils.executor import set_webhook

from utils.conf import load_json
from utils.notion import write, update_or_create, get_data

conf = load_json("./conf.json")
API_TOKEN = conf.get("telegram_token")
CLIENT_ID = conf.get("client_id")
CLIENT_SECRET = conf.get("client_secret")
REDIRECT_URI = conf.get("redirect_uri")

# webhook settings
WEBHOOK_HOST = 'https://service-8povhv40-1257855910.sg.apigw.tencentcs.com/release'
WEBHOOK_PATH = '/echo'
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# webserver settings
WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = 9000

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())


@dp.message_handler(commands=['database_id'])
async def send_welcome(message: types.Message):
    """授权"""
    # notion 记录 chat_id & database_id 的关系
    chat_id = message.chat.id
    print(chat_id, "chat_id")
    reply_message = "写入成功"
    await message.reply(reply_message)


@dp.message_handler(commands=['bind'])
async def send_welcome(message: types.Message):
    """授权"""
    reply_message = f"授权地址: https://api.notion.com/v1/oauth/authorize?client_id={CLIENT_ID}" \
                    f"&redirect_uri={REDIRECT_URI}" \
                    "&response_type=code"
    await message.reply(reply_message)


@dp.message_handler()
async def echo(message: types.Message):
    chat_id = message.chat.id
    text = message.text

    database_id, code = get_data(chat_id)
    if write(database_id, code, text):
        await bot.send_message(chat_id, "已存储")
        return SendMessage(chat_id, "已存储")


async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL)


async def on_shutdown(dp):
    logging.warning('Shutting down..')

    await bot.delete_webhook()

    await dp.storage.close()
    await dp.storage.wait_closed()

    logging.warning('Bye!')


async def auth(request):
    """授权回调"""
    # 向 https://api.notion.com/v1/oauth/token 发起请求
    host = request.headers.get("Host")
    code = request.rel_url.query["code"]
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": f"{host}/auth"
    }

    authorization = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode("utf-8")).decode("utf-8")
    headers = {
        'content-type': 'application/json',
        'Authorization': f'Basic {authorization}'
    }
    result = requests.post('https://api.notion.com/v1/oauth/token', json=data, headers=headers)
    if result.status_code != 200:
        print(result.content)
        return web.json_response({"message": "Failure"})

    json_data = result.json()
    # 根据 chat_id、code、json_data 更新数据库

    return web.json_response({"message": "Success"})


# web_app
web_app = web.Application()
web_app.add_routes([web.get('/auth', auth)])


if __name__ == '__main__':
    executor = set_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        web_app=web_app
    )
    executor.run_app(host=WEBAPP_HOST,
                     port=WEBAPP_PORT)
