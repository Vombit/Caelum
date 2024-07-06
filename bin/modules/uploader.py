import threading
import os
from PyQt5.QtCore import QThread, pyqtSignal
from bin.modules.telegram_bot import TelegramBot
from bin.modules.file_manager import FileManager
from bin.modules.db_manager import DBManager
from bin.modules.utils import (
    split_chunks
)

db = DBManager()
fm = FileManager()
lock = threading.Lock()



def bot_upload(file_hash: str, chunks: list, bot: object):
    for chunk in chunks:
        chunk_path = f"{fm.split_chunks}/{chunk}"

        chunk_file_id = bot.send_document(chunk_path)
        chunk_file_hash = fm.get_file_hash(chunk_path)

        try:
            lock.acquire(True)
            db.add_chunk(file_hash, chunk_file_hash, chunk.split("_")[1], chunk_file_id)
        except Exception:
            print(Exception)
        finally:
            lock.release()
    print(f'chunks uploaded for bot:{bot.bot_token}')
    for chunk in chunks:
        chunk_path = f"{fm.split_chunks}/{chunk}"
        try:
            os.remove(chunk_path)
        except Exception:
            print(Exception)
    print(f'chunks deleted for bot:{bot.bot_token}')


class Uploader(QThread):
    counter = pyqtSignal(int)

    def __init__(self, file_path):
        QThread.__init__(self)
        self.file_path = file_path
        self.t_bots = []
        self.view = None

    def __del__(self):
        self.wait()

    def run(self):
        self.view.page().runJavaScript(f"setText('start')")
        self.view.page().runJavaScript(f"toggleNotification()")

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

        self.view.page().runJavaScript(f"toggleNotification()")
