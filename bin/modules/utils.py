import sys
import os
from numpy import array_split


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

def split_chunks(file_list: list, num_threads: int) -> list:
    """
    Get the absolute path to the resource,
    works for dev and for PyInstaller
    """
    chunk_lists = array_split(file_list, num_threads)

    return chunk_lists