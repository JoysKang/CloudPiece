import json

import requests

from utils.conf import load_json

conf = load_json("./conf.json")
relation_database_id = conf.get('relation_database_id')
relation_code = conf.get('relation_code')
notion_version = conf.get('notion_version')


def delete_relation(chat_id):
    """删除记录"""
    headers = {
        'Authorization': f'Bearer {relation_code}',
        'Notion-Version': f'{notion_version}',
        'Content-Type': 'application/json',
    }
    data = {
        "parent": {"database_id": relation_database_id},
        "properties": {},
        "archived": True
    }

    page_id = get_page_id(chat_id)
    response = requests.patch(f'https://api.notion.com/v1/pages/{page_id}',
                              headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        return True

    print(response.content)
    return False


def write(database_id, code, text):
    headers = {
        'Authorization': f'Bearer {code}',
        'Notion-Version': '2021-05-13',
        'Content-Type': 'application/json',
    }
    data = {
        "parent": {"database_id": database_id},
        "properties": {
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": ""
                        }
                    }
                ]
            }
        },
        "children": [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "text": [
                        {
                            "type": "text",
                            "text": {
                                "content": text
                            }
                        }
                    ]
                }
            }
        ]
    }

    response = requests.post('https://api.notion.com/v1/pages', headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        return True

    return False


def update(chat_id="", access_token="", database_id="", code=""):
    headers = {
        'Authorization': f'Bearer {relation_code}',
        'Notion-Version': f'{notion_version}',
        'Content-Type': 'application/json',
    }

    page_id = get_page_id(chat_id)

    data = {
        "parent": {"database_id": relation_database_id},
        "properties": {}
    }
    if not (access_token or database_id or code):
        return False

    if access_token:
        data['properties']["AccessToken"] = {
                "rich_text": [
                    {
                        "text": {
                            "content": access_token
                        }
                    }
                ]
            }

    if database_id:
        data['properties']["DatabaseId"] = {
                "rich_text": [
                    {
                        "text": {
                            "content": database_id
                        }
                    }
                ]
            }

    if code:
        data['properties']["Code"] = {
            "rich_text": [
                {
                    "text": {
                        "content": code
                    }
                }
            ]
        }

    response = requests.patch(f'https://api.notion.com/v1/pages/{page_id}',
                              headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        return True

    print(response.content)
    return False


def create(name, chat_id=""):
    """
        更新或创建数据库记录
    """
    headers = {
        'Authorization': f'Bearer {relation_code}',
        'Notion-Version': f'{notion_version}',
        'Content-Type': 'application/json',
    }

    # 先判断 chat_id 是否已存在，不存在再写入，已存在的直接跳过
    _, _, page_id = get_data(chat_id)
    if page_id:
        return False

    data = {
        "parent": {"database_id": relation_database_id},
        "properties": {
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": name
                        }
                    }
                ]
            },
            "ChatId": {
                "rich_text": [
                    {
                        "text": {
                            "content": chat_id
                        }
                    }
                ]
            }
        },
    }

    response = requests.post('https://api.notion.com/v1/pages', headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        return True

    print(response.content)
    return False


def get_page_id(chat_id=None):
    """根据 chat_id 获取 database_id、code"""
    _data = '{ "filter": { "or": [ { "property": "ChatId", "rich_text": {"equals": "' + str(chat_id) + '"}} ] } }'
    _data = _data.encode()

    headers = {
        'Authorization': f'Bearer {relation_code}',
        'Notion-Version': f'{notion_version}',
        'Content-Type': 'application/json',
    }
    response = requests.post(
        f'https://api.notion.com/v1/databases/{relation_database_id}/query',
        headers=headers, data=_data)
    if response.status_code != 200:
        return "", ""

    content = json.loads(response.content)
    result = content["results"][0]
    return result["id"]


def get_data(chat_id=None):
    """根据 chat_id 获取 database_id、code"""
    _data = '{ "filter": { "or": [ { "property": "ChatId", "rich_text": {"equals": "' + str(chat_id) + '"}} ] } }'
    _data = _data.encode()

    headers = {
        'Authorization': f'Bearer {relation_code}',
        'Notion-Version': f'{notion_version}',
        'Content-Type': 'application/json',
    }
    response = requests.post(
        f'https://api.notion.com/v1/databases/{relation_database_id}/query',
        headers=headers, data=_data)
    # print(response.content)
    if response.status_code != 200:
        return "", ""

    content = json.loads(response.content)
    if len(content["results"]) <= 0:
        return None, None, None

    result = content["results"][0]
    database_id = result["properties"]["DatabaseId"]["rich_text"][0]["plain_text"]
    access_token = result["properties"]["AccessToken"]["rich_text"][0]["plain_text"]
    page_id = result["id"]  # 存在 page_id 则说明当前 chat_id 已有记录，不需要重复写
    return database_id, access_token, page_id


def get_database_id(access_token=""):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Notion-Version': f'{notion_version}',
        'Content-Type': 'application/json',
    }
    response = requests.post(
        f'https://api.notion.com/v1/search',
        headers=headers)
    if response.status_code != 200:
        return "", ""

    content = json.loads(response.content)
    result = content["results"][0]
    return result["id"].replace("-", "")


if __name__ == "__main__":
    chat_id = "682824241"
    delete_relation(chat_id)
    # database_id, access_token, page_id = get_data(chat_id)
    # print(database_id, access_token, page_id)
    # write(database_id, access_token, "test")
    # print(get_page_id(chat_id))
    # create("Joys", "1")  # 更新
    # update("682824241", "1000")  # 更新

    # token = "secret_VyhnFdYcY8wz1coSvTKICUZY7EFauucB0ySsZXu7EyO"
    # print(get_database_id(token))
