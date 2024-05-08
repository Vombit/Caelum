# py.test -s
import os
import sys
import pytest
sys.path.append(os.getcwd())
from bin.modules.file_manager import FileManager


@pytest.fixture(scope="session")
def FM():
    return FileManager(base_path="TEMP_test", base_output="TEMP_test/output")


def test_create_path(FM):
    test_path = FM.create_path(f"{FM.base_path}/test_path")
    assert os.path.exists(test_path)


def test_get_file_hash(FM):
    file_path = "tests/test_data/test_50mb"
    file_hash = FM.get_file_hash(file_path)

    assert len(file_hash) == 32  # MD5 hash length
    assert file_hash == '2e66bb4f605fc0ab8b33baf395c46760'


def test_split_file(FM):
    file_path = "tests/test_data/test_50mb"

    FM.process_file(file_path)
    chunks = FM.get_split_chunks()
    assert len(chunks) == 3


def test_merge_chunks(FM):
    file_path = "tests/test_data/test_50mb"
    main_file_hash = '2e66bb4f605fc0ab8b33baf395c46760'
    main_file_name = 'test_50mb'

    check_file_path = f"{FM.output_path}/{main_file_name}"

    FM.process_file(file_path)
    chunks = FM.get_split_chunks()
    assert len(chunks) == 3

    FM.merge_chunks(main_file_name, main_file_hash, filepath='TEMP_test/split')
    assert os.path.isfile(check_file_path)

    file_hash = FM.get_file_hash(check_file_path)
    assert len(file_hash) == 32  # MD5 hash length
    assert file_hash == '2e66bb4f605fc0ab8b33baf395c46760'
