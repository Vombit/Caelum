import os
import sys
import threading
from bin.modules.file_manager import FileManager
from bin.modules.db_manager import DBManager
from numpy import array_split

fm = FileManager()
db = DBManager()
lock = threading.Lock()


# trash all
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


def bot_download(chunks: list, bot: object, bots):
    for chunk in chunks:
        path_chunk = f"{fm.loaded_chunks}/{chunk[1]}_{chunk[3]}"

        if os.path.isfile(path_chunk):
            hash = fm.get_file_hash(path_chunk)
            if chunk[1] == hash:
                continue

        loaded_file = bot.download_document(chunk[4])
        if not loaded_file:
            for bot in bots:
                loaded_file = bot.download_document(chunk[4])
                if loaded_file:
                    break

        # print(loaded_file)
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


class Manager:
    def __init__(self):
        pass

    def download(args):
        pass

    def continue_download(args):
        pass

    def upload(file_hash: str, chunks: list, bots: object):
        for chunk in chunks:
            chunk_path = f"{fm.split_chunks}/{chunk}"

            chunk_file_id = bots.send_document(chunk_path)
            chunk_file_hash = fm.get_file_hash(chunk_path)

            try:
                lock.acquire(True)
                db.add_chunk(file_hash, chunk_file_hash, chunk.split("_")[1], chunk_file_id)
            finally:
                lock.release()

        for chunk in chunks:
            chunk_path = f"{fm.split_chunks}/{chunk}"
            try:
                os.remove(chunk_path)
            except Exception:
                print(Exception)
        
    def continue_upload(args):
        pass