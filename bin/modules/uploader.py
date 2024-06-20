import threading
import os
from PyQt5.QtCore import QThread, pyqtSignal
from bin.modules.telegram_bot import TelegramBot
from bin.modules.file_manager import FileManager
from bin.modules.db_manager import DBManager
from bin.modules.additional_functions import (
    split_chunks,
    bot_upload
)

db = DBManager()
fm = FileManager()

class Uploader(QThread):
    counter = pyqtSignal(int)

    def __init__(self, file_path):
        QThread.__init__(self)
        self.file_path = file_path
        self.t_bots = []

    def __del__(self):
        self.wait()

    def run(self):
        for obj in db.get_bots():
            bot = TelegramBot(obj[2], obj[3])
            self.t_bots.append(bot)

        file_hash = fm.get_file_hash(self.file_path)
        filename = os.path.basename(self.file_path)
        fm.process_file(self.file_path)
        db.add_file(filename, file_hash)

        split_chinks = split_chunks(fm.get_split_chunks(), len(self.t_bots))

        threads = []
        for i, chunks in enumerate(split_chinks):
            my_thread = threading.Thread(
                target=bot_upload, args=(file_hash, chunks, self.t_bots[i])
            )
            threads.append(my_thread)
            my_thread.start()
            self.counter.emit(i)

        for thread in threads:
            thread.join()
