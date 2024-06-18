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

    