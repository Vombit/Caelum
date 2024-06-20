import threading
from PyQt5.QtCore import QThread
from bin.modules.telegram_bot import TelegramBot
from bin.modules.file_manager import FileManager
from bin.modules.db_manager import DBManager
from bin.modules.additional_functions import (
    split_chunks,
    bot_download
)

db = DBManager()
fm = FileManager()


class Downloader(QThread):
    def __init__(self, filename):
        QThread.__init__(self)
        self.file_name = filename
        self.t_bots = []

    def __del__(self):
        self.wait()

    def run(self):
        for obj in db.get_bots():
            bot = TelegramBot(obj[2], obj[3])
            self.t_bots.append(bot)

        file_hash = db.get_file_by_name(self.file_name)[0][2]
        chunks = db.get_chunks(file_hash)
        split_chinks = split_chunks(chunks, len(self.t_bots))

        threads = []
        for i, chunks in enumerate(split_chinks):
            my_thread = threading.Thread(
                target=bot_download, args=(chunks, self.t_bots[i], self.t_bots)
            )
            threads.append(my_thread)
            my_thread.start()

        for thread in threads:
            thread.join()

        fm.merge_chunks(self.file_name, file_hash)
