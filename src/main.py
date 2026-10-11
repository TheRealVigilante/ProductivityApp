"""Console menu for the blocker (Python port of Main.java, extended).

Blocks and deadlocks persist in data/data.json and are resumed on startup;
the watchdog relaunches this entry point if it dies mid-block. On start it
requests administrator rights (UAC): hosts-file edits and app file locks
need them."""

import ctypes
import os
import sys

import block_runner
import deadlock
import storage
from create_block_gui import CreateBlockGUI
from edit_block_gui import EditBlockGUI


def is_admin():
    """True when the process already runs with administrator rights."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except AttributeError:  # not Windows: there is nothing to elevate
        return True


def run_as_admin():
    """Relaunch this script elevated (shows the Windows UAC prompt)."""
    script = os.path.abspath(sys.argv[0])
    # ShellExecuteW returns a value greater than 32 when the launch worked
    return ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, f'"{script}"', None, 1) > 32


def unblock_all():
    from website_list import BlacklistGUI
    print("Unblocking all inactive websites and flushing DNS...")
    active_sites = set()
    for block in storage.get_blocks():
        if block.active:
            active_sites.update(block.websites)
        else:
            for site in block.websites:
                try:
                    BlacklistGUI.unblock_website(site)
                except Exception:
                    pass
    try:
        BlacklistGUI.clean_unblocked_hosts(active_sites)
    except Exception:
        pass
    print("Hosts file cleaned and Windows DNS resolver cache flushed.")
    print("Note: If your browser still shows a block page, close and reopen your browser.")


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
    elif choice == 4:
        unblock_all()
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
        print("4. Clean Hosts / Unblock All")
        print("5. Exit")
        try:
            choice = int(input())
        except ValueError:
            print("Invalid choice")
            continue
        if choice == 5:
            return
        select_class(choice)



if __name__ == "__main__":
    try:
        if not is_admin():
            print("Requesting administrator access...")
            if run_as_admin():
                sys.exit(0)  # the elevated instance takes over
            print("Administrator access was refused; website blocking may not work.")
        main()
    except (KeyboardInterrupt, EOFError):
        print()
