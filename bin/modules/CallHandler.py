import os
import webbrowser
from PyQt5.QtCore import QObject, pyqtSlot, QThreadPool, QThread
from PyQt5.QtWidgets import QFileDialog

from bin.modules.file_manager import FileManager
from bin.modules.telegram_bot import TelegramBot
from bin.modules.db_manager import DBManager

fm = FileManager()
db = DBManager()

from bin.modules.additional_functions import (
    split_chunks,
    bot_upload
    
)


import threading
lock = threading.Lock()



class UPLOADER(QThread):
    def __init__(self, file_path):
        QThread.__init__(self)
        self.file_path = file_path

    def __del__(self):
        self.wait()

    def run(self):
        self.t_bots = []
        for obj in db.get_bots():
            bot = TelegramBot(obj[2], obj[3])
            self.t_bots.append(bot)
            
        file_hash = fm.get_file_hash(self.file_path)
        filename = os.path.basename(self.file_path)
        fm.process_file(self.file_path)

        db.add_file(filename, file_hash)

        split_chinks = split_chunks(fm.get_split_chunks(), len(db.get_bots()))

        # Upload each chunk to the TelegramBot
        threads = []
        for i, chunks in enumerate(split_chinks):
            my_thread = threading.Thread(
                target=bot_upload, args=(file_hash, chunks, self.t_bots[i])
            )
            threads.append(my_thread)
            my_thread.start()


        for thread in threads:
            thread.join()












class CallHandler(QObject):
    def __init__(self, view):
        self.view = view
        self.thread_pool = QThreadPool()
        super(CallHandler, self).__init__()

    # base
    def set_items(self, files):
        # hide "empt_files" div
        self.view.page().runJavaScript(
            "document.querySelector('.empt_files').style.display = 'none';"
        )
        # clear files list
        self.view.page().runJavaScript(
            "document.querySelector('.items').innerHTML = '';"
        )
        # add files
        for chunk in files:
            file_size = round(len(db.get_chunks(chunk[2])) * 20 / 1024, 2)
            self.view.page().runJavaScript(
                f"window.add_item('{str(chunk[1])}', {file_size})"
            )

    @pyqtSlot()
    def start_page(self) -> None:
        files = db.get_files()
        if not files:
            return
        self.set_items(files)

    @pyqtSlot(str)
    def filtered_page(self, filter: str) -> None:
        files = db.get_filter_files(filter)
        if not files:
            return
        self.set_items(files)

    @pyqtSlot()
    def load_data(self) -> None:
        self.start_page()

        filters = db.get_filters()
        bots = db.get_bots()
        print(bots)
        self.view.page().runJavaScript(
            f"window.add_filters({filters})"
        )

        # rewrite this
        self.view.page().runJavaScript("block_settings.innerHTML = '';")
        for obj in bots:
            self.view.page().runJavaScript(
                f'block_settings.appendChild(addBotLine("{obj[0]}", "{obj[2]}", "{obj[3]}"));'
            )
        # ###



    @pyqtSlot()
    def upload(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            None, "Select File", "", "All Files (*)"
        )
        if file_path:
            self.uploader = UPLOADER(file_path)
            self.uploader.start()


            # t(self.get_thread.terminate) вырубить поток







    # @staticmethod
    # def popup_message(self, message):
    #     view.page().runJavaScript(f"openPopup('{message}')")
    #     time.sleep(3)
    #     view.page().runJavaScript("closePopup()")




    @pyqtSlot()
    def update_data_bots(self) -> None:
        self.t_bots = []
        for obj in db.get_bots():
            bot = TelegramBot(obj[2], obj[3])
            self.t_bots.append(bot)




    @pyqtSlot(str, result=str)
    def del_item(self, file_name: str) -> None:
        main_file = db.get_file_by_name(file_name)

        db.del_file(main_file[0][1])
        db.del_chunks(main_file[0][2])

        self.load()

    @pyqtSlot()
    def add_bot(self) -> None:
        new_bot = db.add_bot()
        view.page().runJavaScript(
            f'block_settings.appendChild(addBotLine("{new_bot}", "NULL", "NULL"));'
        )

    @pyqtSlot(str)
    def remove_bot(self, bot_id) -> None:
        db.del_bot(bot_id)

    @pyqtSlot(str, str)
    def settings_token(self, ids, arg: str) -> None:
        db.edit_bot("bot_token", arg, ids)
        self.update_data_bots()

    @pyqtSlot(str, str)
    def settings_id(self, ids, arg):
        db.edit_bot("chat_id", arg, ids)
        self.update_data_bots()




















    @pyqtSlot()
    def open_git(self) -> None:
        webbrowser.open("https://github.com/Vombit/caelum")

    @pyqtSlot()
    def open_donation(self) -> None:
        webbrowser.open("https://www.donationalerts.com/r/vombit_donation")

    @pyqtSlot()
    def open_guide(self) -> None:
        webbrowser.open("https://github.com/Vombit/caelum/blob/main/MD/guide.md")

    @pyqtSlot()
    def last_ver(self) -> None:
        webbrowser.open("https://github.com/Vombit/caelum/releases/latest")
