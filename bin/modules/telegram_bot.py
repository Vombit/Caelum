import os
import json
import requests
import time

class TelegramBot:
    """
    class for telegram bot
    """

    def __init__(self, bot_token: str = None, chat_id: str = None) -> None:
        """
        Initialization of the TelegramBot class
        with optional bot token and chat ID

        Args:
            bot_token (str): Api bot token.
            chat_id (str): Chat id.
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}/"

    def update_bot_token(self, token: str) -> None:
        """
        Updates the bot token for the TelegramBot object.

        Args:
            token (str): The new bot token to be used.
        """
        self.bot_token = token

    def update_chat_id(self, id: str) -> None:
        """
        Updates the chat ID for the TelegramBot object.

        Args:
            id (str): The new chat ID to be used.
        """
        self.chat_id = id

    def send_document(self, file_path: str) -> str:
        """
        Sends a document (file) to the chat using Telegram bot API.

        Args:
            file_path (str): The local path of the file to be sent.

        Return: File ID of the uploaded document in Telegram API.
        """
        url = self.base_url + "sendDocument"

        files = {
            "document": (os.path.basename(file_path), open(file_path, "rb")),
        }
        data = {
            "chat_id": self.chat_id,
        }
        # data = {"chat_id": str(self.chat_id), "document": (open(file_path, "rb"))}
        response = requests.post(url, files=files, data=data, timeout=120)
        
        # shit code
        for _ in range(100):
            try:
                if response.status_code == 200:
                    result = response.json()
                    if result["ok"]:
                        file_id = result["result"]["document"]["file_id"]

                        return file_id
            except Exception as e:
                print(response.status_code)
                print(response.json())
                # 
                time.sleep(30)

            # response = requests.post(url, files=files, data=data, timeout=120, verify=False)
            response = requests.post(url, files=files, data=data, timeout=120)
        else:
            return ""

    def download_document(self, file_id: str) -> str:
        """
        Downloads a document (file) from Telegram API
        using bot token and file ID.

        Args:
            file_id (str): The file ID of the document to be downloaded.

        Return: Content of the downloaded document as bytes.
        """
        url = self.base_url + f"getFile?file_id={file_id}"

        response = requests.get(url)

        for _ in range(10):
            if response.status_code == 200:
                file_url = json.loads(response.content.decode())["result"]["file_path"]

                url_file = (
                    f"https://api.telegram.org/file/bot{self.bot_token}/{file_url}"
                )
                file = requests.get(url_file)
                return file.content
            response = requests.get(url)
        else:
            return ""
