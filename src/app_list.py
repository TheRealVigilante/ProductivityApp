"""Python port of AppList.java.

AppList is a named list of applications; Applications picks files with a
dialog and locks/unlocks them with OS-level file locks (Windows only).
"""

import os
import tkinter as tk
from tkinter import filedialog

try:
    import msvcrt
except ImportError:  # the file locking relies on Windows, like the original
    msvcrt = None


class AppList:
    def __init__(self, name):
        self.name = name
        self.applications = []

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def get_applications(self):
        return self.applications

    def add_app(self, app):
        self.applications.append(app)


class Applications:
    # Open file handles holding an OS-level lock, keyed by file path.
    file_locks = {}

    @staticmethod
    def absolute_finder():
        """Show a file chooser repeatedly until the user cancels."""
        root = tk.Tk()
        root.withdraw()
        files = []

        while True:
            path = filedialog.askopenfilename(parent=root, title="Choose a file")
            if path:
                path = os.path.abspath(path)
                files.append(path)
                print("Selected file: " + path)
            else:
                print("Selection Done")
                break  # Break out of the loop when the user cancels

        root.destroy()
        Applications.remove_duplicates(files)
        return files

    @staticmethod
    def pick_files(parent=None):
        """Multi-select file picker; returns absolute paths (possibly empty)."""
        paths = filedialog.askopenfilenames(parent=parent, title="Choose files")
        return [os.path.abspath(p) for p in paths]

    @staticmethod
    def remove_duplicates(files):
        seen = set()
        unique = []
        for path in files:
            if path not in seen:
                seen.add(path)
                unique.append(path)
        files[:] = unique

    @staticmethod
    def is_empty(files):
        return len(files) == 0

    @staticmethod
    def app_locker(file_path):
        """Hold an exclusive lock on the file (Java: RandomAccessFile + FileChannel.lock)."""
        if msvcrt is None:
            raise OSError("File locking is only supported on Windows")
        try:
            handle = open(file_path, "a+b")  # "rw": created if missing
            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
            Applications.file_locks[file_path] = handle
        except OSError as e:
            print(e)

    @staticmethod
    def unlock_applications(files):
        for path in files:
            print("UnLocking: " + path)
            Applications.app_unlocker(path)

    @staticmethod
    def lock_applications(files):
        for path in files:
            print("Locking: " + path)
            Applications.app_locker(path)

    @staticmethod
    def app_unlocker(file_path):
        handle = Applications.file_locks.get(file_path)
        if handle is not None:
            try:
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)  # Releasing the lock
                handle.close()
                del Applications.file_locks[file_path]
            except OSError as e:
                print(e)
