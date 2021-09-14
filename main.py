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
from utils.notion import write, create, update, get_data, get_database_id, delete_relation
from utils.encryption import AESCipher

conf = load_json("./conf.json")
API_TOKEN = conf.get("telegram_token")
CLIENT_ID = conf.get("client_id")
CLIENT_SECRET = conf.get("client_secret")
REDIRECT_URI = conf.get("redirect_uri")
AES = AESCipher(conf.get("key"))

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


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    text = """
      欢迎使用【CloudPiece】      
    CloudPiece 能够快速记录你的想法到 Notion 笔记中
    1. 请拷贝 [模板](https://joys.notion.site/fa90a1d7e8404e1286f66941dafd4155) 到自己的 Notion 中 
    2. 使用 /bind 命令授权 CloudPiece 访问，在授权页面选择你刚刚拷贝的模板(注：错误的选择将无法正常使用 CloudPiece)
    3. 输入 test ，你将收到 【已存储】的反馈，这时你的想法已经写入到 Notion，快去 Notion 看看吧~
    
    如果 CloudPiece 不能使你满意，你可以到 [反馈页面](https://joys.notion.site/CloudPiece-feedback-3cb2307641184267a6ad7f4f1e97d5a9) 进行反馈, 
    或者直接使用 /unbind 进行解绑
    """
    chat_id = str(message.chat.id)
    return SendMessage(chat_id=chat_id, text=text, parse_mode="Markdown", disable_web_page_preview=True)


@dp.message_handler(commands=['bind'])
async def bind(message: types.Message):
    """绑定"""
    username = message.chat.username
    chat_id = str(message.chat.id)
    state = AES.encrypt(chat_id)    # 加密
    reply_message = f"授权地址: https://api.notion.com/v1/oauth/authorize?client_id={CLIENT_ID}" \
                    f"&redirect_uri={REDIRECT_URI}" \
                    "&response_type=code" \
                    f"&state={state}"
    if not create(name=username, chat_id=chat_id):
        return SendMessage(chat_id, "已绑定")

    return SendMessage(chat_id, reply_message)


@dp.message_handler(commands=['unbind'])
async def unbind(message: types.Message):
    """解除绑定(删除 relation关系 )"""
    chat_id = str(message.chat.id)
    delete_relation(chat_id)

    return SendMessage(chat_id, "解绑完成，如需继续使用，请先使用 /bind 进行绑定")


@dp.message_handler()
async def echo(message: types.Message):
    chat_id = message.chat.id
    text = message.text

    database_id, access_token, _ = get_data(chat_id)
    if not (database_id or access_token):
        return SendMessage(chat_id, "database_id or access_token lack")

    if write(database_id, access_token, text):
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
    code = request.rel_url.query["code"]
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI
    }

    authorization = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode("utf-8")).decode("utf-8")
    headers = {
        'content-type': 'application/json',
        'Authorization': f'Basic {authorization}'
    }
    result = requests.post('https://api.notion.com/v1/oauth/token', json=data, headers=headers)
    if result.status_code != 200:
        print(result.content, "----")
        return web.json_response({"message": "Failure"})

    json_data = result.json()
    # 根据 chat_id、code、json_data 更新数据库
    access_token = json_data.get('access_token')
    database_id = get_database_id(access_token)

    state = request.rel_url.query["state"]
    chat_id = AES.decrypt(state)  # 解密
    update(chat_id=chat_id, access_token=access_token, database_id=database_id, code=code)

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
