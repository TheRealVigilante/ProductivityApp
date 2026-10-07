"""Persistent state for the blocker.

data/data.json holds the saved blocks, the current deadlock engagement and
the entry point the watchdog should relaunch. data/events.jsonl is the
append-only statistics log, data/heartbeat.txt is touched while any block or
deadlock runs, and data/watchdog.pid guards the single watchdog instance.
All paths derive from DATA_DIR (override it in tests)."""

import json
import os
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


@dataclass
class Block:
    name: str
    apps: list = field(default_factory=list)
    websites: list = field(default_factory=list)
    whitelist: list = field(default_factory=list)
    lock_type: str = "timer"  # "timer" | "after" | "daily" | "password"
    duration_seconds: int = 0
    daily_start: str = ""  # "HH:MM"
    daily_end: str = ""
    password: str = ""
    active: bool = False
    lock_start_epoch: float = None
    end_epoch: float = None
    created_at: float = None
    updated_at: float = None

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, d):
        return cls(
            name=d.get("name", ""),
            apps=list(d.get("apps", [])),
            websites=list(d.get("websites", [])),
            whitelist=list(d.get("whitelist", [])),
            lock_type=d.get("lock_type", "timer"),
            duration_seconds=d.get("duration_seconds", 0),
            daily_start=d.get("daily_start", ""),
            daily_end=d.get("daily_end", ""),
            password=d.get("password", ""),
            active=d.get("active", False),
            lock_start_epoch=d.get("lock_start_epoch"),
            end_epoch=d.get("end_epoch"),
            created_at=d.get("created_at"),
            updated_at=d.get("updated_at"),
        )


# ----- paths (functions so tests can retarget DATA_DIR) -----

def data_path():
    return DATA_DIR / "data.json"


def events_path():
    return DATA_DIR / "events.jsonl"


def heartbeat_path():
    return DATA_DIR / "heartbeat.txt"


def pid_path():
    return DATA_DIR / "watchdog.pid"


def ensure_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


# ----- data.json -----

def load_data():
    try:
        with open(data_path(), encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        data = {}
    data.setdefault("entry_point", "main.py")
    data.setdefault("blocks", [])
    data.setdefault("deadlock", None)
    return data


def save_data(data):
    ensure_data_dir()
    tmp = data_path().with_suffix(".json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, data_path())


def set_entry_point(entry):
    data = load_data()
    data["entry_point"] = entry
    save_data(data)


# ----- blocks -----

def get_blocks():
    return [Block.from_dict(d) for d in load_data()["blocks"]]


def get_block(name):
    for block in get_blocks():
        if block.name == name:
            return block
    return None


def upsert_block(block):
    data = load_data()
    blocks = data["blocks"]
    for i, d in enumerate(blocks):
        if d.get("name") == block.name:
            blocks[i] = block.to_dict()
            break
    else:
        blocks.append(block.to_dict())
    save_data(data)


def delete_block(name):
    data = load_data()
    data["blocks"] = [d for d in data["blocks"] if d.get("name") != name]
    save_data(data)


# ----- deadlock engagement -----

def get_deadlock():
    return load_data().get("deadlock")


def set_deadlock(state):
    data = load_data()
    data["deadlock"] = state
    save_data(data)


def clear_deadlock():
    data = load_data()
    data["deadlock"] = None
    save_data(data)


# ----- events (statistics log) -----

def log_event(event_type, block=None, **detail):
    ensure_data_dir()
    record = {"ts": time.time(), "event": event_type, "block": block}
    record.update(detail)
    with open(events_path(), "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


def iter_events():
    try:
        with open(events_path(), encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue
    except OSError:
        return


# ----- aggregation for the Statistics page -----

def total_blocked_seconds():
    return sum(e.get("seconds", 0) for e in iter_events()
               if e.get("event") == "block_ended")


def per_block_summary():
    summary = {}
    for e in iter_events():
        name = e.get("block")
        entry = summary.setdefault(name, {"starts": 0, "seconds": 0, "last_ended": None})
        if e.get("event") == "block_started":
            entry["starts"] += 1
        elif e.get("event") == "block_ended":
            entry["seconds"] += e.get("seconds", 0)
            entry["last_ended"] = e.get("ts")
    return summary


def failed_unlock_count():
    return sum(1 for e in iter_events()
               if e.get("event") == "unlock_attempt" and e.get("success") is False)


def last_7_days_totals():
    cutoff = time.time() - 7 * 86400
    totals = {}
    for e in iter_events():
        if e.get("event") == "block_ended" and e.get("ts", 0) >= cutoff:
            day = datetime.fromtimestamp(e["ts"]).strftime("%Y-%m-%d")
            totals[day] = totals.get(day, 0) + e.get("seconds", 0)
    return totals


# ----- heartbeat / watchdog helpers -----

def touch_heartbeat():
    ensure_data_dir()
    heartbeat_path().write_text(str(time.time()), encoding="utf-8")


def read_heartbeat():
    try:
        return float(heartbeat_path().read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return None


def has_active_work():
    data = load_data()
    deadlock_state = data.get("deadlock")
    if deadlock_state and deadlock_state.get("active"):
        return True
    return any(block.get("active") for block in data["blocks"])
