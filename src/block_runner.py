"""Background engine that engages, monitors and releases blocks.

start_block() runs the engagement on a background thread (locking the apps,
blocking the websites, keeping the heartbeat alive); stop_block() deactivates
and releases. resume_active() re-engages persisted work on startup and cleans
up entries that expired while the app was down."""

import threading
import time

import deadlock
import storage
import watchdog
from app_list import Applications
from locking_methods import (PasswordGUI, next_midnight_epoch,
                             show_countdown_window, today_window_epochs)
from website_list import BlacklistGUI

HEARTBEAT_CHECK_EVERY = 5  # loops re-read data.json at most every 5 seconds

_password_guis = {}  # block name -> PasswordGUI while a password block waits


# ----- applying and releasing locks -----

def _websites_to_block(block):
    whitelist = {BlacklistGUI.format(w) for w in block.whitelist}
    return [w for w in block.websites if BlacklistGUI.format(w) not in whitelist]


def _apply_locks(block):
    Applications.lock_applications(block.apps)
    for website in _websites_to_block(block):
        website = BlacklistGUI.format(website)
        print("Locking: " + website)
        BlacklistGUI.block_website(website)


def _release_locks(block):
    Applications.unlock_applications(block.apps)
    for website in block.websites:
        print("Unlocking: " + website)
        BlacklistGUI.unblock_website(website)
        # also try the normalized form so no hosts entry survives a crash
        # (raw "https://..." entries never match the formatted hosts line)
        formatted = BlacklistGUI.format(website)
        if formatted != website:
            BlacklistGUI.unblock_website(formatted)


# ----- engagement helpers -----

def _block_is_active(block):
    current = storage.get_block(block.name)
    return bool(current and current.active)


def _wait_until(block, deadline):
    """Sleep until deadline while keeping the heartbeat alive; False when stopped."""
    tick = 0
    while True:
        storage.touch_heartbeat()
        if tick % HEARTBEAT_CHECK_EVERY == 0 and not _block_is_active(block):
            return False
        if deadline is not None and time.time() >= deadline:
            return True
        time.sleep(1)
        tick += 1


def _mark_inactive(name, token=None):
    current = storage.get_block(name)
    if current is None:
        return
    if token is not None and current.lock_start_epoch != token:
        return  # a newer engagement took over; leave it alone
    current.active = False
    current.updated_at = time.time()
    storage.upsert_block(current)


def _prepare_for_start(block):
    now = time.time()
    block.active = True
    block.lock_start_epoch = now
    if block.lock_type == "timer":
        block.end_epoch = now + (block.duration_seconds or 0)
    elif block.lock_type == "after":
        block.lock_start_epoch = now + (block.duration_seconds or 0)  # delay phase
        block.end_epoch = next_midnight_epoch()
    else:  # daily and password run until stopped or unlocked
        block.end_epoch = None
    block.created_at = block.created_at or now
    block.updated_at = now


# ----- public API -----

def start_block(block, resume=False):
    """Persist the block (unless resuming) and engage it on a background thread."""
    if not resume:
        _prepare_for_start(block)
        storage.upsert_block(block)
    thread = threading.Thread(target=_engage, args=(block, resume), daemon=True)
    thread.start()
    return thread


def stop_block(name):
    """Deactivate a block and release its locks; the runner thread winds down."""
    current = storage.get_block(name)
    if current is None:
        return
    current.active = False
    current.updated_at = time.time()
    storage.upsert_block(current)
    _release_locks(current)
    gui = _password_guis.get(name)
    if gui is not None:
        gui.cancel()


def monitor_active():
    """Keep the process (and the heartbeat) alive while one-shot blocks run."""
    while True:
        data = storage.load_data()
        if not any(b.get("active") and b.get("lock_type") != "daily"
                   for b in data["blocks"]):
            return
        storage.touch_heartbeat()
        time.sleep(1)


def should_resume(block):
    """True when a persisted block still has to run."""
    if block.lock_type in ("daily", "password"):
        return True
    if block.end_epoch is None:
        return True
    if block.lock_type == "after" and block.lock_start_epoch \
            and time.time() < block.lock_start_epoch:
        return True
    return time.time() < block.end_epoch


def resume_active():
    """Re-engage persisted work on startup; clean up entries that expired."""
    resumed = []
    state = storage.get_deadlock()
    if state and state.get("active"):
        if deadlock.should_resume(state):
            state["resumed"] = True
            threading.Thread(target=deadlock.engage_deadlock, args=(state,),
                             daemon=True).start()
            resumed.append("deadlock:" + str(state.get("type")))
        else:
            storage.clear_deadlock()
            storage.log_event("deadlock_ended", reason="expired")
    for block in storage.get_blocks():
        if not block.active:
            continue
        if should_resume(block):
            start_block(block, resume=True)
            resumed.append("block:" + block.name)
        else:
            # expired while the app was down: clean up leftover hosts entries
            _release_locks(block)
            _mark_inactive(block.name)
            storage.log_event("block_ended", block=block.name, reason="expired")
    return resumed


# ----- engagement implementations -----

def _engage(block, resumed):
    token = block.lock_start_epoch  # identifies this engagement for _mark_inactive
    started_epoch = time.time()
    storage.log_event("block_started", block=block.name,
                      lock_type=block.lock_type, resumed=resumed)
    watchdog.ensure_watchdog()
    storage.touch_heartbeat()
    try:
        if block.lock_type == "timer":
            _engage_timer(block)
        elif block.lock_type == "after":
            _engage_after(block)
        elif block.lock_type == "daily":
            _engage_daily(block)
        else:  # password
            _engage_password(block)
    finally:
        _release_locks(block)
        _mark_inactive(block.name, token)
        storage.log_event("block_ended", block=block.name,
                          seconds=round(time.time() - started_epoch))
        storage.touch_heartbeat()


def _engage_timer(block):
    _apply_locks(block)
    remaining = max(0, int((block.end_epoch or time.time()) - time.time()))
    hours, rem = divmod(remaining, 3600)
    minutes, seconds = divmod(rem, 60)
    show_countdown_window(hours, minutes, seconds)
    _wait_until(block, block.end_epoch)


def _engage_after(block):
    # delay phase first, then locked until midnight (Java: AfterTime)
    if block.lock_start_epoch and time.time() < block.lock_start_epoch:
        if not _wait_until(block, block.lock_start_epoch):
            return
    _apply_locks(block)
    print("\nWait till midnight and it will reset")
    _wait_until(block, block.end_epoch)


def _engage_daily(block):
    locked = False
    while True:
        start, end = today_window_epochs(block.daily_start or "00:00",
                                         block.daily_end or "00:00")
        now = time.time()
        if now < start:
            if locked:
                _release_locks(block)
                locked = False
            print("Before start time, please wait...")
            if not _wait_until(block, start):
                return
        elif now < end:
            if not locked:
                _apply_locks(block)
                locked = True
                print("Inside prohibited time, apps are locked")
            if not _wait_until(block, end):
                return
            print("Outside prohibited time, unlocking apps now")
            _release_locks(block)
            locked = False
        else:
            # past today's end: wait for tomorrow's window
            if not _wait_until(block, start + 86400):
                return


def _engage_password(block):
    _apply_locks(block)
    gui = PasswordGUI(stored_password=block.password or None,
                      on_attempt=lambda success: storage.log_event(
                          "unlock_attempt", block=block.name, success=success))
    _password_guis[block.name] = gui
    try:
        gui.launch_gui()
        gui.wait_for_submit(should_abort=lambda: not _block_is_active(block))
    finally:
        _password_guis.pop(block.name, None)
