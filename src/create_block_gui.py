"""Create/Edit Block dialog with functional tabs.

Moved out of main_gui.py and wired to the persistent storage: the BlackList,
WhiteList and App List tabs collect real lists, the Lock Type tab picks the
kind of block, and Create Block saves it to data/data.json and starts it
immediately (edit mode: an active block is restarted with the new settings)."""

import tkinter as tk
from tkinter import messagebox, ttk

import block_runner
import storage
from app_list import Applications
from gui_utils import center_window
from locking_methods import parse_time


class CreateBlockGUI:
    def __init__(self, edit_block=None):
        self.edit_block = edit_block
        self.black_list = list(edit_block.websites) if edit_block else []
        self.white_list = list(edit_block.whitelist) if edit_block else []
        self.app_list_items = list(edit_block.apps) if edit_block else []

        self.root = tk.Tk()
        self.root.title("Create Block" if edit_block is None else "Edit Block")
        self.root.geometry("400x430")
        # Close only this window, not the entire application
        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)

        # Create tabs
        self.tabbed_pane = ttk.Notebook(self.root)
        self.tabbed_pane.add(self._create_name_panel(), text="Name")
        self.tabbed_pane.add(self._create_url_panel(
            "Enter the URLs you would like to blacklist one at a time:",
            self.black_list, 1), text="BlackList")
        self.tabbed_pane.add(self._create_url_panel(
            "Whitelisted sites are never blocked by this block:",
            self.white_list, 2), text="WhiteList")
        self.tabbed_pane.add(self._create_app_list_panel(), text="App List")
        self.tabbed_pane.add(self._create_lock_type_panel(), text="Lock Type")
        self.tabbed_pane.pack(fill="both", expand=True)

        center_window(self.root)
        self.root.mainloop()

    # ----- tabs -----

    def _create_name_panel(self):
        panel = tk.Frame(self.tabbed_pane)

        # Label and text field for entering the block name
        name_label = tk.Label(panel, text="Enter a name for your block:", anchor="w")
        self.name_entry = tk.Entry(panel)
        if self.edit_block is not None:
            self.name_entry.insert(0, self.edit_block.name)
        # Note text
        note_label = tk.Label(
            panel,
            text="Note: Without entering a name, this Block will not be saved.",
            fg="gray", anchor="w", wraplength=350)

        # Button container for Next and Cancel buttons
        button_container = tk.Frame(panel)
        next_button = tk.Button(button_container, text="Next",
                                command=lambda: self.tabbed_pane.select(1))
        cancel_button = tk.Button(button_container, text="Cancel",
                                  command=self.root.destroy)
        cancel_button.pack(side="left")
        next_button.pack(side="left")

        name_label.pack(fill="x")
        self.name_entry.pack(fill="x")
        note_label.pack(fill="x")
        tk.Frame(panel, height=35).pack()  # some vertical space
        button_container.pack(anchor="w")
        return panel

    def _create_url_panel(self, label_text, values, next_index):
        panel = tk.Frame(self.tabbed_pane)

        tk.Label(panel, text=label_text, anchor="w", wraplength=350).pack(fill="x", pady=(4, 2))
        entry = tk.Entry(panel)
        entry.pack(fill="x")

        listbox = tk.Listbox(panel, height=7)
        for value in values:
            listbox.insert("end", value)

        def add_url():
            value = entry.get().strip()
            if value and value not in values:
                values.append(value)
                listbox.insert("end", value)
            entry.delete(0, "end")

        def remove_selected():
            for index in reversed(listbox.curselection()):
                listbox.delete(index)
                del values[index]

        buttons = tk.Frame(panel)
        tk.Button(buttons, text="Add", command=add_url).pack(side="left")
        tk.Button(buttons, text="Remove Selected", command=remove_selected).pack(side="left")
        buttons.pack(fill="x", pady=4)

        listbox.pack(fill="both", expand=True)

        nav = tk.Frame(panel)
        tk.Button(nav, text="Cancel", command=self.root.destroy).pack(side="left")
        tk.Button(nav, text="Next",
                  command=lambda: self.tabbed_pane.select(next_index + 1)).pack(side="left")
        nav.pack(anchor="w", pady=6)
        return panel

    def _create_app_list_panel(self):
        panel = tk.Frame(self.tabbed_pane)

        tk.Label(panel, text="Applications to lock while this block is active:",
                 anchor="w", wraplength=350).pack(fill="x", pady=(4, 2))

        listbox = tk.Listbox(panel, height=7)
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

        buttons = tk.Frame(panel)
        tk.Button(buttons, text="Choose files...", command=choose_files).pack(side="left")
        tk.Button(buttons, text="Remove Selected", command=remove_selected).pack(side="left")
        buttons.pack(fill="x", pady=4)

        listbox.pack(fill="both", expand=True)

        nav = tk.Frame(panel)
        tk.Button(nav, text="Cancel", command=self.root.destroy).pack(side="left")
        tk.Button(nav, text="Next", command=lambda: self.tabbed_pane.select(4)).pack(side="left")
        nav.pack(anchor="w", pady=6)
        return panel

    def _create_lock_type_panel(self):
        panel = tk.Frame(self.tabbed_pane)

        self.lock_type = tk.StringVar(
            value=self.edit_block.lock_type if self.edit_block is not None else "timer")
        for text, value in (("Block for a time", "timer"),
                            ("Block after a delay, until midnight", "after"),
                            ("Set a daily limit", "daily"),
                            ("Set password", "password")):
            tk.Radiobutton(panel, text=text, value=value, variable=self.lock_type,
                          command=self._update_lock_fields, anchor="w").pack(fill="x")

        # timer / after: duration fields
        self.duration_frame = tk.Frame(panel)
        tk.Label(self.duration_frame, text="Hours:Minutes:Seconds", anchor="w").pack(fill="x")
        duration_row = tk.Frame(self.duration_frame)
        self.hours_entry = tk.Entry(duration_row, width=5)
        self.minutes_entry = tk.Entry(duration_row, width=5)
        self.seconds_entry = tk.Entry(duration_row, width=5)
        for entry in (self.hours_entry, self.minutes_entry, self.seconds_entry):
            entry.pack(side="left", padx=(0, 10))
        duration_row.pack(anchor="w")

        # daily: window fields
        self.daily_frame = tk.Frame(panel)
        tk.Label(self.daily_frame, text="Start and end time (hour:minute, 24h)",
                 anchor="w").pack(fill="x")
        daily_row = tk.Frame(self.daily_frame)
        self.daily_start_entry = tk.Entry(daily_row, width=8)
        self.daily_end_entry = tk.Entry(daily_row, width=8)
        self.daily_start_entry.pack(side="left", padx=(0, 10))
        self.daily_end_entry.pack(side="left")
        daily_row.pack(anchor="w")

        # password: entry + confirm
        self.password_frame = tk.Frame(panel)
        tk.Label(self.password_frame, text="Password", anchor="w").pack(fill="x")
        self.password_entry = tk.Entry(self.password_frame, show="*")
        self.password_entry.pack(fill="x")
        tk.Label(self.password_frame, text="Confirm password", anchor="w").pack(fill="x")
        self.password_confirm_entry = tk.Entry(self.password_frame, show="*")
        self.password_confirm_entry.pack(fill="x")

        if self.edit_block is not None:  # prefill
            duration = self.edit_block.duration_seconds or 0
            self.hours_entry.insert(0, str(duration // 3600))
            self.minutes_entry.insert(0, str((duration % 3600) // 60))
            self.seconds_entry.insert(0, str(duration % 60))
            self.daily_start_entry.insert(0, self.edit_block.daily_start)
            self.daily_end_entry.insert(0, self.edit_block.daily_end)
            self.password_entry.insert(0, self.edit_block.password)
            self.password_confirm_entry.insert(0, self.edit_block.password)

        # Button container (Create/Save and Cancel)
        button_container = tk.Frame(panel)
        button_container.pack(side="bottom", fill="x", pady=6)
        cancel_button = tk.Button(button_container, text="Cancel", command=self.root.destroy)
        save_button = tk.Button(
            button_container,
            text="Save Changes" if self.edit_block is not None else "Create Block",
            command=self._on_create)
        cancel_button.pack(side="left")
        save_button.pack(side="left")

        self._update_lock_fields()
        return panel

    def _update_lock_fields(self):
        kind = self.lock_type.get()
        self.duration_frame.pack_forget()
        self.daily_frame.pack_forget()
        self.password_frame.pack_forget()
        if kind in ("timer", "after"):
            self.duration_frame.pack(fill="x", pady=4)
        elif kind == "daily":
            self.daily_frame.pack(fill="x", pady=4)
        else:
            self.password_frame.pack(fill="x", pady=4)

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
                                     "Use the time format 'hour:minute'.",
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
                # restart the engagement with the new settings
                block_runner.stop_block(block.name)
                block_runner.start_block(block)
            else:
                storage.upsert_block(block)
        else:
            storage.log_event("block_created", block=block.name)
            block_runner.start_block(block)  # saves and starts immediately
        self.root.destroy()
