"""Small helpers shared by the tkinter GUIs, plus the shared flat theme."""

import os
import tkinter as tk
from tkinter import ttk

# ----- Modern Dark Focus Theme -----

BG = "#0f172a"             # Deep slate canvas
BG_SIDEBAR = "#090d16"     # Deeper sidebar surface
CARD = "#1e293b"           # Elevated card surface
CARD_HOVER = "#27354f"     # Hovered card
BORDER = "#334155"         # Subtle slate border
BORDER_LIGHT = "#475569"   # Highlight border
ACCENT = "#6366f1"         # Electric indigo / violet
ACCENT_HOVER = "#4f46e5"
ACCENT_DISABLED = "#312e81"
DANGER = "#f43f5e"         # Modern coral rose
DANGER_HOVER = "#e11d48"
SUCCESS = "#10b981"        # Emerald focus
SUCCESS_HOVER = "#059669"
WARNING = "#f59e0b"        # Amber
CYAN = "#06b6d4"           # Cyan highlight
SIDEBAR = BG_SIDEBAR
SIDEBAR_HOVER = "#1e293b"
SIDEBAR_ACTIVE = "#6366f1"
TEXT = "#f8fafc"           # Bright slate white
TEXT_MUTED = "#94a3b8"     # Soft slate
TEXT_DIM = "#64748b"       # Muted slate
TEXT_ON_DARK = "#f1f5f9"

FONT = ("Segoe UI", 10)
FONT_BOLD = ("Segoe UI", 10, "bold")
FONT_TITLE = ("Segoe UI", 20, "bold")
FONT_HEADING = ("Segoe UI", 13, "bold")
FONT_HERO = ("Segoe UI", 24, "bold")
FONT_SIDEBAR = ("Segoe UI", 10, "bold")
FONT_BADGE = ("Segoe UI", 8, "bold")
FONT_CODE = ("Consolas", 10)


def apply_style(root):
    """Apply the modern dark focus theme; call once per Tk root."""
    enable_high_dpi()
    root.configure(bg=BG)
    style = ttk.Style(root)

    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure(".", background=BG, foreground=TEXT, font=FONT)
    style.configure("TFrame", background=BG)
    style.configure("Card.TFrame", background=CARD)
    style.configure("Sidebar.TFrame", background=BG_SIDEBAR)

    # Standard / Card Button
    style.configure("TButton", background=CARD, foreground=TEXT, borderwidth=1,
                    bordercolor=BORDER, focusthickness=0, padding=(12, 7), font=FONT)
    style.map("TButton",
              background=[("active", BORDER), ("pressed", CARD_HOVER)],
              bordercolor=[("active", BORDER_LIGHT)])

    # Primary Action (Accent) Button
    style.configure("Accent.TButton", background=ACCENT, foreground="#ffffff",
                    borderwidth=0, focusthickness=0, padding=(16, 9),
                    font=FONT_BOLD)
    style.map("Accent.TButton",
              background=[("disabled", ACCENT_DISABLED),
                          ("active", ACCENT_HOVER)],
              foreground=[("disabled", "#a5b4fc")])

    # Success Button (e.g. Start block, unblock)
    style.configure("Success.TButton", background=SUCCESS, foreground="#ffffff",
                    borderwidth=0, focusthickness=0, padding=(14, 8),
                    font=FONT_BOLD)
    style.map("Success.TButton", background=[("active", SUCCESS_HOVER)])

    # Danger Button
    style.configure("Danger.TButton", background=DANGER, foreground="#ffffff",
                    borderwidth=0, focusthickness=0, padding=(12, 7),
                    font=FONT_BOLD)
    style.map("Danger.TButton", background=[("active", DANGER_HOVER)])

    # Entry fields
    style.configure("TEntry", fieldbackground="#090d16", bordercolor=BORDER,
                    insertcolor=TEXT, foreground=TEXT, padding=7)
    style.map("TEntry", bordercolor=[("focus", ACCENT)])

    # Radio buttons
    style.configure("TRadiobutton", background=BG, foreground=TEXT, padding=5, font=FONT)
    style.map("TRadiobutton",
              background=[("active", BG)], foreground=[("active", TEXT)])

    # Labels
    style.configure("TLabel", background=BG, foreground=TEXT)
    style.configure("Muted.TLabel", background=BG, foreground=TEXT_MUTED)
    style.configure("Title.TLabel", font=FONT_TITLE, foreground=TEXT, background=BG)
    style.configure("Heading.TLabel", font=FONT_HEADING, foreground=TEXT, background=BG)
    style.configure("Card.TLabel", background=CARD, foreground=TEXT)
    style.configure("CardHeading.TLabel", background=CARD, foreground=TEXT, font=FONT_HEADING)
    style.configure("CardMuted.TLabel", background=CARD, foreground=TEXT_MUTED, font=("Segoe UI", 9))
    style.configure("CardValue.TLabel", background=CARD, foreground=TEXT,
                    font=("Segoe UI", 20, "bold"))
    style.configure("Badge.TLabel", background="#312e81", foreground="#c7d2fe",
                    font=FONT_BADGE, padding=(6, 2))

    # Notebook & Tabs
    style.configure("TNotebook", background=BG, borderwidth=0,
                    tabmargins=(4, 4, 4, 0))
    style.configure("TNotebook.Tab", background=BG_SIDEBAR, foreground=TEXT_MUTED,
                    padding=(10, 6), font=FONT_BOLD, borderwidth=0)
    style.map("TNotebook.Tab",
              background=[("selected", CARD), ("active", "#162033")],
              foreground=[("selected", "#ffffff"), ("active", TEXT)])

    # Treeview
    style.configure("Treeview", background=CARD, fieldbackground=CARD,
                    foreground=TEXT, rowheight=32, borderwidth=0, font=FONT)
    style.configure("Treeview.Heading", font=FONT_BOLD, padding=(10, 8),
                    background=BG_SIDEBAR, foreground=TEXT_MUTED, borderwidth=0)
    style.map("Treeview",
              background=[("selected", ACCENT)],
              foreground=[("selected", "#ffffff")])


def enable_high_dpi():
    """Enable high-DPI scaling on Windows so text and windows render razor sharp."""
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            import ctypes
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


def maximize_window(root):
    """Maximize the window to full screen by default on Windows."""
    try:
        root.state("zoomed")
    except Exception:
        try:
            root.attributes("-zoomed", True)
        except Exception:
            pass


def is_admin():
    """True when the process already runs with administrator rights."""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except (AttributeError, OSError):
        return True


def run_as_admin():
    """Relaunch the current script elevated (shows the Windows UAC prompt)."""
    import ctypes
    import sys
    script = os.path.abspath(sys.argv[0])
    try:
        return ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, f'"{script}"', None, 1) > 32
    except (AttributeError, OSError):
        return False


def exit_application():
    """Cleanly exit the application."""
    import sys
    sys.exit(0)


def center_window(root):
    # Mirrors frame.setLocationRelativeTo(null): center the window on screen.
    root.eval("tk::PlaceWindow . center")


