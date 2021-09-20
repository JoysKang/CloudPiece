import logging
import base64

import requests
import sentry_sdk
from aiohttp import web
from aiogram import Bot
from aiogram.types import Message, ContentType
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.webhook import SendMessage
from aiogram.utils.executor import set_webhook

from utils.conf import load_json
from utils.notion import create, update, get_database_id, delete_relation, CloudPiece
from utils.encryption import AESCipher
from utils.latitude import Degree
from utils.telegram import get_total_file_path

conf = load_json("./conf.json")
API_TOKEN = conf.get("telegram_token")
CLIENT_ID = conf.get("client_id")
CLIENT_SECRET = conf.get("client_secret")
REDIRECT_URI = conf.get("redirect_uri")
AES = AESCipher(conf.get("key"))

sentry_sdk.init(
    conf.get("sentry_address"),

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0
)

# webhook settings
WEBHOOK_HOST = conf.get('webhook_host')
WEBHOOK_PATH = '/echo'
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# webserver settings
WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = 9000

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())
unsupported = "暂不支持该消息类型的存储，目前仅支持文本、图片、视频、GIF、文件"


@dp.message_handler(commands=['start'])
async def start(message: Message):
    text = """
      欢迎使用【CloudPiece】      
    CloudPiece 能够快速记录你的想法到 Notion 笔记中
    1. 请拷贝 [模板](https://joys.notion.site/fa90a1d7e8404e1286f66941dafd4155) 到自己的 Notion 中 
    2. 使用 /bind 命令授权 CloudPiece 访问，在授权页面选择你刚刚拷贝的模板(注：错误的选择将无法正常使用 CloudPiece)
    3. 输入 test,你将收到 【已存储】的反馈，这时你的想法已经写入到 Notion，快去 Notion 看看吧~
    
    更详细的教程请看 [使用说明](https://joys.notion.site/CloudPiece-d9c509b20b0d40d4a1076c991416fd2e)
    
    如果 CloudPiece 不能使你满意，你可以到 [github](https://github.com/JoysKang/CloudPiece/issues) 提 issues,
    或到[留言板](https://joys.notion.site/c144f89764564f928c31f162e0ff307a) 留言,
    或发邮件至 licoricepieces@gmail.com, 
    或直接使用 /unbind 进行解绑，然后到拷贝的模板页，点击右上角的 Share 按钮，从里边移除 CloudPiece。
    """
    chat_id = str(message.chat.id)
    return SendMessage(chat_id=chat_id, text=text, parse_mode="Markdown", disable_web_page_preview=True)


@dp.message_handler(commands=['bind'])
async def bind(message: Message):
    """绑定"""
    username = message.chat.username
    chat_id = str(message.chat.id)
    state = AES.encrypt(chat_id)  # 加密
    reply_message = f"授权地址: https://api.notion.com/v1/oauth/authorize?client_id={CLIENT_ID}" \
                    f"&redirect_uri={REDIRECT_URI}" \
                    "&response_type=code" \
                    f"&state={state}"
    if not create(name=username, chat_id=chat_id):
        return SendMessage(chat_id, "已绑定")

    return SendMessage(chat_id, reply_message)


@dp.message_handler(commands=['unbind'])
async def unbind(message: Message):
    """解除绑定(删除 relation关系 )"""
    chat_id = str(message.chat.id)
    delete_relation(chat_id)

    return SendMessage(chat_id, "解绑完成，如需继续使用，请先使用 /bind 进行绑定")


@dp.errors_handler()
async def errors(exception):
    print(exception, "=====")


@dp.message_handler(content_types=ContentType.PHOTO)
async def photo_handler(message: Message):
    """
    {"message_id": 286, "from": {"id": 682824243, "is_bot": false, "first_name": "F", "last_name": "joys", "username": "joyskaren", "language_code": "zh-hans"}, "chat": {"id": 682824243, "first_name": "F", "last_name": "joys", "username": "joyskaren", "type": "private"}, "date": 1631746843, "photo": [{"file_id": "AgACAgUAAxkBAAIBHmFCexuQ1bp0N47YwArKM5YcPdokAAJUrzEbhcgQVmmEKN_iB7NbAQADAgADcwADIAQ", "file_unique_id": "AQADVK8xG4XIEFZ4", "file_size": 1028, "width": 90, "height": 46}, {"file_id": "AgACAgUAAxkBAAIBHmFCexuQ1bp0N47YwArKM5YcPdokAAJUrzEbhcgQVmmEKN_iB7NbAQADAgADbQADIAQ", "file_unique_id": "AQADVK8xG4XIEFZy", "file_size": 9704, "width": 320, "height": 163}, {"file_id": "AgACAgUAAxkBAAIBHmFCexuQ1bp0N47YwArKM5YcPdokAAJUrzEbhcgQVmmEKN_iB7NbAQADAgADeAADIAQ", "file_unique_id": "AQADVK8xG4XIEFZ9", "file_size": 12657, "width": 436, "height": 222}], "caption": "压缩图片"}
    :param message:
    :return:
    """
    chat_id = message.chat.id
    cloud_piece = CloudPiece(chat_id)
    if None in (cloud_piece.database_id, cloud_piece.access_token):
        return SendMessage(chat_id, "database_id or access_token lack")

    file_id = message.photo[-1].file_id
    file_info = await bot.get_file(file_id)
    file_path = get_total_file_path(file_info.file_path)
    result, url = cloud_piece.image(file_path, message.caption)
    if result:
        return SendMessage(chat_id, f"已存储, </br>[立即编辑]({url})", parse_mode="Markdown")

    return SendMessage(chat_id, "存储失败")


@dp.message_handler(content_types=ContentType.DOCUMENT)
async def document_handler(message: Message):
    """
    不压缩的图片，算文档
    {"message_id": 284, "from": {"id": 682824243, "is_bot": false, "first_name": "F", "last_name": "joys", "username": "joyskaren", "language_code": "zh-hans"}, "chat": {"id": 682824243, "first_name": "F", "last_name": "joys", "username": "joyskaren", "type": "private"}, "date": 1631746717, "document": {"file_name": "2021-09-15.201013.png", "mime_type": "image/png", "thumb": {"file_id": "AAMCBQADGQEAAgEcYUJ6nWHPFcqdm_jJ6w-p4AksE0AAAuwDAAKFyBhWMSxfrcFlbvcBAAdtAAMgBA", "file_unique_id": "AQAD7AMAAoXIGFZy", "file_size": 9208, "width": 320, "height": 163}, "file_id": "BQACAgUAAxkBAAIBHGFCep1hzxXKnZv4yesPqeAJLBNAAALsAwAChcgYVjEsX63BZW73IAQ", "file_unique_id": "AgAD7AMAAoXIGFY", "file_size": 33225}, "caption": "test"}
    真是文件
    {"message_id": 285, "from": {"id": 682824243, "is_bot": false, "first_name": "F", "last_name": "joys", "username": "joyskaren", "language_code": "zh-hans"}, "chat": {"id": 682824243, "first_name": "F", "last_name": "joys", "username": "joyskaren", "type": "private"}, "date": 1631746783, "document": {"file_name": "新建文件.txt", "mime_type": "text/plain", "file_id": "BQACAgUAAxkBAAIBHWFCet8RB9iWOrzJ0z6SnIWI9LQhAALtAwAChcgYVsW0GgABkA8qWSAE", "file_unique_id": "AgAD7QMAAoXIGFY", "file_size": 5}, "caption": "文件"}
    :param message:
    :return:
    """
    chat_id = message.chat.id
    cloud_piece = CloudPiece(chat_id)
    if None in (cloud_piece.database_id, cloud_piece.access_token):
        return SendMessage(chat_id, "database_id or access_token lack")

    file_id = message.document.file_id
    file_info = await bot.get_file(file_id)
    file_path = get_total_file_path(file_info.file_path)
    result, url = cloud_piece.document(file_path, message.caption)
    if result:
        return SendMessage(chat_id, f"已存储, \n立即编辑：{url}")

    return SendMessage(chat_id, "存储失败")


@dp.message_handler(content_types=ContentType.VIDEO or ContentType.ANIMATION)
async def video_handler(message: Message):
    """
    {"message_id": 287, "from": {"id": 682824243, "is_bot": false, "first_name": "F", "last_name": "joys", "username": "joyskaren", "language_code": "zh-hans"}, "chat": {"id": 682824243, "first_name": "F", "last_name": "joys", "username": "joyskaren", "type": "private"}, "date": 1631746989, "video": {"duration": 14, "width": 416, "height": 640, "file_name": "1 (106).mp4", "mime_type": "video/mp4", "thumb": {"file_id": "AAMCBQADGQEAAgEfYUJ7rSeorGrhyuNAO7UoI1juc6wAAu4DAAKFyBhWmITq7CWOlKkBAAdtAAMgBA", "file_unique_id": "AQAD7gMAAoXIGFZy", "file_size": 11560, "width": 208, "height": 320}, "file_id": "BAACAgUAAxkBAAIBH2FCe60nqKxq4crjQDu1KCNY7nOsAALuAwAChcgYVpiE6uwljpSpIAQ", "file_unique_id": "AgAD7gMAAoXIGFY", "file_size": 5698704}, "caption": "视频"}
    :param message:
    :return:
    """
    print(message)
    chat_id = message.chat.id
    cloud_piece = CloudPiece(chat_id)
    if None in (cloud_piece.database_id, cloud_piece.access_token):
        return SendMessage(chat_id, "database_id or access_token lack")

    file_id = message.video.file_id
    file_info = await bot.get_file(file_id)
    file_path = get_total_file_path(file_info.file_path)
    result, url = cloud_piece.video(file_path, message.caption)
    if result:
        return SendMessage(chat_id, f"已存储, </br>[立即编辑]({url})", parse_mode="Markdown")

    return SendMessage(chat_id, "存储失败")


@dp.message_handler(content_types=ContentType.LOCATION)
async def location_handler(message: Message):
    """
    位置
    {"message_id": 289, "from": {"id": 682824243, "is_bot": false, "first_name": "F", "last_name": "joys", "username": "joyskaren", "language_code": "zh-hans"}, "chat": {"id": 682824243, "first_name": "F", "last_name": "joys", "username": "joyskaren", "type": "private"}, "date": 1631747382, "location": {"latitude": 36.129698, "longitude": 113.141452}}
    :param message:
    :return:
    """
    chat_id = message.chat.id
    return SendMessage(chat_id, unsupported)

    cloud_piece = CloudPiece(chat_id)
    if None in (cloud_piece.database_id, cloud_piece.access_token):
        return SendMessage(chat_id, "database_id or access_token lack")

    latitude = Degree.dd_to_dms(message.location.latitude)
    longitude = Degree.dd_to_dms(message.location.longitude)
    url = f"https://www.google.com/maps/place/{latitude}N+{longitude}E/"
    result, url = cloud_piece.maps(url, message.caption)
    if result:
        return SendMessage(chat_id, f"已存储, </br>[立即编辑]({url})", parse_mode="Markdown")

    return SendMessage(chat_id, "存储失败")


@dp.message_handler(content_types=ContentType.TEXT)
async def text_handler(message: Message):
    chat_id = message.chat.id
    cloud_piece = CloudPiece(chat_id)
    if None in (cloud_piece.database_id, cloud_piece.access_token):
        return SendMessage(chat_id, "database_id or access_token lack")

    result, url = cloud_piece.text(message.text)
    if result:
        return SendMessage(chat_id, f"已存储, </br>[立即编辑]({url})", parse_mode="Markdown")

    return SendMessage(chat_id, "存储失败")


@dp.message_handler(content_types=ContentType.ANY)
async def other_handler(message: Message):
    """
    链接
    {"message_id": 288, "from": {"id": 682824243, "is_bot": false, "first_name": "F", "last_name": "joys", "username": "joyskaren", "language_code": "zh-hans"}, "chat": {"id": 682824243, "first_name": "F", "last_name": "joys", "username": "joyskaren", "type": "private"}, "date": 1631747159, "text": "https://map.baidu.com/poi/%E6%96%B0%E4%B9%A1%E4%B8%9C%E7%AB%99/@12683140.43,4181023.18,11.87z?uid=024242f8281b5de0902ca33d&info_merge=1&isBizPoi=false&ugc_type=3&ugc_ver=1&device_ratio=2&compat=1&seckey=646f10cb77181888e7eef50bc07d45274c5fe0c85c4ae6a2b8a66de6bcc21f3371287d727a5322140481ce64c70ad1b657a6e09c31496fd4129b0c48c0873df5e65fdd5dad42907939e1c29f1e11ff580221bd14f507d16fad988972b921284165fbbccef2db3357a30d08caba9a19fdf2c10a5c840df1137ccbed3c5e40ca918cda30ea2f66f38a7e17e010fcbd4e928a8511b6e804161898d38f712965abbc0f6b83ff2f5fbc1c9570e45839f1841ba7270a4c39c64b6770fbd429074f3b1c6ff61418188ec88e01d6caae3961a0f895782a5894e76547d1e2e280a9ccbf9572ceb18c2badf993e2f815ce10e09c04&pcevaname=pc4.1&newfrom=zhuzhan_webmap&querytype=detailConInfo&da_src=shareurl", "entities": [{"type": "url", "offset": 0, "length": 762}]}

    音频
    {"message_id": 292, "from": {"id": 682824243, "is_bot": false, "first_name": "F", "last_name": "joys", "username": "joyskaren", "language_code": "zh-hans"}, "chat": {"id": 682824243, "first_name": "F", "last_name": "joys", "username": "joyskaren", "type": "private"}, "date": 1631752942, "voice": {"duration": 2, "mime_type": "audio/ogg", "file_id": "AwACAgUAAxkBAAIBJGFCku7P2ja9BS39AAHLA_28X7ya8AAC-AMAAoXIGFZWhpP-i8pVYyAE", "file_unique_id": "AgAD-AMAAoXIGFY", "file_size": 8003}}
    :param message:
    :return:
    """
    return SendMessage(message.chat.id, unsupported)


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


async def root(request):
    return web.json_response({"message": "Success"})


if __name__ == '__main__':
    # web_app
    web_app = web.Application()
    web_app.add_routes([web.get('/', root)])
    web_app.add_routes([web.get('/auth', auth)])

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
