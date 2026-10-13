"""Python port of WebsiteList.java, with hardened hosts-file blocking.

WebsiteList is a named list of websites; BlacklistGUI shows the window where
the user enters the sites, and writes/removes entries in the Windows hosts
file to block/unblock them.

Blocking redirects both the bare and the "www." form of a site, over IPv4
(127.0.0.1) and IPv6 (::1), skips duplicates, removes legacy entries and
flushes the Windows DNS cache so the change applies immediately."""

import ctypes
import os
import subprocess
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

    def __init__(self):
        self.current_list_name = None
        self.root = None
        self.websites_text = None
        self._submitted = threading.Event()
        self._thread = None

    # ----- hosts file helpers (static in the Java original) -----

    @staticmethod
    def format(website):
        """Normalize to the "www." form; scheme, path, port and case are stripped.

        A stray "/" or path used to land in the hosts file, which made the
        line an invalid hostname that Windows silently ignores — blocking
        "worked" but never blocked anything."""
        website = website.strip().lower()
        for scheme in ("https://", "http://"):
            if website.startswith(scheme):
                website = website[len(scheme):]
                break
        website = website.split("/")[0]  # drop any path
        website = website.split(":")[0]  # the hosts file knows no ports
        website = website.strip(".")
        if not website:
            return ""
        if not website.startswith("www."):
            website = "www." + website
        return website

    @staticmethod
    def _variants(website):
        """The bare and the "www." form of the domain — both must be blocked,
        otherwise the site stays reachable through the other one."""
        domain = BlacklistGUI.format(website)
        if not domain:
            return []
        bare = domain[4:] if domain.startswith("www.") else domain
        www = domain if domain.startswith("www.") else "www." + domain
        return sorted({bare, www})

    @staticmethod
    def _flush_dns():
        """Flush the Windows DNS cache so hosts changes apply immediately."""
        try:
            ctypes.windll.dnsapi.DnsFlushResolverCache()
        except (AttributeError, OSError):
            pass
        try:
            subprocess.run(["ipconfig", "/flushdns"], capture_output=True, timeout=5)
        except (OSError, subprocess.SubprocessError):
            pass

    @staticmethod
    def _redirect_fields(line):
        """(ip, hostnames) of a hosts line, ignoring comments; "/" junk is
        stripped from hostnames so legacy broken entries still match."""
        fields = [field.split("/")[0] for field in line.split("#")[0].split()]
        if len(fields) < 2:
            return None
        return fields[0], fields[1:]

    @staticmethod
    def block_website(website):
        """Redirect the site (bare and www form, IPv4 and IPv6) to localhost."""
        variants = BlacklistGUI._variants(website)
        if not variants:
            print("Not a valid website: " + str(website))
            return False
        redirects = []
        for variant in variants:
            redirects.append(f"127.0.0.1 {variant} # ProductivityApp")
            redirects.append(f"::1 {variant} # ProductivityApp")
        try:
            with open(BlacklistGUI.hosts_path, "r", encoding="utf-8", errors="ignore") as reader:
                content = reader.read()
        except OSError as e:
            print("Error reading the hosts file: " + str(e))
            return False
        existing = set()
        for line in content.splitlines():
            fields = BlacklistGUI._redirect_fields(line)
            if fields is not None:
                ip, hostnames = fields
                for hostname in hostnames:
                    existing.add(ip + " " + hostname)
        missing = [redirect for redirect in redirects
                   if redirect.split("#")[0].strip() not in existing]
        if not missing:
            return True  # already blocked
        try:
            import stat
            try:
                attrs = os.stat(BlacklistGUI.hosts_path).st_mode
                if not (attrs & stat.S_IWRITE):
                    os.chmod(BlacklistGUI.hosts_path, stat.S_IWRITE)
            except OSError:
                pass
            with open(BlacklistGUI.hosts_path, "a", encoding="utf-8") as writer:
                if content and not content.endswith("\n"):
                    writer.write("\n")
                for redirect in missing:
                    writer.write(redirect + "\n")
        except OSError as e:
            print("Error writing to the hosts file (run as administrator): "
                  + str(e))
            return False
        BlacklistGUI._flush_dns()
        return True

    @staticmethod
    def unblock_website(url):
        """Remove every hosts line that redirects the site (either form, either IP)."""
        variants = set(BlacklistGUI._variants(url))
        if not variants:
            return False
        try:
            with open(BlacklistGUI.hosts_path, "r", encoding="utf-8", errors="ignore") as reader:
                lines = reader.read().splitlines()
        except OSError as e:
            print("Error reading the hosts file: " + str(e))
            return False
        kept = []
        for line in lines:
            fields = BlacklistGUI._redirect_fields(line)
            if fields is not None and fields[0] in ("127.0.0.1", "::1") \
                    and any(hostname in variants for hostname in fields[1]):
                continue  # a redirect line for this site
            kept.append(line)
        if kept == lines:
            return True  # nothing pointed at the site
        try:
            import stat
            try:
                attrs = os.stat(BlacklistGUI.hosts_path).st_mode
                if not (attrs & stat.S_IWRITE):
                    os.chmod(BlacklistGUI.hosts_path, stat.S_IWRITE)
            except OSError:
                pass
            with open(BlacklistGUI.hosts_path, "w", encoding="utf-8") as writer:
                for line in kept:
                    writer.write(line + "\n")
        except OSError as e:
            print("Error writing to the hosts file (run as administrator): "
                  + str(e))
            return False
        BlacklistGUI._flush_dns()
        return True

    @classmethod
    def clean_unblocked_hosts(cls, active_websites=None):
        """Remove hosts entries for any websites not in the active set."""
        if active_websites is None:
            active_websites = set()
        active_normalized = {cls.format(w) for w in active_websites}
        try:
            import storage
            all_sites = set()
            for b in storage.get_blocks():
                all_sites.update(b.websites)
            for site in all_sites:
                norm = cls.format(site)
                if norm not in active_normalized:
                    cls.unblock_website(site)
        except Exception as e:
            print(f"Error cleaning inactive hosts entries: {e}")


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

    # ----- GUI (legacy; the current flows collect lists in create_block_gui) -----

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
