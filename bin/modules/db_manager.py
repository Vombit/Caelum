import sqlite3


class DBManager:
    """
    pass
    """
    def __init__(self, db_path="db.sqlite3") -> None:
        self.__conn = sqlite3.connect(db_path, check_same_thread=False)
        self.__cursor = self.__conn.cursor()

        # Create tables if they don't exist
        self.__cursor.execute("""CREATE TABLE IF NOT EXISTS
                        files (
                            id INTEGER PRIMARY KEY,
                            file_name TEXT UNIQUE,
                            hash TEXT UNIQUE
                        )""")
        try:
            self.__cursor.execute("""ALTER TABLE files ADD COLUMN file_filters TEXT""")
        except sqlite3.OperationalError as e:
            print(e)

        self.__cursor.execute("""CREATE TABLE IF NOT EXISTS
                        chunks (
                            id INTEGER PRIMARY KEY,
                            main_file TEXT,
                            hash TEXT UNIQUE,
                            chunk_index INTEGER,
                            file_id TEXT,
                            key TEXT
                        )""")

        self.__cursor.execute("""CREATE TABLE IF NOT EXISTS
                        bot_settings (
                            id INTEGER PRIMARY KEY,
                            domain TEXT,
                            bot_token TEXT,
                            chat_id INTEGER
                        )""")

        # Add default values for the bot settings table
        self.__cursor.execute("SELECT * FROM bot_settings")
        rows = self.__cursor.fetchall()
        if not rows:
            self.__cursor.execute(
                "INSERT INTO bot_settings (domain, bot_token, chat_id) VALUES(?, ?, ?)",
                ("telegram", "NULL", "NULL"),
            )
            self.__conn.commit()

    def add_file(self, file_name: str, file_hash: str) -> None:
        """
        Add a new file to the 'files' table.

        Args:
            file_name (str): The name of the file.
            file_hash (str): The hash of the file content.
        """
        self.__cursor.execute(f"""INSERT INTO
                            'files' (file_name, hash)
                            VALUES(
                                '{file_name}',
                                '{file_hash}'
                            )
                            """)
        self.__conn.commit()

    def add_chunk(
        self, main_file_hash: str, chunk_hash: str, chunk_index: str, chunk_file_id: str
    ) -> None:
        """
        Add a new chunk to the 'chunks' table.

        Args:
            main_file_hash (str): The hash of the parent file.
            chunk_hash (str): The hash of the current chunk.
            chunk_index (int): The index of the chunk in the parent file.
            chunk_file_id (str): The ID of the current chunk.
        """
        self.__cursor.execute(f"""INSERT INTO
                        'chunks' (main_file, hash, chunk_index, file_id)
                        VALUES(
                            '{main_file_hash}',
                            '{chunk_hash}',
                            '{chunk_index}',
                            '{chunk_file_id}'
                        )
                        """)
        self.__conn.commit()

    def add_bot(self) -> int:
        """
        Add new bot to DB.

        Return: pos bot in data table
        """
        self.__cursor.execute("""INSERT INTO
                            'bot_settings' (domain, bot_token, chat_id)
                            VALUES(
                                'telegram',
                                NULL,
                                NULL
                            )
                            """)
        self.__conn.commit()
        new_bot_data = self.__cursor.lastrowid

        return new_bot_data

    def del_file(self, file_name: str) -> None:
        """
        Delete file from DB by name.

        Args:
            file_name (str): File name in DB.
        """
        self.__cursor.execute(f"DELETE FROM files WHERE file_name = '{file_name}'")
        self.__conn.commit()

    def del_chunks(self, main_file_hash: str) -> None:
        """
        Delete all chunks from DB by main file hash.

        Args:
            main_file_hash (str): Own file hash in DB.
        """
        self.__cursor.execute(f"DELETE FROM chunks WHERE main_file = '{main_file_hash}'")
        self.__conn.commit()

    def del_bot(self, bot_id: int) -> None:
        """
        Delete bot by id.

        Args:
            bot_id (int): bot index in db.
        """
        self.__cursor.execute(f"DELETE FROM bot_settings WHERE id = '{bot_id}'")
        self.__conn.commit()

    def edit_file(self) -> None:
        """Not implemented"""

    def edit_chunk(self) -> None:
        """Not implemented"""

    def edit_bot(self, name: str, token: str, ids: int) -> None:
        """
        Edit the bot settings.

        Args:
            name (str): The name of the setting to edit ('domain', 'bot_token' or 'chat_id').
            token (str): The new value for the setting.
            ids (int): The 'id' in table.
        """
        self.__cursor.execute(
            f"UPDATE bot_settings SET {name} = ? WHERE id = {ids}", (str(token),)
        )
        self.__conn.commit()

    def get_files(self) -> list:
        """
        Get all files in the 'files' table.

        Return:
            list all files.
        """
        self.__cursor.execute("SELECT * FROM files")

        return self.__cursor.fetchall()

    def get_file_by_name(self, name: str) -> list:
        """
        Get a file from the 'files' table by its name.

        Return: data file from table.
        """
        self.__cursor.execute(f"SELECT * FROM files WHERE file_name = '{name}'")

        return self.__cursor.fetchall()


    def get_filters(self) -> list:
        self.__cursor.execute('SELECT file_filters FROM files')
        filters_list = []
        for row in self.__cursor.fetchall():
            filters = row[0].split(', ')
            filters_list.extend(filters)

        unique_filters = sorted(set(filters_list))

        return unique_filters

    def get_filter_files(self, filter: str) -> list:
        self.__cursor.execute(f"SELECT * FROM files WHERE file_filters GLOB '*{filter}*';")

        return self.__cursor.fetchall()


    def get_chunk(self, file_hash: str) -> str:
        """
        Get chunk info
        """
        self.__cursor.execute(f"SELECT * FROM chunks WHERE hash = '{file_hash}'")

        return self.__cursor.fetchall()

    def get_chunks(self, main_file_hash: str) -> list:
        """
        Get all chunks from the 'chunks'
        table that belong to a specific parent file.

        Return: all chunks.
        """
        self.__cursor.execute(
            f"SELECT * FROM chunks WHERE main_file = '{main_file_hash}'"
        )

        return self.__cursor.fetchall()

    def get_bots(self) -> tuple:
        """
        Get the current bots settings.

        Return: data all bots.
        """
        self.__cursor.execute("SELECT * FROM bot_settings")

        return self.__cursor.fetchall()
