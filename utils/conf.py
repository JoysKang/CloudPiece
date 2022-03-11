import json


def load_json(file_path="../conf.json"):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except:
        return {}
