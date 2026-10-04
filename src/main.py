"""Python port of Main.java: the console menu entry point."""

import sys

from app_list import Applications
from deadlock import Deadlock
from locking_methods import CountdownTimerGUI, DailyLimitLock, PasswordGUI
from website_list import BlacklistGUI


def select_class(choice):
    if choice == 1:
        print("Enter the name of this block:")
        list_name = input()
        print("Choose an option for Create Block:")
        print("a. Block for a time")
        print("b. Block After")
        print("c. Set A daily Limit")
        print("d. Set password")

        line = input().strip()
        block_choice = line[:1] if line else ""

        blacklist = BlacklistGUI()
        blacklist.launch_gui(list_name)
        blacklist.wait_for_submit()
        files = Applications.absolute_finder()

        if block_choice == "a":
            CountdownTimerGUI.time_lock(files, list_name)
        elif block_choice == "b":
            CountdownTimerGUI.after_time(files, list_name)
        elif block_choice == "c":
            DailyLimitLock.daily_lock(files, list_name)
        elif block_choice == "d":
            PasswordGUI.password_lock(files, list_name)
        else:
            print("Invalid option for Create Block")
    elif choice == 2:
        print("Edit Block is Under Development")
        sys.exit(0)
    elif choice == 3:
        print("Choose an option for Create Deadlock:")
        print("a. Block for a time")
        print("b. Block After")
        print("c. Set a daily Limit")
        print("d. Set password(Under Devolopment)")

        line = input().strip()
        deadlock_choice = line[:1] if line else ""

        if deadlock_choice == "a":
            Deadlock.timer_deadlock()
        elif deadlock_choice == "b":
            Deadlock.after_timer_deadlock()
        elif deadlock_choice == "c":
            # Deadlock.daily_deadlock_static()
            print("Under Development")
            sys.exit(0)
        elif deadlock_choice == "d":
            Deadlock.pass_deadlock()
        else:
            print("Invalid option for Create Deadlock")
    else:
        print("Invalid choice")


def main():
    print("Choose a number:")
    print("1. Create Block")
    print("2. Edit Block (Under Development)")
    print("3. Create Deadlock")

    choice = int(input())
    select_class(choice)


if __name__ == "__main__":
    main()
