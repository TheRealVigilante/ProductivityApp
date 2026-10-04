"""Temporary smoke test for the Python port (deleted after running)."""
import os
import sys
import tempfile
from datetime import time as dt_time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

import app_list
import deadlock
import gui_utils
import locking_methods
import main
import main_gui
import website_list

from app_list import Applications
from locking_methods import parse_time
from website_list import BlacklistGUI

# BlacklistGUI.format
assert BlacklistGUI.format("www.youtube.com") == "www.youtube.com"
assert BlacklistGUI.format("https://youtube.com") == "www.youtube.com"
assert BlacklistGUI.format("https://www.youtube.com") == "www.youtube.com"

# hosts file round-trip on a scratch file
handle, path = tempfile.mkstemp()
os.close(handle)
BlacklistGUI.hosts_path = path
with open(path, "w") as f:
    f.write("# test hosts\n")
BlacklistGUI.block_website("www.youtube.com")
BlacklistGUI.block_website("www.facebook.com")
BlacklistGUI.unblock_website("youtube.com")
with open(path) as f:
    content = f.read()
assert "youtube.com" not in content
assert "www.facebook.com" in content

# parse_time
assert parse_time("09:30") == dt_time(9, 30)
assert parse_time("21:05:10") == dt_time(21, 5, 10)
try:
    parse_time("bogus")
    raise AssertionError("expected ValueError")
except ValueError:
    pass

# remove_duplicates mutates in place, is_empty
items = ["a", "b", "a", "c"]
Applications.remove_duplicates(items)
assert items == ["a", "b", "c"]
assert Applications.is_empty([])
assert not Applications.is_empty(["x"])

os.remove(path)
print("All smoke tests passed.")
