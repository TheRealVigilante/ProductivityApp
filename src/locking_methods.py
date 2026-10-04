"""Python port of LockingMethods.java.

CountdownTimerGUI (window + terminal helpers), PasswordGUI and
DailyLimitLock, which implement the different block types.
"""

import threading
import time
import tkinter as tk
from datetime import datetime
from tkinter import messagebox

from app_list import Applications
from gui_utils import exit_application
from website_list import BlacklistGUI


def parse_time(text):
    """Parse 'hour:minute' or 'hour:minute:second' like java.time.LocalTime.parse."""
    for fmt in ("%H:%M", "%H:%M:%S"):
        try:
            return datetime.strptime(text.strip(), fmt).time()
        except ValueError:
            continue
    raise ValueError("Invalid time format: " + text)


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

            show_countdown_window(hours, minutes, seconds)
            temp_sec = hours * 3600 + minutes * 60 + seconds
            CountdownTimerGUI.timer(temp_sec)
        except ValueError:
            print("Invalid input. Please enter valid numbers.")

    @staticmethod
    def is_midnight():
        current_time = datetime.now().time()
        return current_time.hour == 0 and current_time.minute == 0

    @staticmethod
    def timer(time_sec):
        time_sec = time_sec * 1000
        extra = time_sec * 0.0061111  # drift correction kept from the original
        time_sec = time_sec + int(extra)
        time.sleep(time_sec / 1000)

    @classmethod
    def time_lock(cls, files, list_name):
        """Java: CountdownTimerGUI.Time - block for a time."""
        if Applications.is_empty(files):
            print("No files is selected, Try picking some first")
            return
        BlacklistGUI.lock_websites(list_name)
        Applications.lock_applications(files)
        cls.timer_set()
        Applications.unlock_applications(files)
        BlacklistGUI.unlock_websites(list_name)
        # do you want to do anything else? if yes, recurse main. if no, exit

    @classmethod
    def after_time(cls, files, list_name):
        """Java: CountdownTimerGUI.AfterTime - block after a delay, until midnight."""
        if Applications.is_empty(files):
            print("No files is selected")
            return
        cls.timer_set()
        BlacklistGUI.lock_websites(list_name)
        Applications.lock_applications(files)
        print("\nWait till midnight and it will reset")
        while not cls.is_midnight():
            time.sleep(1)  # the original busy-spins here; sleep to avoid 100% cpu
        BlacklistGUI.unlock_websites(list_name)
        Applications.unlock_applications(files)


class PasswordGUI:
    def __init__(self):
        self.files = None  # kept for parity with the Java original (unused)
        self.stored_password = None
        self.root = None
        self.password_entry = None
        self.set_password_button = None
        self._submitted = threading.Event()
        self._thread = None

    def launch_gui(self):
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def wait_for_submit(self):
        self._submitted.wait()  # Wait until the button is clicked

    def _run(self):
        self.root = tk.Tk()
        self.root.title("Password Management")
        self.root.geometry("350x200")
        self.root.protocol("WM_DELETE_WINDOW", exit_application)  # EXIT_ON_CLOSE
        self._create_set_password_gui()
        self.root.mainloop()

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
            self.root.destroy()  # Close the GUI window
            self._submitted.set()  # Notify the waiting thread
        else:
            print("Incorrect Password! Access Denied.")
            self.password_entry.delete(0, "end")

    @staticmethod
    def password_lock(files, list_name):
        Applications.lock_applications(files)
        BlacklistGUI.lock_websites(list_name)
        password_gui = PasswordGUI()
        password_gui.launch_gui()
        password_gui.wait_for_submit()
        Applications.unlock_applications(files)
        BlacklistGUI.unlock_websites(list_name)


class DailyLimitLock:
    @staticmethod
    def daily_lock(files, list_name):
        print("Enter the start time in 24 hour format (hour:minute): ")
        start_time_str = input()
        print("Enter the end time in 24 hour format (hour:minute): ")
        end_time_str = input()

        try:
            start_time = parse_time(start_time_str)
            end_time = parse_time(end_time_str)
            print(start_time)
            print(end_time)
            while True:
                if DailyLimitLock.is_before(datetime.now().time(), start_time):
                    print("Before start time, please wait...")
                    time.sleep(10)
                    print(datetime.now().time())
                else:
                    Applications.lock_applications(files)
                    BlacklistGUI.lock_websites(list_name)
                    while not DailyLimitLock.is_after(datetime.now().time(), end_time):
                        print("Inside prohibited time, apps are locked")
                        time.sleep(30)
                    print("Outside prohibited time, unlocking apps now")
                    Applications.unlock_applications(files)
                    BlacklistGUI.unlock_websites(list_name)
                    break
        except ValueError:
            print("Invalid time format. Please use the format 'hour:minute'.")

    @staticmethod
    def is_before(current_time, start_time):
        return current_time < start_time

    @staticmethod
    def is_after(current_time, end_time):
        return current_time > end_time
