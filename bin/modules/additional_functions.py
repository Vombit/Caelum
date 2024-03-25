import os
import sys
import threading
import time
from bin.modules.file_manager import FileManager
from bin.modules.db_manager import DBManager
from numpy import array_split

fm = FileManager()
db = DBManager()
lock = threading.Lock()


def bot_upload(file_hash: str, chunks: list, bot: object):
    for chunk in chunks:
        chunk_path = f"{fm.split_chunks}/{chunk}"

        chunk_file_id = bot.send_document(chunk_path)
        chunk_file_hash = fm.get_file_hash(chunk_path)

        try:
            lock.acquire(True)
            db.add_chunk(file_hash, chunk_file_hash, chunk.split("_")[1], chunk_file_id)
        finally:
            lock.release()

        while True:
            try:
                os.remove(chunk_path)
                break
            except Exception:
                time.sleep(0.3)


def bot_download(chunks: list, bot: object):
    for chunk in chunks:
        path_chunk = f"{fm.loaded_chunks}/{chunk[1]}_{chunk[3]}"

        loaded_file = bot.download_document(chunk[4])

        # Save the chunk to a file and remove it when done
        with open(path_chunk, "wb") as new_file:
            new_file.write(loaded_file)


def split_chunks(file_list, num_threads):
    chunk_lists = array_split(file_list, num_threads)

    return chunk_lists


def resource_path(relative_path: str) -> str:
    """
    Get the absolute path to the resource,
    works for dev and for PyInstaller
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def check_healh_bot(bot: object) -> bool:
    test_file = resource_path("bin/static/test.txt")
    if bot.send_document(test_file):
        return True
    return False
