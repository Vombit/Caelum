import threading
import webbrowser
from PyQt5.QtCore import QObject, pyqtSlot, QThreadPool, pyqtSignal
from PyQt5.QtWidgets import QFileDialog

from bin.modules.file_manager import FileManager
from bin.modules.db_manager import DBManager

from bin.modules.downloader import Downloader
from bin.modules.uploader import Uploader

fm = FileManager()
db = DBManager()
lock = threading.Lock()


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
            self.uploader = Uploader(file_path)
            self.uploader.finished.connect(self.load_data)
            self.uploader.start()


    @pyqtSlot(str)
    def download(self, filename: str) -> None:
        self.downloader = Downloader(filename)
        self.downloader.start()

    @pyqtSlot(str)
    def del_item(self, file_name: str) -> None:
        main_file = db.get_file_by_name(file_name)

        db.del_file(main_file[0][1])
        db.del_chunks(main_file[0][2])

        self.load_data()

    # some problem return undefined (js func popup_menu_creator)
    @pyqtSlot(str, result=list)
    def popup_get_filters(self, filename: str) -> list:
        file_tags = db.get_filters_by_name(filename)

        self.view.page().runJavaScript(f"tags = {list(file_tags)}")
        self.view.page().runJavaScript("createTag()")

        return list(file_tags)

    @pyqtSlot(str, list)
    def popup_set_filters(self, file_name: str, filters_list: list) -> None:
        db.set_filters(file_name, filters_list)
        self.load_data()





















    # @staticmethod
    # def popup_message(self, message):
    #     view.page().runJavaScript(f"openPopup('{message}')")
    #     time.sleep(3)
    #     view.page().runJavaScript("closePopup()")


    # t(self.get_thread.terminate) вырубить поток


    # @pyqtSlot()
    # def update_data_bots(self) -> None:
    #     self.t_bots = []
    #     for obj in db.get_bots():
    #         bot = TelegramBot(obj[2], obj[3])
    #         self.t_bots.append(bot)





    # @pyqtSlot()
    # def add_bot(self) -> None:
    #     new_bot = db.add_bot()
    #     view.page().runJavaScript(
    #         f'block_settings.appendChild(addBotLine("{new_bot}", "NULL", "NULL"));'
    #     )

    # @pyqtSlot(str)
    # def remove_bot(self, bot_id) -> None:
    #     db.del_bot(bot_id)

    # @pyqtSlot(str, str)
    # def settings_token(self, ids, arg: str) -> None:
    #     db.edit_bot("bot_token", arg, ids)
    #     self.update_data_bots()

    # @pyqtSlot(str, str)
    # def settings_id(self, ids, arg):
    #     db.edit_bot("chat_id", arg, ids)
    #     self.update_data_bots()







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
