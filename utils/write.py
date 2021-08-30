import json

import requests

from utils.conf import load_json

conf = load_json("./conf.json")
authorization = conf.get('authorization')
database_id = conf.get('database_id')


async def async_write(text):
    write(text)


def write(text):
    headers = {
        'Authorization': f'Bearer {authorization}',
        'Content-Type': 'application/json',
        'Notion-Version': '2021-08-16',
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


