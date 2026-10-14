"""Modernized MainGUI for the Productivity / Focus Engine.

Features:
- Sleek dark slate dashboard with real-time focus session hero banner
- Direct sidebar navigation (Dashboard, Manage Blocks, Statistics)
- Action cards with rich descriptions, quick metrics, and status badges
- Clean hosts integration and UAC status check
"""

from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

import block_runner
import storage
from create_block_gui import CreateBlockGUI
from edit_block_gui import build_edit_blocks_ui
from gui_utils import (ACCENT, BG, BORDER, CARD, CARD_HOVER, DANGER, FONT,
                       FONT_BOLD, FONT_HEADING, FONT_HERO, FONT_SIDEBAR,
                       FONT_TITLE, SIDEBAR, SIDEBAR_ACTIVE, SIDEBAR_HOVER,
                       SUCCESS, TEXT, TEXT_DIM, TEXT_MUTED, TEXT_ON_DARK,
                       WARNING, apply_style, center_window, exit_application,
                       is_admin, maximize_window, run_as_admin)


def _format_duration(seconds):
    seconds = int(seconds)
    hours, rem = divmod(seconds, 3600)
    minutes, secs = divmod(rem, 60)
    if hours:
        return f"{hours}h {minutes}m"
    if minutes:
        return f"{minutes}m {secs}s"
    return f"{secs}s"


def _format_ts(ts):
    if not ts:
        return "-"
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")


class MainGUI:
    def __init__(self):
        storage.set_entry_point("main_gui.py")
        block_runner.resume_active()

        # Set up the main window
        self.root = tk.Tk()
        self.root.title("Focus Engine — Productivity Suite")
        self.root.geometry("1100x720")
        self.root.minsize(920, 580)
        apply_style(self.root)
        maximize_window(self.root)  # Full screen / maximized by default
        self.root.protocol("WM_DELETE_WINDOW", exit_application)


        # Side navigation panel
        self._sidebar_buttons = {}
        self.side_panel = self._create_side_panel()
        self.side_panel.pack(side="left", fill="y")

        # Content display area
        self.content_panel = tk.Frame(self.root, bg=BG)
        self.content_panel.pack(side="right", fill="both", expand=True)

        # Initial view
        self._show_page(self._create_home_page())
        self._set_active_sidebar("Dashboard")

        center_window(self.root)
        self.root.mainloop()

    # ----- Sidebar Navigation -----

    def _create_side_panel(self):
        panel = tk.Frame(self.root, bg=SIDEBAR, width=240)
        panel.pack_propagate(False)

        # Brand header
        brand_frame = tk.Frame(panel, bg=SIDEBAR, padx=20, pady=22)
        brand_frame.pack(fill="x")

        tk.Label(brand_frame, text="⚡ FOCUS ENGINE", fg="#ffffff", bg=SIDEBAR,
                 font=("Segoe UI", 13, "bold"), anchor="w").pack(fill="x")
        tk.Label(brand_frame, text="Productivity Suite v3.1", fg=TEXT_DIM, bg=SIDEBAR,
                 font=("Segoe UI", 9), anchor="w").pack(fill="x", pady=(2, 0))

        # Divider
        tk.Frame(panel, bg=BORDER, height=1).pack(fill="x", padx=16, pady=(0, 14))

        # Nav buttons
        nav_items = (
            ("Dashboard", "🏠  Dashboard"),
            ("Manage Blocks", "📋  Manage Blocks"),
            ("Statistics", "📊  Statistics"),
        )
        for key, display_text in nav_items:
            btn = tk.Button(panel, text=display_text, fg=TEXT_MUTED, bg=SIDEBAR,
                            activebackground=SIDEBAR_HOVER,
                            activeforeground="#ffffff", bd=0, anchor="w",
                            padx=18, pady=10, font=FONT_SIDEBAR,
                            cursor="hand2",
                            command=lambda k=key: self._on_side_bar_click(k))
            btn.bind("<Enter>", lambda e, b=btn: self._sidebar_hover(b, True))
            btn.bind("<Leave>", lambda e, b=btn: self._sidebar_hover(b, False))
            self._sidebar_buttons[key] = btn
            btn.pack(fill="x", padx=12, pady=2)

        # Bottom System Status Widget
        footer_frame = tk.Frame(panel, bg="#0d1424", padx=14, pady=14,
                                highlightthickness=1, highlightbackground=BORDER)
        footer_frame.pack(side="bottom", fill="x", padx=12, pady=16)

        active_blocks = [b for b in storage.get_blocks() if b.active]
        is_active = len(active_blocks) > 0 or bool(
            storage.get_deadlock() and storage.get_deadlock().get("active"))

        status_dot = "●" if is_active else "○"
        status_color = SUCCESS if is_active else TEXT_DIM
        status_text = "FOCUS ACTIVE" if is_active else "SYSTEM IDLE"

        tk.Label(footer_frame, text=f"{status_dot}  {status_text}",
                 fg=status_color, bg="#0d1424",
                 font=("Segoe UI", 9, "bold"), anchor="w").pack(fill="x")

        status_sub = f"{len(active_blocks)} block(s) running" if is_active else "Ready to focus"
        tk.Label(footer_frame, text=status_sub, fg=TEXT_MUTED, bg="#0d1424",
                 font=("Segoe UI", 8), anchor="w").pack(fill="x", pady=(2, 8))

        clean_btn = tk.Button(footer_frame, text="🧹 Clean Hosts", fg=TEXT_MUTED,
                              bg=CARD, activebackground=CARD_HOVER,
                              activeforeground="#ffffff", bd=0, padx=8, pady=4,
                              font=("Segoe UI", 8, "bold"), cursor="hand2",
                              command=self._on_clean_hosts_quick)
        clean_btn.pack(fill="x")

        return panel

    def _sidebar_hover(self, button, entered):
        if button["bg"] != SIDEBAR_ACTIVE:
            button.config(bg=SIDEBAR_HOVER if entered else SIDEBAR,
                          fg="#ffffff" if entered else TEXT_MUTED)

    def _set_active_sidebar(self, active_key):
        for key, button in self._sidebar_buttons.items():
            if key == active_key:
                button.config(bg=SIDEBAR_ACTIVE, fg="#ffffff")
            else:
                button.config(bg=SIDEBAR, fg=TEXT_MUTED)

    def _on_side_bar_click(self, key):
        self._set_active_sidebar(key)
        if key == "Dashboard":
            self._show_page(self._create_home_page())
        elif key == "Manage Blocks":
            self._show_page(build_edit_blocks_ui(self.content_panel))
        elif key == "Statistics":
            self._show_page(self._create_statistics_page())

    def _show_page(self, page):
        for child in self.content_panel.winfo_children():
            child.destroy()
        if page is not None:
            page.pack(fill="both", expand=True)

    def _on_clean_hosts_quick(self):
        from website_list import BlacklistGUI
        active_sites = set()
        for b in storage.get_blocks():
            if b.active:
                active_sites.update(b.websites)
            else:
                for site in b.websites:
                    try:
                        BlacklistGUI.unblock_website(site)
                    except Exception:
                        pass
        try:
            BlacklistGUI.clean_unblocked_hosts(active_sites)
        except Exception:
            pass
        messagebox.showinfo(
            "Clean Hosts",
            "Leftover website redirects removed and Windows DNS cache flushed.\n\n"
            "If your browser still shows 'Connection Refused', close and reopen your browser.",
            parent=self.root)

    # ----- Dashboard (Home Page) -----

    def _create_home_page(self):
        page = ttk.Frame(self.content_panel, padding=(32, 28))

        # Top Header
        header_frame = ttk.Frame(page)
        header_frame.pack(fill="x", pady=(0, 20))

        ttk.Label(header_frame, text="Dashboard", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            header_frame,
            text="Control your focus sessions, block distracting apps and websites, and eliminate procrastination.",
            style="Muted.TLabel").pack(anchor="w", pady=(3, 0))

        # Admin status banner if not elevated
        if not is_admin():
            warn_card = tk.Frame(page, bg="#2d1a04", padx=16, pady=12,
                                 highlightthickness=1, highlightbackground=WARNING)
            warn_card.pack(fill="x", pady=(0, 20))
            tk.Label(warn_card,
                     text="⚠️ Administrator rights needed for website blocking.",
                     bg="#2d1a04", fg="#fde68a", font=FONT_BOLD).pack(anchor="w")
            tk.Label(warn_card,
                     text="Run this application as Administrator so it can update the Windows hosts file.",
                     bg="#2d1a04", fg="#fef3c7", font=("Segoe UI", 9)).pack(anchor="w", pady=(2, 0))

        # Hero Focus Status Banner
        active_blocks = [b for b in storage.get_blocks() if b.active]
        hero_card = tk.Frame(page, bg=CARD, padx=22, pady=18,
                             highlightthickness=1,
                             highlightbackground=ACCENT if active_blocks else BORDER)
        hero_card.pack(fill="x", pady=(0, 22))

        hero_left = tk.Frame(hero_card, bg=CARD)
        hero_left.pack(side="left", fill="both", expand=True)

        if active_blocks:
            active_names = ", ".join(b.name for b in active_blocks)
            tk.Label(hero_left, text="🔥 FOCUS MODE ACTIVE",
                     bg=CARD, fg=SUCCESS, font=("Segoe UI", 11, "bold")).pack(anchor="w")
            tk.Label(hero_left, text=f"Currently blocking for: {active_names}",
                     bg=CARD, fg="#ffffff", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(4, 2))
            total_apps = sum(len(b.apps) for b in active_blocks)
            total_sites = sum(len(b.websites) for b in active_blocks)
            tk.Label(hero_left,
                     text=f"{total_apps} application(s) locked • {total_sites} website(s) blacklisted",
                     bg=CARD, fg=TEXT_MUTED, font=FONT).pack(anchor="w")

            btn_manage = ttk.Button(hero_card, text="Manage Active Blocks", style="Accent.TButton",
                                    command=lambda: self._on_side_bar_click("Manage Blocks"))
            btn_manage.pack(side="right", padx=(16, 0))
        else:
            tk.Label(hero_left, text="⚡ SYSTEM IDLE • READY TO FOCUS",
                     bg=CARD, fg=TEXT_MUTED, font=("Segoe UI", 10, "bold")).pack(anchor="w")
            tk.Label(hero_left, text="Start a new focus session",
                     bg=CARD, fg="#ffffff", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(4, 2))
            tk.Label(hero_left,
                     text="Lock out social media and distracting software with timer or password protection.",
                     bg=CARD, fg=TEXT_MUTED, font=FONT).pack(anchor="w")

            btn_start = ttk.Button(hero_card, text="+ New Focus Block", style="Accent.TButton",
                                   command=self._on_create_block)
            btn_start.pack(side="right", padx=(16, 0))

        # Metric KPI Cards Row
        metrics_frame = ttk.Frame(page)
        metrics_frame.pack(fill="x", pady=(0, 22))

        kpis = (
            ("⏱️ Total Focus Time", _format_duration(storage.total_blocked_seconds()),
             "Across all completed blocks"),
            ("🎯 Blocks Saved", str(len(storage.get_blocks())),
             "Configured focus profiles"),
            ("🛡️ Unlock Resistance", str(storage.failed_unlock_count()),
             "Failed unlock attempts prevented"),
        )
        for idx, (title, value, sub) in enumerate(kpis):
            kpi_card = tk.Frame(metrics_frame, bg=CARD, padx=16, pady=14,
                                highlightthickness=1, highlightbackground=BORDER)
            kpi_card.pack(side="left", fill="both", expand=True,
                          padx=(0 if idx == 0 else 14, 0))

            tk.Label(kpi_card, text=title, bg=CARD, fg=TEXT_MUTED,
                     font=("Segoe UI", 9, "bold")).pack(anchor="w")
            tk.Label(kpi_card, text=value, bg=CARD, fg="#ffffff",
                     font=("Segoe UI", 18, "bold")).pack(anchor="w", pady=(4, 2))
            tk.Label(kpi_card, text=sub, bg=CARD, fg=TEXT_DIM,
                     font=("Segoe UI", 8)).pack(anchor="w")

        # Action Cards Section
        ttk.Label(page, text="Quick Actions", style="Heading.TLabel").pack(anchor="w", pady=(0, 10))

        actions_frame = ttk.Frame(page)
        actions_frame.pack(fill="x")

        # Action 1: Create Block
        self._create_action_card(
            actions_frame,
            icon="🛡️",
            title="Create Block",
            desc="Configure a new block with blacklists, whitelists, app locks, and timer or password locks.",
            btn_text="Create Block",
            btn_style="Accent.TButton",
            command=self._on_create_block,
            side_pad=(0, 14)
        )

        # Action 2: Manage Blocks
        self._create_action_card(
            actions_frame,
            icon="📋",
            title="Manage Blocks",
            desc="Start or stop existing blocks, edit targets, delete old profiles, or clean hosts entries.",
            btn_text="Manage Blocks",
            btn_style="TButton",
            command=lambda: self._on_side_bar_click("Manage Blocks"),
            side_pad=(0, 14)
        )

        # Action 3: Deadlock
        self._create_action_card(
            actions_frame,
            icon="🔒",
            title="Deadlock Engine",
            desc="Strict focus mode that locks your workstation continuously. Trigger from terminal (main.py).",
            btn_text="Console Option",
            btn_style="TButton",
            command=lambda: messagebox.showinfo(
                "Deadlocks",
                "Deadlocks lock the entire Windows workstation every second.\n\n"
                "To run a deadlock, launch 'python src/main.py' and choose option 3.",
                parent=self.root),
            side_pad=(0, 0)
        )

        return page

    def _create_action_card(self, parent, icon, title, desc, btn_text, btn_style, command, side_pad):
        card = tk.Frame(parent, bg=CARD, padx=18, pady=16,
                        highlightthickness=1, highlightbackground=BORDER)
        card.pack(side="left", fill="both", expand=True, padx=side_pad)

        tk.Label(card, text=f"{icon}  {title}", bg=CARD, fg="#ffffff",
                 font=FONT_HEADING).pack(anchor="w")
        tk.Label(card, text=desc, bg=CARD, fg=TEXT_MUTED, wraplength=220,
                 justify="left", font=("Segoe UI", 9)).pack(anchor="w", pady=(6, 16))

        btn = ttk.Button(card, text=btn_text, style=btn_style, command=command)
        btn.pack(anchor="w")

    def _on_create_block(self):
        CreateBlockGUI()
        # Refresh current page to reflect new block if created
        self._show_page(self._create_home_page())

    # ----- Statistics Page -----

    def _create_statistics_page(self):
        page = ttk.Frame(self.content_panel, padding=(32, 28))

        # Header
        header_frame = ttk.Frame(page)
        header_frame.pack(fill="x", pady=(0, 18))

        ttk.Label(header_frame, text="Analytics & Insights", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            header_frame,
            text="Track your productivity trends, blocked time totals, and unlock resistance.",
            style="Muted.TLabel").pack(anchor="w", pady=(3, 0))

        # KPI Summary Card
        card = tk.Frame(page, bg=CARD, padx=20, pady=16,
                        highlightthickness=1, highlightbackground=BORDER)
        card.pack(fill="x", pady=(0, 20))

        metrics = (
            ("Total Focus Time", _format_duration(storage.total_blocked_seconds())),
            ("Blocks Created", str(sum(1 for e in storage.iter_events()
                                       if e.get("event") == "block_created"))),
            ("Failed Unlocks", str(storage.failed_unlock_count())),
        )
        for column, (label_text, value) in enumerate(metrics):
            kpi_box = tk.Frame(card, bg=CARD)
            kpi_box.grid(row=0, column=column, sticky="w", padx=(0, 54))
            tk.Label(kpi_box, text=label_text, bg=CARD, fg=TEXT_MUTED,
                     font=("Segoe UI", 9, "bold")).pack(anchor="w")
            tk.Label(kpi_box, text=value, bg=CARD, fg="#ffffff",
                     font=("Segoe UI", 18, "bold")).pack(anchor="w", pady=(2, 0))

        # Last 7 Days Treeview
        ttk.Label(page, text="Last 7 Days Activity", style="Heading.TLabel").pack(anchor="w", pady=(0, 6))
        days_tree = ttk.Treeview(page, columns=("day", "blocked"),
                                 show="headings", height=5)
        days_tree.heading("day", text="Day")
        days_tree.heading("blocked", text="Blocked Duration")
        days_tree.column("day", width=180, anchor="w")
        days_tree.column("blocked", width=180, anchor="w")
        days_tree.pack(fill="x", pady=(0, 18))

        for day, seconds in sorted(storage.last_7_days_totals().items(), reverse=True):
            days_tree.insert("", "end", values=(day, _format_duration(seconds)))

        # Per-Block Summary Treeview
        ttk.Label(page, text="All Profiles Summary", style="Heading.TLabel").pack(anchor="w", pady=(0, 6))
        blocks_tree = ttk.Treeview(
            page, columns=("name", "starts", "blocked", "last"), show="headings", height=6)
        blocks_tree.heading("name", text="Profile Name")
        blocks_tree.heading("starts", text="Sessions")
        blocks_tree.heading("blocked", text="Total Time")
        blocks_tree.heading("last", text="Last Active")
        blocks_tree.column("name", width=220, anchor="w")
        blocks_tree.column("starts", width=90, anchor="w")
        blocks_tree.column("blocked", width=140, anchor="w")
        blocks_tree.column("last", width=180, anchor="w")
        blocks_tree.pack(fill="both", expand=True, pady=(0, 16))

        for name, entry in sorted(storage.per_block_summary().items()):
            blocks_tree.insert("", "end", values=(
                name, entry["starts"], _format_duration(entry["seconds"]),
                _format_ts(entry["last_ended"])))

        ttk.Button(page, text="🔄 Refresh Statistics", style="TButton",
                   command=lambda: self._show_page(
                       self._create_statistics_page())).pack(anchor="w")
        return page


if __name__ == "__main__":
    import sys
    try:
        if not is_admin():
            print("Requesting administrator access...")
            if run_as_admin():
                sys.exit(0)
            print("Administrator access was refused; website blocking may not work.")
    except Exception:
        pass
    MainGUI()
