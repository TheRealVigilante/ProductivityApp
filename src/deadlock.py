"""Python port of Deadlock.java: stricter blocks that keep the whole
workstation locked."""

import subprocess
import sys
import time
from datetime import datetime

from locking_methods import (CountdownTimerGUI, DailyLimitLock, PasswordGUI,
                             parse_time, show_countdown_window)


def lock_workstation():
    # subprocess.run already waits for the process to complete
    result = subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"])
    if result.returncode == 0:
        print("Workstation locked successfully.")
    else:
        print("Failed to lock the workstation. Exit code: " + str(result.returncode))


class Deadlock:
    def __init__(self, deadlock_name, start_time, end_time, is_active):
        self.deadlock_name = deadlock_name
        self.start_time = start_time
        self.end_time = end_time
        self.active = is_active
        self.daily_deadlock()

    @staticmethod
    def pass_deadlock():
        password_gui = PasswordGUI()
        password_gui.launch_gui()
        password_gui.wait_for_submit()
        while True:
            print("Deadlock is active")
            lock_workstation()
            time.sleep(1)  # Sleep for 1 second

    @staticmethod
    def timer_deadlock():
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
            while temp_sec >= 0:
                print("Deadlock is active")
                lock_workstation()
                temp_sec -= 1
                time.sleep(1)  # Sleep for 1 second
            sys.exit(0)
        except ValueError:
            print("Invalid input. Please enter valid numbers.")

    @staticmethod
    def after_timer_deadlock():
        CountdownTimerGUI.timer_set()
        while not CountdownTimerGUI.is_midnight():
            print("Deadlock is active")
            lock_workstation()
            time.sleep(1)  # Sleep for 1 second

    @staticmethod
    def daily_deadlock_static():
        """Java: Deadlock.DailyDeadlock (currently not reachable from the menu)."""
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
                    # deadlock
                    while not DailyLimitLock.is_after(datetime.now().time(), end_time):
                        print("Inside prohibited time, apps are locked")
                        Deadlock("Test", start_time, end_time, True)
                        time.sleep(30)
                    print("Outside prohibited time, unlocking now")
                    break
        except ValueError:
            print("Invalid time format. Please use the format 'hour:minute'.")

    def daily_deadlock(self):
        now = datetime.now().time()
        greater_equal_start_time = now >= self.start_time
        less_equal_end_time = now <= self.end_time

        while greater_equal_start_time and less_equal_end_time and self.active:
            print("Deadlock is active")
            lock_workstation()
            time.sleep(1)  # Sleep for 1 second

            now = datetime.now().time()
            greater_equal_start_time = now >= self.start_time
            less_equal_end_time = now <= self.end_time
