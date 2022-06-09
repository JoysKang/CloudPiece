import os


def get_total_file_path(file_path=""):
    """获取 file path"""
    return f"https://api.telegram.org/file/bot{os.environ.get('telegram_token')}/{file_path}"
