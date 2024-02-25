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

from bin.modules.file_manager import FileManager
from bin.modules.telegram_bot import TelegramBot
from bin.modules.db_manager import DBManager

fm = FileManager()
db = DBManager()
tb = None

def resource_path(relative_path):
    """ Get the absolute path to the resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class Worker(QRunnable):
    """A QRunnable class for running a function asynchronously."""
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    def run(self):
        """Run the function as a worker thread."""
        self.fn(*self.args, **self.kwargs)

class CallHandler(QObject):
    def __init__(self):
        """
        Initialize the CallHandler class with TelegramBot and DBManager instances.
        """
        global tb
        tb = TelegramBot()
        tg_bot = db.get_bot()
        if tg_bot:
            tb = TelegramBot(tg_bot[2], tg_bot[3])

        super(CallHandler, self).__init__()
        

    @pyqtSlot()
    def load(self):
        """
        Load bot token and file list from database to the frontend.
        """
        
        # Get bot data from database
        tg_bot = db.get_bot()
        if tg_bot:
            # Set bot token and chat ID in JavaScript
            view.page().runJavaScript(f"document.getElementById('bot_token').setAttribute('value', \"{tg_bot[2]}\");")
            view.page().runJavaScript(f"document.getElementById('chat_id').setAttribute('value', {tg_bot[3]});")
        
        # Get files from database and update GUI
        files = db.get_files()
        if files:
            view.page().runJavaScript(f"document.querySelector('.empt_files').style.display = 'none';")
            view.page().runJavaScript(f"document.querySelector('.items').innerHTML = '';")
            
        for chunk in files:
            file_size = round(len(db.get_chunks(chunk[2])) * 20 / 1024, 2 )
            view.page().runJavaScript(f"window.add_item('{str(chunk[1])}', {file_size})")

    @pyqtSlot()
    def open_git(self):
        webbrowser.open('https://github.com/Vombit/caelum')
    @pyqtSlot()
    def open_donation(self):
        webbrowser.open('https://www.donationalerts.com/r/vombit_donation')
    @pyqtSlot()
    def open_guide(self):
        webbrowser.open('https://github.com/Vombit/caelum/blob/main/MD/guide.md') 
    @pyqtSlot()
    def last_ver(self):
        webbrowser.open('https://github.com/Vombit/caelum/releases/latest') 
      
        
    @pyqtSlot(str, result=str)
    def downloader(self, file_name: str) -> None:
        """Download the file using a worker thread."""
        worker = Worker(self._async_downloader, file_name)
        QThreadPool.globalInstance().start(worker)

    @staticmethod
    def _download_chunk(tb, chunk_id, item_name):
        """Download a single file chunk using TelegramBot."""
        loaded_file = tb.download_document(chunk_id)
        path_chunk = f'{fm.loaded_chunks}/{item_name}'
        
        # Save the chunk to a file and remove it when done
        with open(path_chunk, 'wb') as new_file:
            new_file.write(loaded_file)
            
    @staticmethod
    def _async_downloader(file_name: str):
        """Download all file chunks asynchronously."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Get the file hash and total number of chunks
        file_hash = db.get_file_by_name(file_name)[0][2]
        total = len(db.get_chunks(file_hash))
        
        # Update the progress bar in JavaScript and display a loading popup
        view.page().runJavaScript("openPopup('loading...')")
        
        # Download all chunks
        for i, chunk in enumerate(db.get_chunks(file_hash)):
            item_name = f"{chunk[1]}_{chunk[3]}"
            chunk_id = chunk[4]

            CallHandler._download_chunk(tb, chunk_id, item_name)
            view.page().runJavaScript(f"changeProgress({ (i+1) / total * 100 })")
            
        # Merge all chunks and update the progress bar in JavaScript
        view.page().runJavaScript("openPopup('merging files...')")
        fm.merge_chunks(file_name)
        view.page().runJavaScript("openPopup('uploaded!')")
        view.page().runJavaScript(f"changeProgress(0)")
        time.sleep(2)
        view.page().runJavaScript("closePopup()")


    @pyqtSlot()
    def upload(self):
        """Upload a file using a worker thread."""
        worker = Worker(self._async_upload)
        QThreadPool.globalInstance().start(worker)

    @staticmethod
    def _async_upload():
        """Upload the selected file using TelegramBot."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Open a file dialog to select a file
        file_path, _ = QFileDialog.getOpenFileName(None, "Select File", "", "All Files (*)")
        
        if file_path:
            # Update the progress bar in JavaScript and display a loading popup
            view.page().runJavaScript("openPopup('getting file hash...')")
            
            # Get the file hash and create chunks using FileManager
            file_hash = fm.get_file_hash(file_path)
            filename = os.path.basename(file_path)

            view.page().runJavaScript("openPopup('creating chunks...')")
            fm.process_file(file_path)
            chunks = fm.get_split_chunks()

            # Update the database with the new file and its chunks
            db.add_file(filename, file_hash)
            
            total = len(chunks)
            view.page().runJavaScript("openPopup('uploading to the server...')")
            # Upload each chunk to the TelegramBot
            for i, chunk in enumerate(chunks):
                chunk_path = f"{fm.split_chunks}/{chunk}"

                chunk_file_id = tb.send_document(chunk_path)
                chunk_file_hash = fm.get_file_hash(chunk_path)
                
                db.add_chunk(file_hash, chunk_file_hash, i+1, chunk_file_id)

                os.remove(chunk_path)
                view.page().runJavaScript(f"changeProgress({ (i+1) / total * 100 })")
                
            # Update the progress bar in JavaScript and close the loading popup
            view.page().runJavaScript("openPopup('done!')")
            view.page().runJavaScript(f"changeProgress(0)")
            time.sleep(2)
            view.page().runJavaScript("closePopup()")


    @pyqtSlot(str, result=str)
    def settings_token(self, arg):
        tb.update_bot_token(arg)
        
        db.edit_bot("bot_token", arg)
        
    @pyqtSlot(str, result=str)
    def settings_id(self, arg):
        tb.update_chat_id = arg
        db.edit_bot("chat_id", arg)

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
