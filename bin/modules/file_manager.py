# FileManager class for managing file processing, splitting, and merging

import os
import hashlib


class FileManager:
    def __init__(self, base_path="TEMP", base_output="output") -> None:
        """
        Initialize the FileManager with default paths and chunk size.
        Create necessary directories if they don't exist yet.
        """
        self.base_path = self.create_path(base_path)
        self.split_chunks = self.create_path(self.base_path + "/split")
        self.loaded_chunks = self.create_path(self.base_path + "/loaded")
        self.output_path = self.create_path(base_output)

        self.chunk_size = 20  # size on MB (type: int)

    def create_path(self, path: str) -> str:
        """
        Create a new directory if it doesn't exist.

        Args:
            path (str): The absolute path of the directory to create.

        Return: The created directory path.
        """
        if not os.path.exists(path):
            os.mkdir(path)

        return os.path.abspath(path)

    def get_file_hash(self, file_path: str):
        block_size = 1024 * 1024
        hash_md5 = hashlib.md5()
        hash_progress = 0

        def generator():
            nonlocal hash_md5, hash_progress
            with open(file_path, "rb") as f:
                block = f.read(block_size)
                while block:
                    hash_md5.update(block)
                    block = f.read(block_size)
                    hash_progress += block_size
                    yield hash_progress

        return generator(), hash_md5


    def get_file_size(self, file_path: str) -> int:
        return os.path.getsize(file_path)

    def merge_chunks(self, filename: str, filehash: str, filepath=None) -> None:
        """
        Merge all loaded chunks with the given
        filename and save to output path.

        Args:
            filename (str): The name of the file to merge.
        """
        if not filepath:
            filepath = self.loaded_chunks

        chunks = []
        for file in os.listdir(filepath):
            if filehash in file:
                chunks.append(file)
        chunks = sorted(chunks, key=lambda x: int(x.split("_")[1]))

        try:
            with open(self.output_path + "/" + filename, "wb") as output_file:
                for chunk in chunks:
                    with open(
                        os.path.join(filepath, chunk), "rb"
                    ) as input_file:
                        output_file.write(input_file.read())
                    os.remove(filepath + "/" + chunk)
        except Exception:
            return self.merge_chunks(filename)

    def split_file(self, file_path: str) -> any:
        """
        Split the given file into chunks of given size and yield each chunk.

        Args:
            file_path (str): The absolute path of the file to split.

        Yield: A tuple containing the filename and the data of each chunk.
        """
        with open(file_path, "rb") as f:
            i = 0
            while True:
                data = f.read(self.chunk_size * 1024 * 1024)
                if not data:
                    break
                i += 1

                yield self.hash_filename + "_" + str(i), data

    def process_file(self, file_path: str):
        """
        Split the given file into chunks and save them.

        Args:
            file_path (str): The absolute path of the file to process.
        """
        gen, hasher = self.get_file_hash(file_path)
        list(gen)
        self.hash_filename = hasher.hexdigest()

        for file_name, data in self.split_file(file_path):
            with open(self.split_chunks + "/" + file_name, "wb") as f:
                f.write(data)

            yield file_name.split('_')[1]


    def get_split_chunks(self, dir_chunks=None) -> list:
        """
        Get a list of all split chunks in the `split_chunks` directory.

        Return: A list of file names of all split chunks.
        """
        if not dir_chunks:
            dir_chunks = self.split_chunks

        chunks = [file for file in os.listdir(dir_chunks)]
        chunks = sorted(chunks, key=lambda x: int(x.split("_")[1]))

        return chunks
