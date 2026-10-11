"""Smoke tests for the Python port and the persistence layer.

Run with:  python smoke_test.py
The storage tests retarget storage.DATA_DIR to a temp folder and the
hosts-file test uses a scratch file, so nothing on this machine is modified."""

import os
import sys
import tempfile
import time
from datetime import time as dt_time
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

import app_list
import block_runner
import deadlock
import gui_utils
import locking_methods
import main
import main_gui
import storage
import watchdog
import website_list

from app_list import Applications
from locking_methods import next_midnight_epoch, parse_time, today_window_epochs
from website_list import BlacklistGUI

# --- original checks (format / hosts round-trip / parse / dedupe) ---
assert BlacklistGUI.format("www.youtube.com") == "www.youtube.com"
assert BlacklistGUI.format("https://youtube.com") == "www.youtube.com"
assert BlacklistGUI.format("https://www.youtube.com") == "www.youtube.com"

handle, hosts_scratch = tempfile.mkstemp()
os.close(handle)
BlacklistGUI.hosts_path = hosts_scratch
with open(hosts_scratch, "w") as f:
    f.write("# test hosts\n")
BlacklistGUI.block_website("www.youtube.com")
BlacklistGUI.block_website("www.facebook.com")
BlacklistGUI.unblock_website("youtube.com")
with open(hosts_scratch) as f:
    content = f.read()
assert "youtube.com" not in content
assert "www.facebook.com" in content

assert parse_time("09:30") == dt_time(9, 30)
assert parse_time("21:05:10") == dt_time(21, 5, 10)
try:
    parse_time("bogus")
    raise AssertionError("expected ValueError")
except ValueError:
    pass

items = ["a", "b", "a", "c"]
Applications.remove_duplicates(items)
assert items == ["a", "b", "c"]
assert Applications.is_empty([])
assert not Applications.is_empty(["x"])
os.remove(hosts_scratch)

# --- time helpers ---
assert next_midnight_epoch() > time.time()
start, end = today_window_epochs("09:00", "17:00")
assert start < end
start, end = today_window_epochs("22:00", "06:00")  # overnight window
assert end - start == 8 * 3600

# --- storage layer (temp data dir) ---
storage.DATA_DIR = Path(tempfile.mkdtemp())
block = storage.Block(name="Study", apps=["C:\\apps\\x.exe"],
                      websites=["youtube.com"], whitelist=["wikipedia.org"],
                      lock_type="timer", duration_seconds=30)
storage.upsert_block(block)
loaded = storage.get_block("Study")
assert loaded is not None and loaded.duration_seconds == 30
assert loaded.whitelist == ["wikipedia.org"]

# upsert replaces by name
storage.upsert_block(storage.Block(name="Study", lock_type="daily",
                                   daily_start="09:00", daily_end="17:00"))
blocks = storage.get_blocks()
assert len(blocks) == 1 and blocks[0].lock_type == "daily"
assert storage.has_active_work() is False

# deadlock state and resume decision
storage.set_deadlock({"type": "timer", "active": True, "end_epoch": time.time() + 10})
assert storage.has_active_work() is True
assert deadlock.should_resume({"type": "timer", "active": True,
                               "end_epoch": time.time() + 10}) is True
assert deadlock.should_resume({"type": "timer", "active": True,
                               "end_epoch": time.time() - 10}) is False
assert deadlock.should_resume({"type": "password", "active": True}) is True
assert deadlock.should_resume({"type": "daily", "active": False}) is False
storage.clear_deadlock()
assert storage.has_active_work() is False

# resume decision for blocks
running = storage.Block(name="R", lock_type="timer", active=True,
                        end_epoch=time.time() + 60)
expired = storage.Block(name="E", lock_type="timer", active=True,
                        end_epoch=time.time() - 60)
delayed = storage.Block(name="D", lock_type="after", active=True,
                        lock_start_epoch=time.time() + 60,
                        end_epoch=next_midnight_epoch())
recurring = storage.Block(name="W", lock_type="daily", active=True)
assert block_runner.should_resume(running) is True
assert block_runner.should_resume(expired) is False
assert block_runner.should_resume(delayed) is True
assert block_runner.should_resume(recurring) is True

# heartbeat
storage.touch_heartbeat()
assert abs(storage.read_heartbeat() - time.time()) < 5

# events + aggregation
storage.log_event("block_started", block="Study")
storage.log_event("unlock_attempt", block="Study", success=False)
storage.log_event("block_ended", block="Study", seconds=60)
events = list(storage.iter_events())
assert len(events) == 3
assert storage.total_blocked_seconds() == 60
summary = storage.per_block_summary()["Study"]
assert summary["starts"] == 1 and summary["seconds"] == 60
assert storage.failed_unlock_count() == 1
assert len(storage.last_7_days_totals()) == 1

# whitelist filtering from the runner
filtered = block_runner._websites_to_block(storage.Block(
    name="T", websites=["youtube.com", "wikipedia.org"], whitelist=["wikipedia.org"]))
assert filtered == ["youtube.com"]

# delete
storage.delete_block("Study")
assert storage.get_blocks() == []

print("All smoke tests passed.")
