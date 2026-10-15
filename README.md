# Focus Engine — Application Blocker & Deadlock Tool

A Windows productivity suite that blocks distracting applications and websites on customizable schedules, with strict workstation "deadlock" modes. Built with a modern dark slate UI, persistent background engine, crash recovery, and automated hosts-file management.

---

## Project History

### v1 — The Java Original

The project started as a Java/Swing desktop application. It locked applications with OS-level file locks, blocked websites through the Windows hosts file, and ran workstation deadlocks. State lived only in memory (nothing survived an exit) and several screens were incomplete. The original sources are preserved in [`java_archive/`](java_archive/).

### v2 — The Python Port

The application was ported to pure Python: `tkinter` replaced Swing, `msvcrt` replaced Java's file locks, and `subprocess` replaced `ProcessBuilder`. It runs using only the Python standard library.

### v3 — Persistence and Watchdog Engine

Persistent state was added: blocks and deadlocks are stored in `data/` and resume automatically across reboots, engagements run on a background heartbeat engine, and a detached watchdog process relaunches the app if killed. UAC elevation was added to handle hosts-file modifications.

### v3.1 — Modern Dark UI & Enterprise Reliability (Current)

- **Modern Dark Focus Theme**: Complete visual redesign using a modern dark slate canvas (`#0f172a`), elevated cards (`#1e293b`), electric indigo accents (`#6366f1`), and emerald status indicators (`#10b981`).
- **Maximized by Default & High-DPI**: All windows open maximized / full screen by default (`root.state('zoomed')`) with Windows high-DPI scaling enabled (`SetProcessDpiAwareness`) for razor-sharp text and graphics.
- **Hero Dashboard**: Real-time focus session banner, live KPI metrics (Focus Time, Configured Blocks, Resistance), and quick-action cards.
- **Direct Sidebar Navigation**: Modern sidebar with quick links (`Dashboard`, `Manage Blocks`, `Statistics`), live system status pill (`● FOCUS ACTIVE` / `○ SYSTEM IDLE`), and quick hosts cleanup.
- **Automated Hosts Cleanup**: `resume_active()` automatically scrubs orphaned redirects from inactive blocks upon startup.
- **Emergency Unblock Tool**: Standalone `unblock_all.py` script and in-app "Clean Hosts" buttons for instant unblocking and DNS cache flushing.
- **Quality of Life**: Pressing <kbd>Enter</kbd> instantly adds websites to the blacklist or submits unlock passwords.

---

## Features

- **Application Blocking**: Executables are held with OS-level exclusive file locks (`msvcrt`) while active.
- **Website Blocking**: Domains are redirected to localhost (`127.0.0.1` and `::1`) in `C:\Windows\System32\drivers\etc\hosts` in both bare and `www.` forms, tagged with `# ProductivityApp`.
- **Whitelisting**: Per-block domain whitelist excludes specific sites from being blacklisted.
- **Four Lock Modes**:
  - ⏱️ **Countdown Timer**: Blocks for hours:minutes:seconds with a digital focus clock window.
  - 🌙 **Delayed Start**: Waits a duration, then locks until the coming midnight.
  - 📅 **Daily Prohibited Window**: Blocks during recurring daily hours (supports overnight windows like 22:00–06:00).
  - 🔑 **Password Protection**: Locks behind a secret password required to release apps and sites.
- **Workstation Deadlocks**: Strict focus mode that continuously locks the workstation via `rundll32.exe`.
- **Persistence & Crash Recovery**: State persists across restarts; a detached background watchdog restarts the app if killed mid-block.
- **Automated Hosts Cleanup**: Inactive profiles have their hosts entries automatically purged on launch.
- **Productivity Analytics**: Total focus time, per-block session history, and 7-day trend logs backed by `data/events.jsonl`.

---

## Requirements

- **Windows 10 / 11** (uses Windows `msvcrt` file locking, `hosts` driver file, and Win32 UAC elevation).
- **Python 3.8+** with tkinter.
- **Administrator Rights**: Modifying the Windows hosts file requires Administrator privileges. Both `src/main.py` and `src/main_gui.py` self-elevate automatically via Windows UAC.

---

## How to Run

From the project root:

```powershell

# Launch the Modern Dashboard GUI (requests UAC elevation automatically)
python src/main_gui.py

# Launch the Console Menu (requests UAC elevation automatically)
python src/main.py

# Standalone repair tool (instantly unblocks all websites & flushes DNS)
python unblock_all.py
```

---

## How to Use

### 1. Modern GUI (`src/main_gui.py`)

- **Dashboard**:
  - **Hero Status Banner**: Displays whether a focus session is active or idle. When active, shows session name, lock type, and target counts with a direct manage action.
  - **KPI Metrics**: Real-time summary cards for Total Focus Time, Saved Profiles, and Unlock Resistance.
  - **Quick Actions**: Visual cards to create blocks, manage profiles, or view deadlock options.
  - **Sidebar Footer**: Live system status pill (`● FOCUS ACTIVE` or `○ SYSTEM IDLE`) and a `🧹 Clean Hosts` tool.
- **Manage Blocks Page**:
  - Live table showing Profile Name, Lock Mode, Applications, Websites, and Status (`● ACTIVE` vs `○ IDLE`).
  - Toolbar actions: `+ Create Block`, `▶ Start / ⏹ Stop`, `✏️ Edit`, `🗑️ Delete`, `🧹 Clean Hosts`, and `🔄 Refresh`.
- **Analytics & Insights Page**:
  - Summary KPI cards, a 7-day trend table, and per-profile activity history.

### 2. Console Menu (`src/main.py`)

```
Choose a number:
1. Create Block               Opens Create Block window and monitors
2. Edit Block                 Opens Manage Blocks window
3. Create Deadlock            Console submenu (a-d) for workstation lockouts
4. Clean Hosts / Unblock All  Cleans inactive hosts redirects & flushes DNS
5. Exit
```

### 3. Creating a Block

The **Create Focus Block** window opens maximized by default and includes five tabs:

| Tab | Purpose |
| --- | --- |
| 🏷️ **Name** | Profile name (e.g. "Deep Work", "Study"). Required to save. |
| 🌐 **Blacklist** | Domains to block (e.g. `youtube.com`). Press <kbd>Enter</kbd> or click **+ Add**. |
| 🛡️ **Whitelist** | Domains explicitly excluded from hosts-file blocking. |
| 💻 **Apps** | Applications to lock, selected via file picker dialog. |
| 🔒 **Mode** | Choose Countdown Timer, Delay until Midnight, Daily Window, or Password. |

Click **🚀 Save & Start Block** to persist the configuration to `data/data.json` and start the session immediately.

---

## Hosts File Management & Troubleshooting

### Why Websites Stay Blocked After Unlocking

1. **Windows Hosts File**: Website blocking writes redirect entries to `C:\Windows\System32\drivers\etc\hosts`. The app automatically removes these when a session ends or on app launch.
2. **Browser Socket Caching (Important)**: Modern Chromium browsers (Google Chrome, Microsoft Edge, Brave) cache failed TCP connections in an internal socket pool for ~1 minute. Even after the hosts file is restored and DNS is flushed, the browser may still show `ERR_CONNECTION_REFUSED`.
   - **Fix**: Close and reopen your web browser; **OR**
   - In Chrome / Edge, navigate to `chrome://net-internals/#sockets` and click **"Flush socket pools"**.

### Emergency Unblock Utility
If a session was abruptly terminated or you want to force-unblock all websites immediately:

```powershell
python unblock_all.py
```
*(Accept the Windows UAC prompt when asked)*

---

## The `data/` Directory

Created automatically on first launch and ignored by git:

| File | Purpose |
| --- | --- |
| `data.json` | Persistent state: saved blocks, active deadlock, and relaunch entry point. Written atomically. |
| `events.jsonl` | Append-only statistics and event log. |
| `heartbeat.txt` | Timestamp updated every few seconds while any block or deadlock runs. |
| `watchdog.pid` | PID lock file guarding the single detached watchdog instance. |

*To reset the application to a clean slate, delete the `data/` folder.*

---

## Project Structure

```
ProductivityApp/
├── src/
│   ├── main_gui.py          Modern GUI dashboard (Home, Manage Blocks, Analytics)
│   ├── main.py              Console menu with UAC self-elevation
│   ├── create_block_gui.py  Maximized Create/Edit Block dialog with 5 tabs
│   ├── edit_block_gui.py    Manage Blocks table and toolbar
│   ├── block_runner.py      Background engine: start, stop, monitor, resume
│   ├── deadlock.py          Workstation lockouts (persisted & resumable)
│   ├── locking_methods.py   Digital countdown timer and password unlock dialogs
│   ├── website_list.py      Hosts file blocking, unblocking, and dual DNS flushing
│   ├── app_list.py          File pickers and OS-level exclusive file locking
│   ├── storage.py           Persistence layer (data.json, events.jsonl, heartbeat)
│   ├── watchdog.py          Detached background watchdog process
│   └── gui_utils.py         Dark theme styles, DPI awareness, elevation & window helpers
├── unblock_all.py           Standalone repair tool to unblock all sites & flush DNS
├── smoke_test.py            Unit & integration test suite (side-effect free)
├── java_archive/            Original Java sources (v1, preserved for reference)
├── data/                    Runtime persistent state (auto-created, gitignored)
├── README.md                Documentation
└── LICENSE                  MIT License
```

---

## License

MIT — see [LICENSE](LICENSE).
