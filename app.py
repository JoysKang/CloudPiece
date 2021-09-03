from fastapi import FastAPI
from starlette.requests import Request
from aiogram import Bot
from aiogram.dispatcher import Dispatcher

from utils.write import write, update_or_create, get_data
from utils.conf import load_json


app = FastAPI()

conf = load_json("./conf.json")
API_TOKEN = conf.get("telegram_token")
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@app.post("/echo")
async def echo(request: Request):
    """
    :param request: {
        "update_id": 103xxx,
        "message": {
            "message_id": 56,
            "from": {
                "id": 682xxx,
                "is_bot": False,
                "first_name": "F",
                "last_name": "joys",
                "username": "joyskaren",
                "language_code": "zh-hans"
            },
            "chat": {
                "id": 682xxx,
                "first_name": "F",
                "last_name": "joys",
                "username": "joyskaren",
                "type": "private"
            },
            "date": 1629899314,
            "text": "test2",
            "document": {
                "file_name": "2021-08-26.201916.png",
                "mime_type": "image/png",
                "thumb": {
                    "file_id": "AAMCBQADGQEAA1BhJ4eDF8k4_M90jfPwGRkEkrHGyAACbQMAAnF2QVX5iT3KiDyKNgEAB20AAyAE",
                    "file_unique_id": "AQADbQMAAnF2QVVy",
                    "file_size": 6346,
                    "width": 320,
                    "height": 97
                },
                "file_id": "BQACAgUAAxkBAANQYSeHgxfJOPzPdI3z8BkZBJKxxsgAAm0DAAJxdkFV-Yk9yog8ijYgBA",
                "file_unique_id": "AgADbQMAAnF2QVU",
                "file_size": 36459
            },
            "caption": "图片"
        }
    }
    :return:
    """
    body = await request.json()
    message = body["message"]
    database_id, code = get_data(message["chat"])

    if write(database_id, code, message.get("text")):
        await bot.send_message(message.get("chat").get("id"), "已存储")
        return {"message": "Success"}

    return {"message": "Failure"}


@app.get("/auth")
async def root(request: Request):
    """授权回调"""
    print(dict(request.query_params.multi_items()))
    return {"message": "Success"}


@app.get("/")
def root():
    return {"message": "Success"}
