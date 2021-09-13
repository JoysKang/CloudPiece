import json

import requests

from utils.conf import load_json

conf = load_json("./conf.json")
relation_database_id = conf.get('relation_database_id')
relation_code = conf.get('relation_code')


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


def update_or_create(name, database_id="", chat_id="", code="", create=False):
    """
        更新或创建数据库记录
    """
    headers = {
        'Authorization': f'Bearer {conf.get("relation_code")}',
        'Notion-Version': '2021-05-13',
        'Content-Type': 'application/json',
    }
    data = {
        "parent": {"database_id": conf.get("relation_database_id")},
        "properties": {
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": name
                        }
                    }
                ]
            }
        },
    }
    if database_id:
        data["properties"]["DatabaseId"] = {
            "rich_text": [
                    {
                        "text": {
                            "content": database_id
                        }
                    }
                ]
            }

    if chat_id:
        if create:
            data["properties"]["ChatId"] = {
                "rich_text": [
                        {
                            "text": {
                                "content": chat_id
                            }
                        }
                    ]
                }
        else:
            print("===")
            data["ChatId"] = {
                "rich_text": [
                        {
                            "text": {
                                "content": chat_id
                            }
                        }
                    ]
                }

    if code:
        data["properties"]["Code"] = {
            "rich_text": [
                    {
                        "text": {
                            "content": code
                        }
                    }
                ]
            }

    response = requests.post('https://api.notion.com/v1/pages', headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        return True

    print(response.content)
    return False


def get_data(chat_id=None):
    """根据 chat_id 获取 database_id、code"""
    _data = '{ "filter": { "or": [ { "property": "ChatId", "rich_text": {"equals": "' + str(chat_id) + '"}} ] } }'
    _data = _data.encode()

    headers = {
        'Authorization': f'Bearer {relation_code}',
        'Notion-Version': '2021-05-13',
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


if __name__ == "__main__":
    # write(conf.get('database_id'), conf.get('code'), "test")

    # chat_id = 682824241
    # print(get_data(chat_id))

    update_or_create("Joys", "1", "682824241")  # 更新
