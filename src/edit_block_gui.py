"""Edit Blocks manager: list, edit, delete and start/stop saved blocks.

build_edit_blocks_ui() builds the manager into an existing parent frame (the
MainGUI page); EditBlockGUI is a standalone window wrapper for the console
menu (option 2)."""

import tkinter as tk
from tkinter import messagebox, ttk

import block_runner
import storage
from create_block_gui import CreateBlockGUI
from gui_utils import center_window


def build_edit_blocks_ui(parent):
    """Build the blocks manager into parent; returns the (unpacked) page frame."""
    frame = tk.Frame(parent)

    columns = ("name", "type", "apps", "sites", "status")
    tree = ttk.Treeview(frame, columns=columns, show="headings", height=12)
    headings = {"name": "Name", "type": "Type", "apps": "Apps",
                "sites": "Sites", "status": "Status"}
    widths = {"name": 170, "type": 90, "apps": 60, "sites": 60, "status": 90}
    for col in columns:
        tree.heading(col, text=headings[col])
        tree.column(col, width=widths[col], anchor="w")

    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    tree.pack(side="top", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    def refresh():
        try:
            for item in tree.get_children():
                tree.delete(item)
            for block in storage.get_blocks():
                tree.insert("", "end", iid=block.name, values=(
                    block.name, block.lock_type, len(block.apps),
                    len(block.websites), "Active" if block.active else "Stopped"))
        except tk.TclError:
            return  # the page was closed while an edit dialog was open

    def selected_name():
        selection = tree.selection()
        return selection[0] if selection else None

    def on_edit():
        name = selected_name()
        if name is None:
            messagebox.showinfo("Edit Blocks", "Select a block first.", parent=parent)
            return
        block = storage.get_block(name)
        if block is not None:
            CreateBlockGUI(edit_block=block)  # nested window; blocks until closed
            refresh()

    def on_delete():
        name = selected_name()
        if name is None:
            messagebox.showinfo("Edit Blocks", "Select a block first.", parent=parent)
            return
        if not messagebox.askyesno("Delete Block", "Delete '" + name + "'?",
                                   parent=parent):
            return
        block_runner.stop_block(name)  # release locks first if it was running
        storage.delete_block(name)
        storage.log_event("block_deleted", block=name)
        refresh()

    def on_toggle():
        name = selected_name()
        if name is None:
            messagebox.showinfo("Edit Blocks", "Select a block first.", parent=parent)
            return
        block = storage.get_block(name)
        if block is None:
            return
        if block.active:
            block_runner.stop_block(name)
        else:
            block_runner.start_block(block)
        refresh()

    buttons = tk.Frame(frame)
    tk.Button(buttons, text="Edit", command=on_edit).pack(side="left", padx=4)
    tk.Button(buttons, text="Start/Stop", command=on_toggle).pack(side="left", padx=4)
    tk.Button(buttons, text="Delete", command=on_delete).pack(side="left", padx=4)
    tk.Button(buttons, text="Refresh", command=refresh).pack(side="left", padx=4)
    buttons.pack(side="bottom", fill="x", pady=6)

    refresh()
    return frame


class EditBlockGUI:
    """Standalone window wrapper for the console menu."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Edit Blocks")
        self.root.geometry("640x420")
        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)
        page = build_edit_blocks_ui(self.root)
        page.pack(fill="both", expand=True)
        center_window(self.root)
        self.root.mainloop()
