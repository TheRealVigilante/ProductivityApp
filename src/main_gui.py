"""Python port of MainGUI.java: the main window and the Create Block dialog
(both still a work in progress, like the originals)."""

import tkinter as tk
from tkinter import ttk

from gui_utils import center_window, exit_application


class MainGUI:
    def __init__(self):
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
        # Handle button click (you can navigate to different pages here)
        if button_text == "Home":
            self._show_page(self._create_home_page())
        elif button_text == "Statistics":
            # Add code to switch to Statistics page
            self._show_page(None)

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

        for button in (create_block_button, create_deadlock_button, edit_blocks_button):
            button.pack(side="left", padx=10, pady=10)
        return home_page

    def _create_home_content_button(self, parent, button_text):
        # roughly a 190x120 button with internal margins, like the original
        return tk.Button(parent, text=button_text, width=22, height=6)

    def _on_create_block(self):
        # Opens on top of this window (the main window waits until it closes)
        CreateBlockGUI()


class CreateBlockGUI:
    def __init__(self):
        self.block_name = None
        self.black_list = []
        self.white_list = []
        self.app_list = []

        self.root = tk.Tk()
        self.root.title("Create Block")
        self.root.geometry("400x390")
        # Close only this window, not the entire application
        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)

        # Create tabs
        self.tabbed_pane = ttk.Notebook(self.root)
        self.name_tab = self._create_name_panel()
        self.black_list_tab = self._create_black_list_panel()
        self.tabbed_pane.add(self.name_tab, text="Name")
        self.tabbed_pane.add(self.black_list_tab, text="BlackList")
        self.tabbed_pane.add(self._create_white_list_panel(), text="WhiteList")
        self.tabbed_pane.add(self._create_app_list_panel(), text="App List")
        self.tabbed_pane.add(self._create_lock_type_panel(), text="Lock Type")
        self.tabbed_pane.pack(fill="both", expand=True)

        center_window(self.root)
        self.root.mainloop()

    def _create_name_panel(self):
        panel = tk.Frame(self.tabbed_pane)

        # Label and text field for entering the block name
        name_label = tk.Label(panel, text="Enter a name for your block:", anchor="w")
        self.name_entry = tk.Entry(panel)
        # Note text
        note_label = tk.Label(
            panel,
            text="Note: Without entering a name, this Block will not be saved.",
            fg="gray", anchor="w", wraplength=350)

        # Button container for Next and Cancel buttons
        button_container = tk.Frame(panel)
        next_button = tk.Button(button_container, text="Next",
                                command=self._on_next_from_name)
        cancel_button = tk.Button(button_container, text="Cancel",
                                  command=self._on_cancel_from_name)
        cancel_button.pack(side="left")
        next_button.pack(side="left")

        name_label.pack(fill="x")
        self.name_entry.pack(fill="x")
        note_label.pack(fill="x")
        tk.Frame(panel, height=35).pack()  # some vertical space
        button_container.pack(anchor="w")
        return panel

    def _on_next_from_name(self):
        # Save the user's input to the block_name variable
        self.block_name = self.name_entry.get()
        # Move to the BlackList tab
        self.tabbed_pane.select(self.black_list_tab)
        print(self.block_name)

    def _on_cancel_from_name(self):
        # Close the window and discard the input
        self.root.destroy()
        self.block_name = None

    def _create_black_list_panel(self):
        panel = tk.Frame(self.tabbed_pane)

        # Label for entering URLs
        enter_url_label = tk.Label(
            panel,
            text="Enter the URLs you would like to blacklist one at a time:",
            anchor="w", wraplength=350)
        # Text field for entering URLs
        self.url_entry = tk.Entry(panel)
        # Button for adding URLs
        add_button = tk.Button(panel, text="Add", command=self._on_add_url)
        # Area to display entered URLs
        self.url_display_area = tk.Text(panel, height=6)

        # Button container for Cancel and Next buttons
        button_container = tk.Frame(panel)
        cancel_button = tk.Button(button_container, text="Cancel",
                                  command=self._on_cancel_black_list)
        next_button = tk.Button(button_container, text="Next",
                                command=self._on_next_black_list)
        cancel_button.pack(side="left")
        next_button.pack(side="left")

        enter_url_label.pack(fill="x")
        self.url_entry.pack(fill="x")
        add_button.pack(anchor="w")
        self.url_display_area.pack(fill="both", expand=True)
        button_container.pack(anchor="w")
        return panel

    def _on_add_url(self):
        # Add the entered URL to the BlackList (the original only prints it)
        url = self.url_entry.get()
        print("Added to BlackList: " + url)
        # Clear the text field for the next input
        self.url_entry.delete(0, "end")

    def _on_cancel_black_list(self):
        # Add code to handle cancel action
        print("Cancel button clicked")

    def _on_next_black_list(self):
        # Add code to handle next action
        print("Next button clicked")

    def _create_white_list_panel(self):
        return tk.Frame(self.tabbed_pane)  # Add components for the "WhiteList" tab

    def _create_app_list_panel(self):
        return tk.Frame(self.tabbed_pane)  # Add components for the "App List" tab

    def _create_lock_type_panel(self):
        return tk.Frame(self.tabbed_pane)  # Add components for the "Lock Type" tab


if __name__ == "__main__":
    MainGUI()
