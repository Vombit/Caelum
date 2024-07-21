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


class Uploader(QThread):
    def __init__(self, file_path):
        QThread.__init__(self)
        self.file_path = file_path
        self.t_bots = []
        self.view = None

        self.uploaded_chunks_counter = 0
        self.uploaded_chunks_counter_lock = threading.Lock()

    def __del__(self):
        self.wait()

    def run(self):
        filename = os.path.basename(self.file_path)
        file_size = fm.get_file_size(self.file_path)
        total_file_size = round((file_size / 1024 / 1024) + 0.5)

        self.view.page().runJavaScript("setText('start')")
        self.view.page().runJavaScript("toggleNotification()")
        for obj in db.get_bots():
            bot = TelegramBot(obj[2], obj[3])
            self.t_bots.append(bot)

        # getting file hash and change progress
        self.view.page().runJavaScript("setText('getting the hash')")
        gen, hasher = fm.get_file_hash(self.file_path)
        for current in gen:
            progress = int(((current / (1024 * 1024)) / total_file_size) * 100)
            self.view.page().runJavaScript(f"changeProgress({progress})")
        file_hash = hasher.hexdigest()
        db.add_file(filename, file_hash)

        # splitting a file into chunks
        self.view.page().runJavaScript("setText('splitting into chunks')")
        self.view.page().runJavaScript("changeProgress(0)")
        chunks_file = fm.process_file(self.file_path)
        for chunk in chunks_file:
            progress = int((int(chunk) / (total_file_size / 20)) * 100)
            self.view.page().runJavaScript(f"changeProgress({progress})")

        self.view.page().runJavaScript("changeProgress(0)")
        self.view.page().runJavaScript("setText('uploading')")

        # splitting chunks by bots
        split_chinks = split_chunks(fm.get_split_chunks(), len(self.t_bots))

        threads = []
        for i, chunks in enumerate(split_chinks):
            my_thread = threading.Thread(
                target=self.bot_upload, args=(file_hash, chunks, self.t_bots[i])
            )
            threads.append(my_thread)
            my_thread.start()

        for thread in threads:
            thread.join()
            
        self.view.page().runJavaScript("toggleNotification()")


    def bot_upload(self, file_hash: str, chunks: list, bot: object):
        for chunk in chunks:
            chunk_path = f"{fm.split_chunks}/{chunk}"

            chunk_file_id = bot.send_document(chunk_path)
            gen, hasher = fm.get_file_hash(chunk_path)
            list(gen)
            chunk_file_hash = hasher.hexdigest()

            try:
                lock.acquire(True)
                db.add_chunk(file_hash, chunk_file_hash, chunk.split("_")[1], chunk_file_id)
            except Exception:
                print(Exception)
            finally:
                lock.release()
        print(f'chunks uploaded, bot={bot.bot_token}')
        for chunk in chunks:
            chunk_path = f"{fm.split_chunks}/{chunk}"
            try:
                os.remove(chunk_path)
            except Exception:
                print(Exception)