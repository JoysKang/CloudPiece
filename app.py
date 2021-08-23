import asyncio

from fastapi import FastAPI
from utils.write import write, async_write

app = FastAPI()

# 异步函数路径以 /async 开头


@app.get("/write")
def write():
    """同步写入"""
    write()
    return {"message": "Write success"}


@app.get("/async/write")
def write():
    """异步写入(腾讯云函数暂不支持异步调用)"""
    asyncio.create_task(async_write())
    return {"message": "Write success"}


@app.get("/async")
async def async_root():
    return {"message": "Hello World"}


@app.get("/")
def root():
    return {"message": "Hello World"}
