from utils.conf import load_json

conf = load_json("./conf.json")


def get_total_file_path(file_path=""):
    """获取 file path"""
    return f"https://api.telegram.org/file/bot{conf.get('telegram_token')}/{file_path}"
