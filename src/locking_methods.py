"""Python port of LockingMethods.java, extended for the persistent engine.

Keeps the countdown window, the password dialog and the time helpers used by
blocks and deadlocks. The old one-shot orchestration (Time / AfterTime /
PasswordLock / DailyLock) now lives in block_runner.py."""

import threading
import time
import tkinter as tk
from datetime import datetime, time as dt_time, timedelta
from tkinter import messagebox

from gui_utils import exit_application


def parse_time(text):
    """Parse 'hour:minute' or 'hour:minute:second' like java.time.LocalTime.parse."""
    for fmt in ("%H:%M", "%H:%M:%S"):
        try:
            return datetime.strptime(text.strip(), fmt).time()
        except ValueError:
            continue
    raise ValueError("Invalid time format: " + text)


def next_midnight_epoch():
    """Epoch timestamp of the coming midnight."""
    now = datetime.now()
    return datetime.combine(now.date() + timedelta(days=1), dt_time(0, 0)).timestamp()


def today_window_epochs(start_text, end_text):
    """Epochs of today's window; an end at or before the start is treated as next day."""
    now = datetime.now()
    start = datetime.combine(now.date(), parse_time(start_text))
    end = datetime.combine(now.date(), parse_time(end_text))
    if end <= start:
        end += timedelta(days=1)
    return start.timestamp(), end.timestamp()


def show_countdown_window(hours, minutes, seconds):
    """Open the countdown window on a background thread (SwingUtilities.invokeLater)."""

    def run():
        CountdownTimerGUI(hours, minutes, seconds).run()

    threading.Thread(target=run, daemon=True).start()


class CountdownTimerGUI:
    def __init__(self, hours, minutes, seconds):
        self.root = tk.Tk()
        self.root.title("Countdown Timer")
        self.root.geometry("250x200")

        self.timer_label = tk.Label(self.root, font=("Arial", 24))
        self.timer_label.pack()

        # Calculate duration in seconds from input
        self.duration_in_seconds = hours * 3600 + minutes * 60 + seconds

    def run(self):
        self._start_timer()
        self.root.mainloop()

    def _start_timer(self):
        self.root.after(1000, self._tick)  # fires every second, like javax.swing.Timer

    def _tick(self):
        if self.duration_in_seconds > 0:
            hours, remaining_seconds = divmod(self.duration_in_seconds, 3600)
            minutes, seconds = divmod(remaining_seconds, 60)
            self.timer_label.config(text=f"{hours:02d}:{minutes:02d}:{seconds:02d}")
            self.duration_in_seconds -= 1
            self.root.after(1000, self._tick)
        else:
            messagebox.showinfo("Message", "Countdown Complete!")

    @staticmethod
    def timer_set():
        # Get duration input from the terminal
        print("Enter duration in hours:minutes:seconds (e.g., 2:30:00):")
        try:
            raw = input()
        except EOFError:
            print("No input provided.")
            return
        parts = raw.split(":")
        if len(parts) != 3:
            print("Invalid input format. Please enter in hours:minutes:seconds format.")
            return
        try:
            hours = int(parts[0])
            minutes = int(parts[1])
            seconds = int(parts[2])
            temp_sec = hours * 3600 + minutes * 60 + seconds
            show_countdown_window(hours, minutes, seconds)
            CountdownTimerGUI.timer(temp_sec)
        except ValueError:
            print("Invalid input. Please enter valid numbers.")

    @staticmethod
    def timer(time_sec):
        time_sec = time_sec * 1000
        extra = time_sec * 0.0061111  # drift correction kept from the original
        time_sec = time_sec + int(extra)
        time.sleep(time_sec / 1000)


class PasswordGUI:
    def __init__(self, stored_password=None, on_attempt=None):
        # stored_password: preset password, skips the "Set Password" phase
        # on_attempt: called with True/False after each unlock attempt
        self.files = None  # kept for parity with the Java original (unused)
        self.stored_password = stored_password
        self.on_attempt = on_attempt
        self.root = None
        self.password_entry = None
        self.set_password_button = None
        self._submitted = threading.Event()
        self._cancelled = threading.Event()
        self._thread = None

    def launch_gui(self):
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def wait_for_submit(self, should_abort=None):
        """Wait for the password; True when accepted, False when cancelled/aborted."""
        while not self._submitted.is_set():
            if self._cancelled.is_set():
                return False
            if should_abort is not None and should_abort():
                self.cancel()
                return False
            self._submitted.wait(timeout=0.25)
        return True

    def cancel(self):
        # tkinter calls must stay on the GUI thread; _poll_cancel closes the window
        self._cancelled.set()

    def _run(self):
        self.root = tk.Tk()
        self.root.title("Password Management")
        self.root.geometry("350x200")
        self.root.protocol("WM_DELETE_WINDOW", exit_application)  # EXIT_ON_CLOSE
        if self.stored_password is None:
            self._create_set_password_gui()
        else:
            self._create_enter_password_gui()
        self._poll_cancel()
        self.root.mainloop()

    def _poll_cancel(self):
        if self._cancelled.is_set():
            self.root.destroy()
        else:
            self.root.after(200, self._poll_cancel)

    def _create_set_password_gui(self):
        tk.Label(self.root, text="Set Password:").pack()
        self.password_entry = tk.Entry(self.root, show="*", width=20)
        self.password_entry.pack()
        self.set_password_button = tk.Button(self.root, text="Set Password",
                                             command=self._on_set_password)
        self.set_password_button.pack()

    def _on_set_password(self):
        # Save the user's input to the stored_password variable
        self.stored_password = self.password_entry.get()
        print("Password Set: " + self.stored_password)
        self.password_entry.delete(0, "end")
        self.set_password_button.config(state="disabled")
        # Simulate background tasks for 3 seconds, then allow password entry
        print("Please Wait....")
        self.root.after(3000, self._on_wait_done)

    def _on_wait_done(self):
        print("Ready..")
        print("Allowing password entry now")
        for widget in self.root.winfo_children():
            widget.destroy()
        self._create_enter_password_gui()

    def _create_enter_password_gui(self):
        tk.Label(self.root, text="Enter Password:").pack()
        self.password_entry = tk.Entry(self.root, show="*", width=20)
        self.password_entry.pack()
        submit_button = tk.Button(self.root, text="Submit Password",
                                  command=self._on_submit_password)
        submit_button.pack()

    def _on_submit_password(self):
        entered_password = self.password_entry.get()
        if self.stored_password is not None and entered_password == self.stored_password:
            print("Password Correct! Access Granted.")
            if self.on_attempt is not None:
                self.on_attempt(True)
            self.root.destroy()  # Close the GUI window
            self._submitted.set()  # Notify the waiting thread
        else:
            print("Incorrect Password! Access Denied.")
            if self.on_attempt is not None:
                self.on_attempt(False)
            self.password_entry.delete(0, "end")


class DailyLimitLock:
    @staticmethod
    def is_before(current_time, start_time):
        return current_time < start_time

    @staticmethod
    def is_after(current_time, end_time):
        return current_time > end_time
