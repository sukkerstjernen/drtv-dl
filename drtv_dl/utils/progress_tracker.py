import sys
from drtv_dl.utils import settings
import time


class ProgressTracker:
    def __init__(self, initial_size, filename):
        self.total_size = int(initial_size) if initial_size != "?" else initial_size
        self.downloaded = 0
        self.filename = filename
        self.start_time = time.time()
        self.longest_line = 0

    def get_appropriate_unit(self, size):
        if size == "?":
            return 'MB', 1024 * 1024
        if size < 1024 * 1024:
            return 'KB', 1024
        elif size < 1024 * 1024 * 1024:
            return 'MB', 1024 * 1024
        else:
            return 'GB', 1024 * 1024 * 1024

    def update(self, chunk_size):
        if settings.SUPPRESS_OUTPUT:
            return
        self.downloaded += chunk_size
        if self.total_size != "?" and self.downloaded > self.total_size:
            self.total_size = self.downloaded
        unit, divisor = self.get_appropriate_unit(self.total_size)
        downloaded_unit = self.downloaded / divisor
        total_unit = "?" if self.total_size == "?" else self.total_size / divisor
        
        elapsed_time = time.time() - self.start_time
        if elapsed_time > 0:
            dlspeed = self.downloaded / (elapsed_time * 1024 * 1024)
            percentage_done = "?" if self.total_size == "?" else f"{(downloaded_unit / total_unit) * 100:.0f}"
            progress_line = f'\r {" " * 2}~ {downloaded_unit:.2f}/{total_unit:.2f} {unit} at {dlspeed:.2f} MB/s - {percentage_done}%'
            padded_line = progress_line.ljust(self.longest_line)
            self.longest_line = max(self.longest_line, len(progress_line))
            print(padded_line, end='', file=sys.stderr, flush=True)

    def finish(self):
        if not settings.SUPPRESS_OUTPUT:
            print(file=sys.stderr)