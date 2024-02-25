import os
import json
import requests

class TelegramBot:
    def __init__(self, bot_token=None, chat_id=None) -> None:
        '''
        Initialization of the TelegramBot class with optional bot token and chat ID
        '''
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f'https://api.telegram.org/bot{self.bot_token}/'

    
    def update_bot_token(self, token: str) -> None:
        '''
        Updates the bot token for the TelegramBot object.

        :param token: The new bot token to be used.
        :return: None
        '''
        self.bot_token = token
        
    def update_chat_id(self, id: str) -> None:
        '''
        Updates the chat ID for the TelegramBot object.

        :param id: The new chat ID to be used.
        :return: None
        '''
        self.chat_id = id

    def send_document(self, file_path: str) -> str:
        '''
        Sends a document (file) to the chat using Telegram bot API.

        :param file_path: The local path of the file to be sent.
        :return: File ID of the uploaded document in Telegram API.
        '''
        url = self.base_url + 'sendDocument'

        files = {
            'document': (os.path.basename(file_path), open(file_path, 'rb')),
        }
        data = {
            'chat_id': self.chat_id,
        }

        response = requests.post(url, files=files, data=data)

        if response.status_code == 200:
            result = response.json()
            if result['ok']:
                file_id = result['result']['document']['file_id']
                return file_id
            else:
                print('Error:', result['description'])
        else:
            print('Error:', response.status_code)

    def download_document(self, file_id: str) -> str:
        '''
        Downloads a document (file) from Telegram API using bot token and file ID.

        :param file_id: The file ID of the document to be downloaded.
        :return: Content of the downloaded document as bytes.
        '''
        url = self.base_url + f"getFile?file_id={file_id}"

        response_file_path = requests.get(url)
        file_url = json.loads(response_file_path.content.decode())['result']['file_path']

        url_file = f"https://api.telegram.org/file/bot{self.bot_token}/{file_url}"
        file = requests.get(url_file)

        return file.content
