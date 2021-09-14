import json

import requests

from utils.conf import load_json

conf = load_json("./conf.json")
relation_database_id = conf.get('relation_database_id')
relation_code = conf.get('relation_code')
notion_version = conf.get('notion_version')


async def async_write(database_id, code, text):
    write(database_id, code, text)


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
    result = content["results"][0]
    database_id = result["properties"]["DatabaseId"]["rich_text"][0]["plain_text"]
    code = result["properties"]["Code"]["rich_text"][0]["plain_text"]
    return database_id, code


def get_database_id(token=""):
    headers = {
        'Authorization': f'Bearer {token}',
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
    print(result)
    return result["parent"]["database_id"].replace("-", "")


if __name__ == "__main__":
    # database_id = "afa9eb11160147e1b5d6975fb725d0b2"
    # code = "secret_6S5keodDtrnRqXjI5dgbQUWzKmSeG6yL9XWvVdAjXW7"
    # write(database_id, code, "test")

    # chat_id = "682824241"
    # print(get_data(chat_id))
    # print(get_page_id(chat_id))
    # create("Joys", "1")  # 更新
    # update("682824241", "1000")  # 更新

    token = "secret_6S5keodDtrnRqXjI5dgbQUWzKmSeG6yL9XWvVdAjXW7"
    workspace_id = "b21e2813-848c-47da-977e-0ac05baa96a6"
    print(get_database_id(token))
