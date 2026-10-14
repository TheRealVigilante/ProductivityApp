"""Manage Blocks UI: list, edit, delete, toggle, and clean hosts for saved blocks.

build_edit_blocks_ui() embeds into MainGUI; EditBlockGUI is a standalone wrapper.
"""

import tkinter as tk
from tkinter import messagebox, ttk

import block_runner
import storage
from create_block_gui import CreateBlockGUI
from gui_utils import (ACCENT, BG, BORDER, CARD, CARD_HOVER, DANGER, FONT,
                       FONT_BOLD, FONT_HEADING, FONT_TITLE, SUCCESS, TEXT,
                       TEXT_MUTED, apply_style, center_window, maximize_window)


def build_edit_blocks_ui(parent):
    """Build the modern blocks manager into parent frame."""
    frame = ttk.Frame(parent, padding=(32, 28))

    # Header
    header_frame = ttk.Frame(frame)
    header_frame.pack(fill="x", pady=(0, 16))

    ttk.Label(header_frame, text="Manage Focus Blocks", style="Title.TLabel").pack(anchor="w")
    ttk.Label(
        header_frame,
        text="View your saved focus profiles, toggle blocking sessions, or edit blacklists.",
        style="Muted.TLabel").pack(anchor="w", pady=(3, 0))

    # Table container
    tree_frame = tk.Frame(frame, bg=CARD, highlightthickness=1, highlightbackground=BORDER)
    tree_frame.pack(fill="both", expand=True, pady=(0, 16))

    columns = ("name", "type", "apps", "sites", "status")
    tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=12)
    headings = {
        "name": "Profile Name",
        "type": "Lock Mode",
        "apps": "Applications",
        "sites": "Websites",
        "status": "Current Status"
    }
    widths = {"name": 220, "type": 130, "apps": 110, "sites": 110, "status": 130}
    for col in columns:
        tree.heading(col, text=headings[col])
        tree.column(col, width=widths[col], anchor="w")

    scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Empty state indicator
    empty_label = tk.Label(tree_frame, text="No focus profiles configured yet.\nClick '+ Create Block' below to add one.",
                           bg=CARD, fg=TEXT_MUTED, font=FONT_HEADING, justify="center")

    def refresh():
        try:
            for item in tree.get_children():
                tree.delete(item)
            blocks = storage.get_blocks()
            if not blocks:
                empty_label.place(relx=0.5, rely=0.5, anchor="center")
            else:
                empty_label.place_forget()
                for block in blocks:
                    status_text = "● ACTIVE" if block.active else "○ IDLE"
                    mode_display = {
                        "timer": "⏱️ Timer",
                        "after": "🌙 After / Midnight",
                        "daily": "📅 Daily Window",
                        "password": "🔑 Password"
                    }.get(block.lock_type, block.lock_type.capitalize())

                    tree.insert("", "end", iid=block.name, values=(
                        block.name,
                        mode_display,
                        f"{len(block.apps)} file(s)",
                        f"{len(block.websites)} site(s)",
                        status_text
                    ))
        except tk.TclError:
            return

    def selected_name():
        selection = tree.selection()
        return selection[0] if selection else None

    def on_create():
        CreateBlockGUI()
        refresh()

    def on_edit():
        name = selected_name()
        if name is None:
            messagebox.showinfo("Manage Blocks", "Select a profile from the table to edit.", parent=parent)
            return
        block = storage.get_block(name)
        if block is not None:
            CreateBlockGUI(edit_block=block)
            refresh()

    def on_delete():
        name = selected_name()
        if name is None:
            messagebox.showinfo("Manage Blocks", "Select a profile from the table to delete.", parent=parent)
            return
        if not messagebox.askyesno("Delete Profile", f"Are you sure you want to delete profile '{name}'?",
                                   parent=parent):
            return
        block_runner.stop_block(name)
        storage.delete_block(name)
        storage.log_event("block_deleted", block=name)
        refresh()

    def on_toggle():
        name = selected_name()
        if name is None:
            messagebox.showinfo("Manage Blocks", "Select a profile to start or stop.", parent=parent)
            return
        block = storage.get_block(name)
        if block is None:
            return
        if block.active:
            block_runner.stop_block(name)
        else:
            block_runner.start_block(block)
        refresh()

    def on_clean_hosts():
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
            "Unblocked inactive websites and flushed Windows DNS resolver cache.\n\n"
            "Tip: If your browser still shows a block page, close and reopen your browser.",
            parent=parent)
        refresh()

    # Toolbar buttons
    buttons_frame = ttk.Frame(frame)
    buttons_frame.pack(fill="x")

    ttk.Button(buttons_frame, text="+ Create Block", style="Accent.TButton",
               command=on_create).pack(side="left")
    ttk.Button(buttons_frame, text="▶ Start / ⏹ Stop", style="TButton",
               command=on_toggle).pack(side="left", padx=(10, 0))
    ttk.Button(buttons_frame, text="✏️ Edit", style="TButton",
               command=on_edit).pack(side="left", padx=(8, 0))
    ttk.Button(buttons_frame, text="🗑️ Delete", style="Danger.TButton",
               command=on_delete).pack(side="left", padx=(8, 0))

    # Right-aligned utility buttons
    ttk.Button(buttons_frame, text="🔄 Refresh", style="TButton",
               command=refresh).pack(side="right")
    ttk.Button(buttons_frame, text="🧹 Clean Hosts", style="TButton",
               command=on_clean_hosts).pack(side="right", padx=(0, 8))

    refresh()
    return frame


class EditBlockGUI:
    """Standalone window wrapper for the console menu."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Manage Focus Blocks")
        self.root.geometry("960x640")
        self.root.minsize(700, 480)
        apply_style(self.root)
        maximize_window(self.root)  # Full screen / maximized by default
        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)
        page = build_edit_blocks_ui(self.root)
        page.pack(fill="both", expand=True)
        center_window(self.root)
        self.root.mainloop()
