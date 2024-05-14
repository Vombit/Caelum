# py.test -s
import sys
import os
import pytest
import json
sys.path.append(os.getcwd())
from bin.modules.telegram_bot import TelegramBot


def get_config():
    with open('tests/test_data/config.json') as f:
        config = json.load(f)
    return config


@pytest.fixture(scope="session")
def TB():
    config = get_config()
    return TelegramBot(config["bot_token"], config["chat_id"])


def test_bot_token_update():
    config = get_config()
    bot = TelegramBot(config["bot_token"], config["chat_id"])
    new_token = "NEW_BOT_TOKEN"
    bot.update_bot_token(new_token)
    assert bot.bot_token == new_token


def test_chat_id_update():
    config = get_config()
    bot = TelegramBot(config["bot_token"], config["chat_id"])
    new_id = "NEW_CHAT_ID"
    bot.update_chat_id(new_id)
    assert bot.chat_id == new_id


def test_send_document_success(TB):
    file_path = "tests/test_data/test_file.txt"
    bot = TB

    file_id = bot.send_document(file_path)
    assert file_id != ""


def test_download_document_success(TB):
    file_path = "tests/test_data/test_file.txt"
    bot = TB

    file_id = bot.send_document(file_path)
    assert file_id != ""

    downloaded_file = bot.download_document(file_id)
    assert downloaded_file != b""
