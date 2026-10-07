"""Detached watchdog process.

Spawned whenever a block or deadlock engages. It polls data/data.json and
data/heartbeat.txt: while active work exists but the heartbeat went stale
(the app was killed or hung), it relaunches the recorded entry point so the
engagement resumes. It removes its pid file and exits once nothing is active.
"""

import subprocess
import sys
import time
from pathlib import Path

import storage

SRC_DIR = Path(__file__).resolve().parent

POLL_SECONDS = 10
HEARTBEAT_STALE_SECONDS = 30
RELAUNCH_BACKOFF_SECONDS = 60
PID_FRESH_SECONDS = 60

DETACHED_PROCESS = 0x00000008
CREATE_NEW_PROCESS_GROUP = 0x00000200


def ensure_watchdog():
    """Spawn the watchdog once, unless a live one recently touched its pid file."""
    pid_path = storage.pid_path()
    try:
        if pid_path.exists() and time.time() - pid_path.stat().st_mtime < PID_FRESH_SECONDS:
            return
    except OSError:
        pass
    # the app is alive right now, so the heartbeat is fresh
    storage.touch_heartbeat()
    subprocess.Popen(
        [sys.executable, str(Path(__file__).resolve())],
        creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP,
        close_fds=True,
        cwd=str(SRC_DIR),
    )


def run():
    last_relaunch = 0.0
    while True:
        _touch_pid_file()
        if not storage.has_active_work():
            _remove_pid_file()
            return
        heartbeat = storage.read_heartbeat()
        now = time.time()
        if (heartbeat is None or now - heartbeat > HEARTBEAT_STALE_SECONDS) \
                and now - last_relaunch > RELAUNCH_BACKOFF_SECONDS:
            last_relaunch = now
            entry = storage.load_data().get("entry_point") or "main.py"
            print("Watchdog: heartbeat stale, relaunching " + entry)
            subprocess.Popen(
                [sys.executable, str(SRC_DIR / entry)],
                creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP,
                close_fds=True,
                cwd=str(SRC_DIR),
            )
        time.sleep(POLL_SECONDS)


def _touch_pid_file():
    storage.ensure_data_dir()
    storage.pid_path().write_text(str(time.time()), encoding="utf-8")


def _remove_pid_file():
    try:
        storage.pid_path().unlink()
    except OSError:
        pass


if __name__ == "__main__":
    run()
