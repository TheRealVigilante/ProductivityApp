"""Python port of MainGUI.java, extended: Home page, Edit Blocks page and a
Statistics page backed by data/events.jsonl. Blocks and deadlocks persisted
in data/data.json are resumed on startup."""

from datetime import datetime

import tkinter as tk
from tkinter import ttk

import block_runner
import storage
from create_block_gui import CreateBlockGUI
from edit_block_gui import build_edit_blocks_ui
from gui_utils import center_window, exit_application


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

        # Set up the main frame
        self.root = tk.Tk()
        self.root.title("Main Page")
        self.root.geometry("960x600")  # considering the padding
        self.root.protocol("WM_DELETE_WINDOW", exit_application)  # EXIT_ON_CLOSE

        # Create and set up the side panel
        self.side_panel = self._create_side_panel()
        self.side_panel.pack(side="left", fill="y")

        # Create and set up the content panel
        self.content_panel = tk.Frame(self.root)
        self.content_panel.pack(side="right", fill="both", expand=True)

        # Initial content (Home page)
        self._show_page(self._create_home_page())

        center_window(self.root)
        self.root.mainloop()

    def _create_side_panel(self):
        panel = tk.Frame(self.root, bg="dark gray", width=250)  # width of 250 pixels
        panel.pack_propagate(False)

        home_button = self._create_side_bar_button(panel, "Home")
        statistics_button = self._create_side_bar_button(panel, "Statistics")

        tk.Frame(panel, bg="dark gray", height=20).pack(fill="x")  # some space at the top
        home_button.pack(fill="x")
        statistics_button.pack(fill="x")
        # the leftover space below acts as the vertical glue at the bottom
        return panel

    def _create_side_bar_button(self, parent, button_text):
        button = tk.Button(parent, text=button_text, fg="white", bg="dark gray",
                           bd=0, anchor="w", padx=8, pady=4,
                           command=lambda: self._on_side_bar_click(button_text))
        return button

    def _on_side_bar_click(self, button_text):
        # Handle button click (navigate to different pages here)
        if button_text == "Home":
            self._show_page(self._create_home_page())
        elif button_text == "Statistics":
            self._show_page(self._create_statistics_page())

    def _show_page(self, page):
        for child in self.content_panel.winfo_children():
            child.destroy()
        if page is not None:
            page.pack(fill="both", expand=True)

    def _create_home_page(self):
        home_page = tk.Frame(self.content_panel)

        create_block_button = self._create_home_content_button(home_page, "Create Block")
        create_deadlock_button = self._create_home_content_button(home_page, "Create Deadlock")
        edit_blocks_button = self._create_home_content_button(home_page, "Edit Blocks")

        # Handle button click (you can create and show the CreateBlockGUI here)
        create_block_button.configure(command=self._on_create_block)
        edit_blocks_button.configure(
            command=lambda: self._show_page(build_edit_blocks_ui(self.content_panel)))
        # Create Deadlock stays console-driven for now (like the original)

        for button in (create_block_button, create_deadlock_button, edit_blocks_button):
            button.pack(side="left", padx=10, pady=10)
        return home_page

    def _create_home_content_button(self, parent, button_text):
        # roughly a 190x120 button with internal margins, like the original
        return tk.Button(parent, text=button_text, width=22, height=6)

    def _on_create_block(self):
        # Opens on top of this window (the main window waits until it closes)
        CreateBlockGUI()

    def _create_statistics_page(self):
        page = tk.Frame(self.content_panel)

        summary = tk.Label(
            page,
            text="Total blocked time: " + _format_duration(storage.total_blocked_seconds())
                 + "    Blocks created: "
                 + str(sum(1 for e in storage.iter_events()
                           if e.get("event") == "block_created"))
                 + "    Failed unlock attempts: " + str(storage.failed_unlock_count()),
            anchor="w")
        summary.pack(fill="x", padx=10, pady=8)

        # last 7 days totals
        tk.Label(page, text="Last 7 days", anchor="w",
                 font=("Arial", 11, "bold")).pack(fill="x", padx=10)
        days_tree = ttk.Treeview(page, columns=("day", "blocked"), show="headings",
                                 height=6)
        days_tree.heading("day", text="Day")
        days_tree.heading("blocked", text="Blocked time")
        days_tree.column("day", width=140, anchor="w")
        days_tree.column("blocked", width=140, anchor="w")
        days_tree.pack(fill="x", padx=10, pady=4)
        for day, seconds in sorted(storage.last_7_days_totals().items(), reverse=True):
            days_tree.insert("", "end", values=(day, _format_duration(seconds)))

        # per-block summary
        tk.Label(page, text="Blocks", anchor="w",
                 font=("Arial", 11, "bold")).pack(fill="x", padx=10)
        blocks_tree = ttk.Treeview(
            page, columns=("name", "starts", "blocked", "last"), show="headings")
        blocks_tree.heading("name", text="Name")
        blocks_tree.heading("starts", text="Starts")
        blocks_tree.heading("blocked", text="Blocked time")
        blocks_tree.heading("last", text="Last ended")
        blocks_tree.column("name", width=200, anchor="w")
        blocks_tree.column("starts", width=70, anchor="w")
        blocks_tree.column("blocked", width=120, anchor="w")
        blocks_tree.column("last", width=160, anchor="w")
        blocks_tree.pack(fill="both", expand=True, padx=10, pady=4)
        for name, entry in sorted(storage.per_block_summary().items()):
            blocks_tree.insert("", "end", values=(
                name, entry["starts"], _format_duration(entry["seconds"]),
                _format_ts(entry["last_ended"])))

        tk.Button(page, text="Refresh",
                  command=lambda: self._show_page(self._create_statistics_page())
                  ).pack(anchor="w", padx=10, pady=6)
        return page


if __name__ == "__main__":
    MainGUI()
