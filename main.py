import sys
import os
import time
from PyQt5.QtWidgets import QApplication, QFileDialog
from PyQt5.QtCore import QObject, pyqtSlot, QUrl, Qt, QThreadPool, QRunnable
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QIcon
import webbrowser
import asyncio
import threading
import numpy as np

from bin.modules.file_manager import FileManager
from bin.modules.telegram_bot import TelegramBot
from bin.modules.db_manager import DBManager

fm = FileManager()
db = DBManager()
lock = threading.Lock()

def bot_upload(file_hash:str, chunks:list, bot:object):
    for i, chunk in enumerate(chunks):
        chunk_path = f"{fm.split_chunks}/{chunk}"

        chunk_file_id = bot.send_document(chunk_path)
        chunk_file_hash = fm.get_file_hash(chunk_path)
        
        try:
            lock.acquire(True)
            db.add_chunk(file_hash, chunk_file_hash, chunk.split('_')[1], chunk_file_id)
        finally:
            lock.release()
       
        os.remove(chunk_path)
        
            
def bot_download(chunks:list, bot:object):
    for chunk in chunks:
        path_chunk = f'{fm.loaded_chunks}/{chunk[1]}_{chunk[3]}'
        
        loaded_file = bot.download_document(chunk[4])
        
        # Save the chunk to a file and remove it when done
        with open(path_chunk, 'wb') as new_file:
            new_file.write(loaded_file)
        
def split_chunks(file_list, num_threads):
    chunk_lists = np.array_split(file_list, num_threads)
        
    return chunk_lists

def resource_path(relative_path: str) -> str:
    """ Get the absolute path to the resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class Worker(QRunnable):
    """A QRunnable class for running a function asynchronously."""
    def __init__(self, fn, instance, *args, **kwargs):
        super(Worker, self).__init__()
        self.fn = fn
        self.instance = instance
        self.args = args
        self.kwargs = kwargs

    def run(self):
        """Run the function as a worker thread."""
        self.fn(self.instance, *self.args, **self.kwargs)

class CallHandler(QObject):
    def __init__(self):
        """
        Initialize the CallHandler class with TelegramBot and DBManager instances.
        """
        self.update_data_bots()
        super(CallHandler, self).__init__()
        
    @pyqtSlot()
    def update_data_bots(self) -> None:
        self.t_bots = []
        for obj in db.get_bots():
            self.t_bots.append(TelegramBot(obj[2], obj[3]))
            
    @pyqtSlot()
    def load(self) -> None:
        """
        Load bot token and file list from database to the frontend.
        """
        
        view.page().runJavaScript(f"block_settings.innerHTML = '';")
        tg_bots = db.get_bots()
        if tg_bots:
            for obj in tg_bots:
                view.page().runJavaScript(f"block_settings.appendChild(addBotLine(\"{obj[0]}\", \"{obj[2]}\", \"{obj[3]}\"));")
        
        # Get files from database and update GUI
        files = db.get_files()
        if files:
            view.page().runJavaScript(f"document.querySelector('.empt_files').style.display = 'none';")
            view.page().runJavaScript(f"document.querySelector('.items').innerHTML = '';")
            
        for chunk in files:
            file_size = round(len(db.get_chunks(chunk[2])) * 20 / 1024, 2 )
            view.page().runJavaScript(f"window.add_item('{str(chunk[1])}', {file_size})")

    @pyqtSlot(str, result=str)
    def del_item(self, file_name: str) -> None:
        main_file = db.get_file_by_name(file_name)
        
        db.del_file(main_file[0][1])
        db.del_chunks(main_file[0][2])
        
        self.load()

    @pyqtSlot()
    def open_git(self) -> None:
        webbrowser.open('https://github.com/Vombit/caelum')
    @pyqtSlot()
    def open_donation(self) -> None:
        webbrowser.open('https://www.donationalerts.com/r/vombit_donation')
    @pyqtSlot()
    def open_guide(self) -> None:
        webbrowser.open('https://github.com/Vombit/caelum/blob/main/MD/guide.md') 
    @pyqtSlot()
    def last_ver(self) -> None:
        webbrowser.open('https://github.com/Vombit/caelum/releases/latest') 
      
    @pyqtSlot(str, result=str)
    def downloader(self, file_name: str) -> None:
        """Download the file using a worker thread."""
        worker = Worker(self._async_downloader, self, file_name)
        QThreadPool.globalInstance().start(worker)
            
    @staticmethod
    def _async_downloader(self, file_name: str):
        """Download all file chunks asynchronously."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Get the file hash and total number of chunks
        file_hash = db.get_file_by_name(file_name)[0][2]
        chunks = db.get_chunks(file_hash)
        split_chinks = split_chunks(chunks, len(db.get_bots()))
        
        # Update the progress bar in JavaScript and display a loading popup
        view.page().runJavaScript("openPopup('loading...')")
        
        threads = []
        for i, chunks in enumerate(split_chinks):
            my_thread = threading.Thread(target=bot_download, args=(chunks, self.t_bots[i]))
            threads.append(my_thread)
            my_thread.start()
            
        for thread in threads:
            thread.join()
        
        # Merge all chunks and update the progress bar in JavaScript
        view.page().runJavaScript("openPopup('merging files...')")
        fm.merge_chunks(file_name)
        view.page().runJavaScript("openPopup('uploaded!')")
        view.page().runJavaScript("changeProgress(0)")
        time.sleep(2)
        view.page().runJavaScript("closePopup()")

    @pyqtSlot()
    def upload(self):
        """Upload a file using a worker thread."""
        worker = Worker(self._async_upload, self)
        QThreadPool.globalInstance().start(worker)
        
    @staticmethod
    def _async_upload(self):
        """Upload the selected file using TelegramBot."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        file_path, _ = QFileDialog.getOpenFileName(None, "Select File", "", "All Files (*)")
        
        if file_path:
            # Update the progress bar in JavaScript and display a loading popup
            view.page().runJavaScript("openPopup('getting file hash...')")
            
            # Get the file hash and create chunks using FileManager
            file_hash = fm.get_file_hash(file_path)
            filename = os.path.basename(file_path)

            view.page().runJavaScript("openPopup('creating chunks...')")
            fm.process_file(file_path)
        
            # Update the database with the new file and its chunks
            db.add_file(filename, file_hash)
            
            split_chinks = split_chunks(fm.get_split_chunks(), len(db.get_bots()))
            
            print(split_chinks)
            
            total = len(fm.get_split_chunks())
            
            view.page().runJavaScript("openPopup('uploading to the server...')")
            # Upload each chunk to the TelegramBot
            threads = []
            for i, chunks in enumerate(split_chinks):
                my_thread = threading.Thread(target=bot_upload, args=(file_hash, chunks, self.t_bots[i]))
                threads.append(my_thread)
                my_thread.start()
                
            for thread in threads:
                thread.join()
            # Update the progress bar in JavaScript and close the loading popup
            view.page().runJavaScript("openPopup('done!')")
            view.page().runJavaScript("changeProgress(0)")
            view.page().runJavaScript("window.PyHandler.load()")
            time.sleep(2)
            view.page().runJavaScript("closePopup()")

    @pyqtSlot()
    def add_bot(self) -> None:
        new_bot = db.add_bot()
        view.page().runJavaScript(f"block_settings.appendChild(addBotLine(\"{new_bot}\", \"NULL\", \"NULL\"));")

    @pyqtSlot(str, str)
    def settings_token(self, ids, arg:str) -> None:
        db.edit_bot("bot_token", arg, ids)
        self.update_data_bots()
        
    @pyqtSlot(str, str)
    def settings_id(self, ids, arg):
        db.edit_bot("chat_id", arg, ids)
        self.update_data_bots()

class WebEngine(QWebEngineView):
    def __init__(self):
        super(WebEngine, self).__init__()
        self.setContextMenuPolicy(Qt.NoContextMenu)

        # Set window title, icon and size
        self.setWindowTitle('Caelum')
        self.setFixedSize(1000, 620)
        self.setWindowIcon(QIcon(resource_path('bin/icon.ico')))

    def closeEvent(self, evt):
        # Override close event to clear http cache before closing application
        self.page().profile().clearHttpCache()
        super(WebEngine, self).closeEvent(evt)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    view = WebEngine()
    channel = QWebChannel()
    handler = CallHandler()
    channel.registerObject('PyHandler', handler)
    view.page().setWebChannel(channel)
    view.load(QUrl.fromLocalFile(resource_path('bin/index.html')))
    view.show()
    sys.exit(app.exec_())
