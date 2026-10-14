"""Create/Edit Block dialog with functional tabs and modern styling.

Moved out of main_gui.py and wired to the persistent storage: the BlackList,
WhiteList and App List tabs collect real lists, the Lock Type tab picks the
kind of block, and Create Block saves it to data/data.json and starts it
immediately (edit mode: an active block is restarted with the new settings).
"""

import tkinter as tk
from tkinter import messagebox, ttk

import block_runner
import storage
from app_list import Applications
from gui_utils import (ACCENT, BG, BORDER, CARD, FONT, FONT_BOLD, FONT_HEADING,
                       TEXT, TEXT_MUTED, apply_style, center_window,
                       maximize_window)
from locking_methods import parse_time


class CreateBlockGUI:
    def __init__(self, edit_block=None):
        self.edit_block = edit_block
        self.black_list = list(edit_block.websites) if edit_block else []
        self.white_list = list(edit_block.whitelist) if edit_block else []
        self.app_list_items = list(edit_block.apps) if edit_block else []

        self.root = tk.Tk()
        self.root.title("Create Focus Block" if edit_block is None else "Edit Focus Block")
        self.root.geometry("820x640")
        self.root.minsize(560, 480)
        apply_style(self.root)
        maximize_window(self.root)  # Full screen / maximized by default
        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)

        # Tabbed interface
        self.tabbed_pane = ttk.Notebook(self.root)
        self.tabbed_pane.add(self._create_name_panel(), text="🏷️ Name")
        self.tabbed_pane.add(self._create_url_panel(
            "Enter websites to blacklist (e.g. youtube.com, reddit.com):",
            self.black_list, 1), text="🌐 Blacklist")
        self.tabbed_pane.add(self._create_url_panel(
            "Whitelisted domains are excluded from blocking:",
            self.white_list, 2), text="🛡️ Whitelist")
        self.tabbed_pane.add(self._create_app_list_panel(), text="💻 Apps")
        self.tabbed_pane.add(self._create_lock_type_panel(), text="🔒 Mode")
        self.tabbed_pane.pack(fill="both", expand=True, padx=8, pady=8)

        center_window(self.root)
        self.root.mainloop()


    # ----- tabs -----

    def _create_name_panel(self):
        panel = ttk.Frame(self.tabbed_pane, padding=20)

        ttk.Label(panel, text="Profile Name", style="Heading.TLabel").pack(fill="x", pady=(0, 4))
        ttk.Label(panel, text="Give your focus block a recognizable name:",
                  style="Muted.TLabel").pack(fill="x", pady=(0, 8))

        self.name_entry = ttk.Entry(panel, font=FONT)
        if self.edit_block is not None:
            self.name_entry.insert(0, self.edit_block.name)
        self.name_entry.pack(fill="x", pady=(0, 8))

        ttk.Label(
            panel,
            text="Tip: Name it after your task, like 'Deep Work', 'Study Session', or 'Writing'.",
            style="Muted.TLabel", wraplength=420).pack(fill="x")

        button_container = ttk.Frame(panel)
        button_container.pack(side="bottom", fill="x", pady=(14, 0))

        cancel_button = ttk.Button(button_container, text="Cancel", style="TButton",
                                   command=self.root.destroy)
        next_button = ttk.Button(button_container, text="Next: Blacklist →", style="Accent.TButton",
                                 command=lambda: self.tabbed_pane.select(1))
        cancel_button.pack(side="left")
        next_button.pack(side="left", padx=(10, 0))

        return panel

    def _create_url_panel(self, label_text, values, next_index):
        panel = ttk.Frame(self.tabbed_pane, padding=20)

        ttk.Label(panel, text="Website URLs", style="Heading.TLabel").pack(fill="x", pady=(0, 2))
        ttk.Label(panel, text=label_text, style="Muted.TLabel", wraplength=420).pack(
            fill="x", pady=(0, 8))

        input_row = ttk.Frame(panel)
        input_row.pack(fill="x", pady=(0, 8))

        entry = ttk.Entry(input_row, font=FONT)
        entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        listbox = tk.Listbox(panel, height=8, bg="#090d16", fg=TEXT, relief="flat",
                             highlightthickness=1, highlightbackground=BORDER,
                             highlightcolor=ACCENT, selectbackground=ACCENT,
                             selectforeground="#ffffff", exportselection=False,
                             font=FONT, bd=0)

        for value in values:
            listbox.insert("end", value)

        def add_url():
            value = entry.get().strip()
            if value and value not in values:
                values.append(value)
                listbox.insert("end", value)
            entry.delete(0, "end")

        entry.bind("<Return>", lambda e: add_url())

        def remove_selected():
            for index in reversed(listbox.curselection()):
                listbox.delete(index)
                del values[index]

        btn_add = ttk.Button(input_row, text="+ Add", style="Accent.TButton", command=add_url)
        btn_add.pack(side="left")

        btn_remove = ttk.Button(panel, text="Remove Selected", style="Danger.TButton",
                                command=remove_selected)
        btn_remove.pack(anchor="w", pady=(0, 8))

        listbox.pack(fill="both", expand=True)

        nav = ttk.Frame(panel)
        nav.pack(side="bottom", fill="x", pady=(14, 0))

        ttk.Button(nav, text="Cancel", style="TButton",
                   command=self.root.destroy).pack(side="left")
        ttk.Button(nav, text="Next →", style="Accent.TButton",
                   command=lambda: self.tabbed_pane.select(next_index + 1)).pack(
                       side="left", padx=(10, 0))

        return panel

    def _create_app_list_panel(self):
        panel = ttk.Frame(self.tabbed_pane, padding=20)

        ttk.Label(panel, text="Executable Applications", style="Heading.TLabel").pack(fill="x", pady=(0, 2))
        ttk.Label(panel, text="Applications to lock while this block is running:",
                  style="Muted.TLabel", wraplength=420).pack(fill="x", pady=(0, 8))

        listbox = tk.Listbox(panel, height=8, bg="#090d16", fg=TEXT, relief="flat",
                             highlightthickness=1, highlightbackground=BORDER,
                             highlightcolor=ACCENT, selectbackground=ACCENT,
                             selectforeground="#ffffff", exportselection=False,
                             font=FONT, bd=0)
        for path in self.app_list_items:
            listbox.insert("end", path)

        def choose_files():
            for path in Applications.pick_files(parent=self.root):
                if path not in self.app_list_items:
                    self.app_list_items.append(path)
                    listbox.insert("end", path)

        def remove_selected():
            for index in reversed(listbox.curselection()):
                listbox.delete(index)
                del self.app_list_items[index]

        buttons = ttk.Frame(panel)
        buttons.pack(fill="x", pady=(0, 8))

        ttk.Button(buttons, text="📁 Choose Files...", style="Accent.TButton",
                   command=choose_files).pack(side="left")
        ttk.Button(buttons, text="Remove Selected", style="Danger.TButton",
                   command=remove_selected).pack(side="left", padx=(8, 0))

        listbox.pack(fill="both", expand=True)

        nav = ttk.Frame(panel)
        nav.pack(side="bottom", fill="x", pady=(14, 0))

        ttk.Button(nav, text="Cancel", style="TButton",
                   command=self.root.destroy).pack(side="left")
        ttk.Button(nav, text="Next: Lock Mode →", style="Accent.TButton",
                   command=lambda: self.tabbed_pane.select(4)).pack(
                       side="left", padx=(10, 0))

        return panel

    def _create_lock_type_panel(self):
        panel = ttk.Frame(self.tabbed_pane, padding=20)

        ttk.Label(panel, text="Lock Mechanism", style="Heading.TLabel").pack(fill="x", pady=(0, 2))
        ttk.Label(panel, text="Choose how this session should be guarded:",
                  style="Muted.TLabel").pack(fill="x", pady=(0, 10))

        self.lock_type = tk.StringVar(
            value=self.edit_block.lock_type if self.edit_block is not None else "timer")

        modes = (
            ("⏱️  Countdown Timer (Hours : Mins : Secs)", "timer"),
            ("🌙  Delay start, then lock until midnight", "after"),
            ("📅  Recurring daily window (Prohibited hours)", "daily"),
            ("🔑  Password protected (Locked until password entered)", "password")
        )
        for label, val in modes:
            ttk.Radiobutton(panel, text=label, value=val,
                            variable=self.lock_type,
                            command=self._update_lock_fields).pack(fill="x", pady=3)

        # Dynamic parameter frames
        params_card = tk.Frame(panel, bg=CARD, padx=14, pady=12,
                               highlightthickness=1, highlightbackground=BORDER)
        params_card.pack(fill="x", pady=(12, 0))

        # timer / after: duration fields
        self.duration_frame = tk.Frame(params_card, bg=CARD)
        tk.Label(self.duration_frame, text="Duration (Hours : Minutes : Seconds)",
                 bg=CARD, fg=TEXT, font=FONT_BOLD).pack(fill="x", pady=(0, 4))
        dur_row = tk.Frame(self.duration_frame, bg=CARD)
        self.hours_entry = ttk.Entry(dur_row, width=6)
        self.minutes_entry = ttk.Entry(dur_row, width=6)
        self.seconds_entry = ttk.Entry(dur_row, width=6)

        self.hours_entry.pack(side="left", padx=(0, 8))
        self.minutes_entry.pack(side="left", padx=(0, 8))
        self.seconds_entry.pack(side="left")
        dur_row.pack(anchor="w")

        # daily: window fields
        self.daily_frame = tk.Frame(params_card, bg=CARD)
        tk.Label(self.daily_frame, text="Prohibited Window (HH:MM to HH:MM)",
                 bg=CARD, fg=TEXT, font=FONT_BOLD).pack(fill="x", pady=(0, 4))
        daily_row = tk.Frame(self.daily_frame, bg=CARD)
        self.daily_start_entry = ttk.Entry(daily_row, width=8)
        self.daily_end_entry = ttk.Entry(daily_row, width=8)
        self.daily_start_entry.pack(side="left", padx=(0, 8))
        tk.Label(daily_row, text="to", bg=CARD, fg=TEXT_MUTED).pack(side="left", padx=(0, 8))
        self.daily_end_entry.pack(side="left")
        daily_row.pack(anchor="w")

        # password: entry + confirm
        self.password_frame = tk.Frame(params_card, bg=CARD)
        tk.Label(self.password_frame, text="Unlock Password",
                 bg=CARD, fg=TEXT, font=FONT_BOLD).pack(fill="x", pady=(0, 2))
        self.password_entry = ttk.Entry(self.password_frame, show="*")
        self.password_entry.pack(fill="x", pady=(0, 6))

        tk.Label(self.password_frame, text="Confirm Password",
                 bg=CARD, fg=TEXT, font=FONT_BOLD).pack(fill="x", pady=(0, 2))
        self.password_confirm_entry = ttk.Entry(self.password_frame, show="*")
        self.password_confirm_entry.pack(fill="x")

        if self.edit_block is not None:
            duration = self.edit_block.duration_seconds or 0
            self.hours_entry.insert(0, str(duration // 3600))
            self.minutes_entry.insert(0, str((duration % 3600) // 60))
            self.seconds_entry.insert(0, str(duration % 60))
            self.daily_start_entry.insert(0, self.edit_block.daily_start)
            self.daily_end_entry.insert(0, self.edit_block.daily_end)
            self.password_entry.insert(0, self.edit_block.password)
            self.password_confirm_entry.insert(0, self.edit_block.password)

        button_container = ttk.Frame(panel)
        button_container.pack(side="bottom", fill="x", pady=(14, 0))

        cancel_button = ttk.Button(button_container, text="Cancel", style="TButton",
                                   command=self.root.destroy)
        save_button = ttk.Button(
            button_container,
            text="Save Changes" if self.edit_block is not None else "🚀 Save & Start Block",
            style="Accent.TButton", command=self._on_create)
        cancel_button.pack(side="left")
        save_button.pack(side="left", padx=(10, 0))

        self._update_lock_fields()
        return panel

    def _update_lock_fields(self):
        kind = self.lock_type.get()
        self.duration_frame.pack_forget()
        self.daily_frame.pack_forget()
        self.password_frame.pack_forget()
        if kind in ("timer", "after"):
            self.duration_frame.pack(fill="x")
        elif kind == "daily":
            self.daily_frame.pack(fill="x")
        else:
            self.password_frame.pack(fill="x")

    # ----- saving -----

    def _on_create(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning(
                "Create Block",
                "Without entering a name, this Block will not be saved.",
                parent=self.root)
            return

        kind = self.lock_type.get()
        duration = 0
        daily_start = daily_end = ""
        password = ""
        if kind in ("timer", "after"):
            try:
                hours = int(self.hours_entry.get() or 0)
                minutes = int(self.minutes_entry.get() or 0)
                seconds = int(self.seconds_entry.get() or 0)
            except ValueError:
                messagebox.showerror("Create Block", "Duration must be numbers.",
                                     parent=self.root)
                return
            duration = hours * 3600 + minutes * 60 + seconds
            if duration <= 0:
                messagebox.showerror("Create Block",
                                     "Enter a duration greater than zero.",
                                     parent=self.root)
                return
        elif kind == "daily":
            daily_start = self.daily_start_entry.get().strip()
            daily_end = self.daily_end_entry.get().strip()
            try:
                parse_time(daily_start)
                parse_time(daily_end)
            except ValueError:
                messagebox.showerror("Create Block",
                                     "Use the time format 'HH:MM' (24-hour).",
                                     parent=self.root)
                return
        else:  # password
            password = self.password_entry.get()
            if not password or password != self.password_confirm_entry.get():
                messagebox.showerror("Create Block",
                                     "Passwords are empty or do not match.",
                                     parent=self.root)
                return

        if self.edit_block is not None:
            block = self.edit_block
            was_active = block.active
        else:
            block = storage.Block(name=name)
            was_active = False

        block.apps = list(self.app_list_items)
        block.websites = list(self.black_list)
        block.whitelist = list(self.white_list)
        block.lock_type = kind
        block.duration_seconds = duration
        block.daily_start = daily_start
        block.daily_end = daily_end
        block.password = password

        if self.edit_block is not None:
            storage.log_event("block_updated", block=block.name)
            if was_active:
                block_runner.stop_block(block.name)
                block_runner.start_block(block)
            else:
                storage.upsert_block(block)
        else:
            storage.log_event("block_created", block=block.name)
            block_runner.start_block(block)

        self.root.destroy()
