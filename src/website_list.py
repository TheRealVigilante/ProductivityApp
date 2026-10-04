"""Python port of WebsiteList.java.

WebsiteList is a named list of websites; BlacklistGUI shows the window where
the user enters the sites, and writes/removes entries in the Windows hosts
file to block/unblock them.
"""

import threading
import tkinter as tk
from tkinter import scrolledtext

from gui_utils import exit_application


class WebsiteList:
    def __init__(self, name):
        self.name = name
        self.websites = []
        self.applications = []  # kept for parity with the Java original (unused)

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def get_websites(self):
        return self.websites

    def add_website(self, website):
        self.websites.append(website)


class BlacklistGUI:
    # list name -> WebsiteList (static state in the Java original)
    website_lists = {}
    hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
    # hosts_path = "fakehost.txt"

    def __init__(self):
        self.current_list_name = None
        self.root = None
        self.websites_text = None
        self._submitted = threading.Event()
        self._thread = None

    # ----- hosts file helpers (static in the Java original) -----

    @staticmethod
    def format(website):  # www.youtube.com or https://youtube.com or https://www.youtube.com
        http = "https://"
        www = "www."
        if http in website:
            website = website[8:]
        if www not in website:
            website = www + website
        return website

    @staticmethod
    def block_website(website):
        redirect_ip = "127.0.0.1"
        try:
            with open(BlacklistGUI.hosts_path, "a") as writer:
                writer.write("\n" + redirect_ip + " " + website + "\n")
        except OSError as e:
            print("Error writing to the hosts file: " + str(e))

    @staticmethod
    def unblock_website(url):
        with open(BlacklistGUI.hosts_path) as reader:
            lines = [line.rstrip("\r\n") for line in reader]
        with open(BlacklistGUI.hosts_path, "w") as writer:
            for line in lines:
                if url not in line:  # keep every line that does not mention the url
                    writer.write(line + "\n")

    @classmethod
    def lock_websites(cls, list_name):
        website_list = cls.website_lists.get(list_name)
        if website_list is not None:
            for website in website_list.get_websites():
                website = cls.format(website)
                print("Locking: " + website)
                cls.block_website(website)

    @classmethod
    def unlock_websites(cls, list_name):
        website_list = cls.website_lists.get(list_name)
        if website_list is not None:
            for website in website_list.get_websites():
                print("Unlocking: " + website)
                cls.unblock_website(website)

    # ----- GUI -----

    def launch_gui(self, list_name):
        self.current_list_name = list_name
        self._thread = threading.Thread(target=self._create_blacklist, daemon=True)
        self._thread.start()

    def _create_blacklist(self):
        self.root = tk.Tk()
        self.root.title("Website Blacklist")
        self.root.geometry("300x200")
        self.root.protocol("WM_DELETE_WINDOW", exit_application)  # EXIT_ON_CLOSE

        self.websites_text = scrolledtext.ScrolledText(self.root, width=20, height=10)
        self.websites_text.pack(fill="both", expand=True)

        submit_button = tk.Button(self.root, text="Submit", command=self._on_submit)
        submit_button.pack(side="bottom", fill="x")

        self.root.mainloop()

    def _on_submit(self):
        text = self.websites_text.get("1.0", "end-1c")
        websites = [website.strip() for website in text.split("\n")]
        self._on_websites_list_ready(websites)
        self.root.destroy()
        self._submitted.set()  # Notify the waiting thread

    def _on_websites_list_ready(self, websites):
        # Process the websitesList here or notify the caller
        print("Blacklist: " + str(websites))
        website_list = WebsiteList(self.current_list_name)
        for website in websites:
            website_list.add_website(website)
        BlacklistGUI.website_lists[self.current_list_name] = website_list

    def wait_for_submit(self):
        self._submitted.wait()  # Wait until the button is clicked
