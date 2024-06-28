import threading
import webbrowser
import json
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
        self.view.page().runJavaScript(
            f"window.add_filters({filters})"
        )

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

    @pyqtSlot()
    def get_bots(self) -> None:
        bots = db.get_bots()
        json_data = []
        for item in bots:
            json_data.append({
                'id': item[0],
                'type': item[1],
                'token': item[2],
                'chat_id': item[3]
            })
        json_output = json.dumps(json_data, indent=4)

        self.view.page().runJavaScript(f"bots = {json_output}")
        self.view.page().runJavaScript("createBots()")

    @pyqtSlot(list)
    def set_bots(self, bots: list) -> None:
        for bot in bots:
            db.edit_bot(bot)

    @pyqtSlot(str)
    def remove_bot(self, bot_id) -> None:
        db.del_bot(bot_id)
        self.get_bots()




    # @staticmethod
    # def popup_message(self, message):
    #     view.page().runJavaScript(f"openPopup('{message}')")
    #     time.sleep(3)
    #     view.page().runJavaScript("closePopup()")


    # t(self.get_thread.terminate) вырубить поток


    @pyqtSlot()
    def add_bot(self) -> None:
        new_bot = db.add_bot()
        self.view.page().runJavaScript(
            f'block_settings.appendChild(addBotLine("{new_bot}", "NULL", "NULL"));'
        )


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
