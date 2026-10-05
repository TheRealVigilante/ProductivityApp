"""Python port of Deadlock.java, extended with persistence and resume.

Deadlocks are the strict variant: they lock the whole workstation via
rundll32.exe while active, persist to data/data.json so they survive
restarts, and are kept alive by the watchdog."""

import subprocess
import time

import storage
import watchdog
from locking_methods import (CountdownTimerGUI, PasswordGUI, next_midnight_epoch,
                              parse_time, show_countdown_window,
                              today_window_epochs)

LOCK_POLL_SECONDS = 1


def lock_workstation():
    # subprocess.run already waits for the process to complete
    result = subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"])
    if result.returncode == 0:
        print("Workstation locked successfully.")
    else:
        print("Failed to lock the workstation. Exit code: " + str(result.returncode))


def should_resume(state):
    """True when a persisted deadlock still has to run."""
    if not state.get("active"):
        return False
    kind = state.get("type")
    if kind in ("daily", "password"):
        return True
    end = state.get("end_epoch")
    return end is None or time.time() < end


def engage_deadlock(state):
    """Run a persisted deadlock engagement until it ends or is deactivated."""
    started_epoch = time.time()
    resumed = bool(state.pop("resumed", False))
    storage.log_event("deadlock_started", deadlock=state.get("type"), resumed=resumed)
    watchdog.ensure_watchdog()
    storage.touch_heartbeat()
    try:
        kind = state.get("type")
        if kind == "timer":
            _engage_timer(state)
        elif kind == "after":
            _engage_after(state)
        elif kind == "daily":
            _engage_daily(state)
        else:  # password
            _engage_password(state)
    finally:
        storage.clear_deadlock()
        storage.log_event("deadlock_ended", seconds=round(time.time() - started_epoch))


def _is_active():
    state = storage.get_deadlock()
    return bool(state and state.get("active"))


def _wait_until(deadline):
    """Sleep until deadline keeping the heartbeat alive; False when deactivated."""
    tick = 0
    while True:
        storage.touch_heartbeat()
        if tick % 5 == 0 and not _is_active():
            return False
        if deadline is not None and time.time() >= deadline:
            return True
        time.sleep(LOCK_POLL_SECONDS)
        tick += 1


def _lock_loop(state, deadline=None):
    """Original deadlock behavior: lock the workstation every second."""
    while True:
        print("Deadlock is active")
        lock_workstation()
        storage.touch_heartbeat()
        if deadline is not None and time.time() >= deadline:
            return True
        time.sleep(LOCK_POLL_SECONDS)
        if not _is_active():
            return False


def _engage_timer(state):
    remaining = max(0, int((state.get("end_epoch") or time.time()) - time.time()))
    hours, rem = divmod(remaining, 3600)
    minutes, seconds = divmod(rem, 60)
    show_countdown_window(hours, minutes, seconds)
    _lock_loop(state, state.get("end_epoch"))


def _engage_after(state):
    # delay phase before the locking starts (Java: CountdownTimerGUI.TimerSet wait)
    lock_start = state.get("lock_start_epoch")
    if lock_start and time.time() < lock_start:
        if not _wait_until(lock_start):
            return
    _lock_loop(state, state.get("end_epoch"))


def _engage_daily(state):
    # recurring: wait for the window, lock through it, repeat the next day
    while True:
        start, end = today_window_epochs(state.get("daily_start", "00:00"),
                                         state.get("daily_end", "00:00"))
        now = time.time()
        if now < start:
            if not _wait_until(start):
                return
        elif now < end:
            if not _lock_loop(state, end):
                return
        else:
            if not _wait_until(start + 86400):
                return


def _engage_password(state):
    # password phase first, then the lock loop, like the original PassDeadlock
    gui = PasswordGUI(stored_password=state.get("password") or None,
                      on_attempt=lambda success: storage.log_event(
                          "unlock_attempt", block="deadlock", success=success))
    gui.launch_gui()
    if not gui.wait_for_submit(should_abort=lambda: not _is_active()):
        return
    if state.get("password") is None and gui.stored_password:
        # persist the chosen password so a resume goes straight to entry
        state["password"] = gui.stored_password
        storage.set_deadlock(state)
    _lock_loop(state, None)


# ----- console entry points (menu case 3) -----

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
    except ValueError:
        print("Invalid input. Please enter valid numbers.")
        return
    duration = hours * 3600 + minutes * 60 + seconds
    state = {"type": "timer", "active": True,
             "duration_seconds": duration,
             "lock_start_epoch": time.time(),
             "end_epoch": time.time() + duration}
    storage.set_deadlock(state)
    engage_deadlock(state)


def after_timer_deadlock():
    CountdownTimerGUI.timer_set()  # asks for the duration and waits it out
    state = {"type": "after", "active": True,
             "lock_start_epoch": None,
             "end_epoch": next_midnight_epoch()}
    storage.set_deadlock(state)
    engage_deadlock(state)


def daily_deadlock():
    print("Enter the start time in 24 hour format (hour:minute): ")
    start_time_str = input()
    print("Enter the end time in 24 hour format (hour:minute): ")
    end_time_str = input()
    try:
        parse_time(start_time_str)
        parse_time(end_time_str)
    except ValueError:
        print("Invalid time format. Please use the format 'hour:minute'.")
        return
    state = {"type": "daily", "active": True,
             "daily_start": start_time_str.strip(),
             "daily_end": end_time_str.strip(),
             "lock_start_epoch": None, "end_epoch": None}
    storage.set_deadlock(state)
    engage_deadlock(state)


def pass_deadlock():
    state = {"type": "password", "active": True,
             "lock_start_epoch": time.time(),
             "end_epoch": None, "password": None}
    storage.set_deadlock(state)
    engage_deadlock(state)
