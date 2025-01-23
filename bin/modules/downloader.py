import threading
import os
from PyQt5.QtCore import QThread
from bin.modules.telegram_bot import TelegramBot
from bin.modules.file_manager import FileManager
from bin.modules.db_manager import DBManager
from bin.modules.utils import (
    split_chunks
)

db = DBManager()
fm = FileManager()
lock = threading.Lock()


class Downloader(QThread):
    def __init__(self, filename):
        QThread.__init__(self)
        self.file_name = filename
        self.t_bots = []
        self.view = None

        self.chunks_total = 0
        self.downloaded_chunks_counter = 0

    def __del__(self):
        self.wait()

    def run(self):
        self.change_text_popup('start download')
        self.view.page().runJavaScript("toggleNotification()")
        
        for obj in db.get_bots():
            bot = TelegramBot(obj[2], obj[3])
            self.t_bots.append(bot)

        file_hash = db.get_file_by_name(self.file_name)[0][2]
        chunks = db.get_chunks(file_hash)
        split_chinks = split_chunks(chunks, len(self.t_bots))
        self.chunks_total = len(chunks)

        self.change_text_popup('download')
        threads = []
        for i, chunks in enumerate(split_chinks):
            my_thread = threading.Thread(
                target=self.bot_download, args=(chunks, self.t_bots[i], self.t_bots)
            )
            threads.append(my_thread)
            my_thread.start()

        for thread in threads:
            thread.join()

        all_chunks_present = all(os.path.isfile(f"{fm.loaded_chunks}/{chunk[1]}_{chunk[3]}") for chunk in chunks)
        if all_chunks_present:
            self.change_text_popup('merging chunks')
            fm.merge_chunks(self.file_name, file_hash)
        else:
            print("Error: Not all chunks are downloaded or valid.")
            self.change_text_popup('error during download')

        self.downloaded_chunks_counter = 0
        self.change_progress(0)
        self.view.page().runJavaScript("toggleNotification()")

    def change_progress(self, progress: int):
        self.view.page().runJavaScript(f"changeProgress({progress})")
        
    def change_text_popup(self, text: str):
        self.view.page().runJavaScript(f"setText('{text}')")

    def bot_download(self, chunks: list, bot: object, bots):
        for chunk in chunks:
            path_chunk = f"{fm.loaded_chunks}/{chunk[1]}_{chunk[3]}"

            if os.path.isfile(path_chunk):
                gen, hasher = fm.get_file_hash(path_chunk)
                list(gen)
                file_hash = hasher.hexdigest()
                if chunk[2] == file_hash:
                    self.downloaded_chunks_counter += 1
                    continue


            loaded_file = None
            bot_index = bots.index(bot)
            attempts = 0
            
            while not loaded_file and attempts < len(bots):
                try:
                    loaded_file = bots[bot_index].download_document(chunk[4])
                except Exception as e:
                    print(f"Error downloading chunk {chunk[3]} with bot {bot_index}: {e}")
                
                if not loaded_file:
                    bot_index = (bot_index + 1) % len(bots)
                    attempts += 1

            if not loaded_file:
                print(f"Failed to download chunk {chunk[3]} after trying all bots.")
                continue

            try:
                lock.acquire(True)
                with open(path_chunk, "wb") as new_file:
                    new_file.write(loaded_file)

                self.downloaded_chunks_counter += 1
                progress = int((self.downloaded_chunks_counter / self.chunks_total) * 100)
                self.change_progress(progress)
            except Exception as e:
                print(f"Error saving chunk {chunk[3]}: {e}")
            finally:
                lock.release()
            # print(f"{chunk[3]}")
