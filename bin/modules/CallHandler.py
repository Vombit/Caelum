
import webbrowser
from PyQt5.QtCore import QObject, pyqtSlot, QThreadPool

from bin.modules.file_manager import FileManager
from bin.modules.telegram_bot import TelegramBot
from bin.modules.db_manager import DBManager

fm = FileManager()
db = DBManager()


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
