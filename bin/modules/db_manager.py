import sqlite3

class DBManager:
    def __init__(self) -> None:
        self.conn = sqlite3.connect('db.sqlite3', check_same_thread=False)
        self.cursor = self.conn.cursor()
        
        # Create tables if they don't exist
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS 
                        files (
                            id INTEGER PRIMARY KEY,
                            file_name TEXT UNIQUE,
                            hash TEXT UNIQUE
                        )''')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS 
                        chunks (
                            id INTEGER PRIMARY KEY,
                            main_file TEXT,
                            hash TEXT UNIQUE,
                            chunk_index INTEGER,
                            file_id TEXT,
                            key TEXT
                        )''')
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS 
                        bot_settings (
                            id INTEGER PRIMARY KEY,
                            domain TEXT,
                            bot_token TEXT,
                            chat_id INTEGER
                        )''')
        
        # Add default values for the bot settings table
        self.cursor.execute('INSERT INTO bot_settings (domain, bot_token, chat_id) VALUES(?, ?, ?)', ('telegram', 'none', 'none'))


    def add_file(self, file_name: str, file_hash: str) -> None:
        '''
        Add a new file to the 'files' table.
        
        Args:
            file_name (str): The name of the file.
            file_hash (str): The hash of the file content.
        '''
        self.cursor.execute(f'''INSERT INTO 
                            'files' (file_name, hash) 
                            VALUES(
                                '{file_name}', 
                                '{file_hash}'
                            )
                            ''')
        self.conn.commit()
        
    def add_chunk(self, main_file_hash: str, chunk_hash: str, chunk_index: str, chunk_file_id: str) -> None:
        '''
        Add a new chunk to the 'chunks' table.
        
        Args:
            main_file_hash (str): The hash of the parent file.
            chunk_hash (str): The hash of the current chunk.
            chunk_index (int): The index of the chunk in the parent file.
            chunk_file_id (str): The ID of the current chunk.
        '''
        self.cursor.execute(f'''INSERT INTO 
                        'chunks' (main_file, hash, chunk_index, file_id) 
                        VALUES(
                            '{main_file_hash}', 
                            '{chunk_hash}', 
                            '{chunk_index}', 
                            '{chunk_file_id}'
                        )
                        ''')
        self.conn.commit()
       
    def add_bot(self, bot_token: str, chat_id:str) -> None:
        '''
        Add or update the current bot settings.
        
        Args:
            bot_token (str): The token of the bot.
            chat_id (str): The ID of the chat where to send messages.
        '''
        self.cursor.execute(f'''INSERT INTO 
                            bot_settings (domain, bot_token, chat_id) 
                            VALUES(?, ?, ?), (
                                'telegram', 
                                {bot_token}, 
                                {chat_id}
                            )
                            ''')
        self.conn.commit()


    def edit_file(self) -> None:
        '''Not implemented'''
        pass
    def edit_chunk(self) -> None:
        '''Not implemented'''
        pass
    

    def edit_bot(self, name:str, token:str) -> None:
        '''
        Edit the bot settings.
        
        Args:
            name (str): The name of the setting to edit ('domain', 'bot_token' or 'chat_id').
            token (str): The new value for the setting.
        '''
        self.cursor.execute(f'UPDATE bot_settings SET {name} = ? WHERE id = 1', (str(token),))
        self.conn.commit()
    
    def get_files(self) -> list:
        '''Get all files in the 'files' table.'''
        self.cursor.execute("SELECT * FROM files")
        return self.cursor.fetchall()
    
    def get_file_by_name(self, name:str) -> list:
        '''Get a file from the 'files' table by its name.'''
        self.cursor.execute(f"SELECT * FROM files WHERE file_name = '{name}'")
        return self.cursor.fetchall()
    
    def get_chunks(self, main_file_hash:str) -> list:
        '''Get all chunks from the 'chunks' table that belong to a specific parent file.'''
        self.cursor.execute(f"SELECT * FROM chunks WHERE main_file = '{main_file_hash}'")
        return self.cursor.fetchall()
    
    def get_bot(self) -> tuple:
        '''Get the current bot settings.'''
        self.cursor.execute("SELECT * FROM bot_settings WHERE id=1")
        return self.cursor.fetchone()
