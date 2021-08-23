import json

import requests

from utils.conf import load_json

conf = load_json("./conf.json")


async def async_write():
    write()


def write():
    headers = {
        'Authorization': f'Bearer {conf.get("authorization")}',
        'Content-Type': 'application/json',
        'Notion-Version': '2021-08-16',
    }

    data = {
        "parent": {"database_id": conf.get("database_id")},
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
                                "content": "test"
                            }
                        }
                    ]
                }
            }
        ]
    }

    response = requests.post('https://api.notion.com/v1/pages', headers=headers, data=json.dumps(data))
    print(response.status_code)


