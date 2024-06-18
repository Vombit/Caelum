import os
import time
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import QRunnable
import asyncio
import threading

lock = threading.Lock()


class Worker(QRunnable):
    """A QRunnable class for running a function asynchronously."""

    def __init__(self, function, *args, **kwargs):
        super().__init__()
        self.function = function
        self.args = args
        self.kwargs = kwargs

    @pyqtSlot()
    def run(self):
        """Run the function as a worker thread."""
        self.function(*self.args, **self.kwargs)



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


    @pyqtSlot(str, result=str)
    def downloader(self, file_name: str) -> None:
        """Download the file using a worker thread."""
        worker = Worker(self._async_downloader, self, file_name)
        self.thread_pool.start(worker)

    @staticmethod
    def _async_downloader(self, file_name: str):
        """Download all file chunks asynchronously."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Get the file hash and total number of chunks
        file_hash = db.get_file_by_name(file_name)[0][2]
        chunks = db.get_chunks(file_hash)
        split_chinks = split_chunks(chunks, len(db.get_bots()))

        view.page().runJavaScript("changeProgress(20)")

        # Update the progress bar in JavaScript and display a loading popup
        view.page().runJavaScript("openPopup('loading...')")

        threads = []
        for i, chunks in enumerate(split_chinks):
            my_thread = threading.Thread(
                target=bot_download, args=(chunks, self.t_bots[i], self.t_bots)
            )
            threads.append(my_thread)
            my_thread.start()

        view.page().runJavaScript("changeProgress(30)")

        for thread in threads:
            thread.join()

        # Merge all chunks and update the progress bar in JavaScript
        view.page().runJavaScript("openPopup('merging files...')")
        view.page().runJavaScript("changeProgress(60)")
        fm.merge_chunks(file_name, file_hash)
        view.page().runJavaScript("openPopup('uploaded!')")
        view.page().runJavaScript("changeProgress(100)")
        time.sleep(2)
        view.page().runJavaScript("changeProgress(0)")
        view.page().runJavaScript("closePopup()")

    @pyqtSlot()
    def upload(self):
        """Upload a file using a worker thread."""
        worker = Worker(self._async_upload, self)
        self.thread_pool.start(worker)

    @staticmethod
    def _async_upload(self):
        """Upload the selected file using TelegramBot."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        file_path, _ = QFileDialog.getOpenFileName(
            None, "Select File", "", "All Files (*)"
        )

        if file_path:
            # Update the progress bar in JavaScript and display a loading popup
            view.page().runJavaScript("openPopup('getting file hash...')")

            # Get the file hash and create chunks using FileManager
            file_hash = fm.get_file_hash(file_path)
            filename = os.path.basename(file_path)
            view.page().runJavaScript("changeProgress(20)")

            view.page().runJavaScript("openPopup('creating chunks...')")
            fm.process_file(file_path)
            view.page().runJavaScript("changeProgress(40)")

            # Update the database with the new file and its chunks
            db.add_file(filename, file_hash)

            split_chinks = split_chunks(fm.get_split_chunks(), len(db.get_bots()))

            view.page().runJavaScript("changeProgress(60)")

            # total = len(fm.get_split_chunks())

            view.page().runJavaScript("openPopup('uploading to the server...')")
            # Upload each chunk to the TelegramBot
            threads = []
            for i, chunks in enumerate(split_chinks):
                my_thread = threading.Thread(
                    target=bot_upload, args=(file_hash, chunks, self.t_bots[i])
                )
                threads.append(my_thread)
                my_thread.start()

            view.page().runJavaScript("changeProgress(70)")

            for thread in threads:
                thread.join()
            # Update the progress bar in JavaScript and close the loading popup
            view.page().runJavaScript("openPopup('done!')")
            view.page().runJavaScript("changeProgress(100)")
            view.page().runJavaScript("window.PyHandler.load()")
            time.sleep(2)
            view.page().runJavaScript("changeProgress(0)")
            view.page().runJavaScript("closePopup()")

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
