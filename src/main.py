"""Console menu for the blocker (Python port of Main.java, extended).

Blocks and deadlocks persist in data/data.json and are resumed on startup;
the watchdog relaunches this entry point if it dies mid-block."""

import block_runner
import deadlock
import storage
from create_block_gui import CreateBlockGUI
from edit_block_gui import EditBlockGUI


def select_class(choice):
    if choice == 1:
        CreateBlockGUI()  # collects name/sites/apps/lock type, saves and starts
        block_runner.monitor_active()
    elif choice == 2:
        EditBlockGUI()
        block_runner.monitor_active()
    elif choice == 3:
        print("Choose an option for Create Deadlock:")
        print("a. Block for a time")
        print("b. Block After")
        print("c. Set a daily Limit")
        print("d. Set password(Under Devolopment)")

        line = input().strip()
        deadlock_choice = line[:1] if line else ""

        if deadlock_choice == "a":
            deadlock.timer_deadlock()
        elif deadlock_choice == "b":
            deadlock.after_timer_deadlock()
        elif deadlock_choice == "c":
            deadlock.daily_deadlock()
        elif deadlock_choice == "d":
            deadlock.pass_deadlock()
        else:
            print("Invalid option for Create Deadlock")
    else:
        print("Invalid choice")


def main():
    storage.set_entry_point("main.py")
    for item in block_runner.resume_active():
        print("Resumed active: " + item)
    while True:
        print("Choose a number:")
        print("1. Create Block")
        print("2. Edit Block")
        print("3. Create Deadlock")
        print("4. Exit")
        try:
            choice = int(input())
        except ValueError:
            print("Invalid choice")
            continue
        if choice == 4:
            return
        select_class(choice)


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print()
