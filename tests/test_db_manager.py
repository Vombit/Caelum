import sys
import string
import os
import random
import pytest
sys.path.append(os.getcwd())
from bin.modules.db_manager import DBManager


def randomword(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


@pytest.fixture
def db_manager():
    db = DBManager(db_path='tests/test_data/test.sqlite3')
    yield db
    db.conn.close()


def test_init(db_manager):
    assert db_manager.conn is not None
    assert db_manager.cursor is not None


def test_add_file(db_manager):
    file_name = randomword(12)
    file_hash = randomword(18)
    db_manager.add_file(file_name, file_hash)
    result = db_manager.get_file_by_name(file_name)
    assert result[0][1] == file_name
    assert result[0][2] == file_hash
