"""Stand-alone repair tool to unblock all websites and flush Windows DNS cache.

Run this script to immediately restore blocked websites in C:\Windows\System32\drivers\etc\hosts.
"""

import ctypes
import os
import stat
import subprocess
import sys


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except (AttributeError, OSError):
        return True


def run_as_admin():
    script = os.path.abspath(sys.argv[0])
    try:
        return ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, f'"{script}"', None, 1) > 32
    except (AttributeError, OSError):
        return False


def flush_dns():
    try:
        ctypes.windll.dnsapi.DnsFlushResolverCache()
    except Exception:
        pass
    try:
        subprocess.run(["ipconfig", "/flushdns"], capture_output=True, timeout=5)
    except Exception:
        pass


def main():
    if not is_admin():
        print("Requesting administrator access to modify hosts file...")
        if run_as_admin():
            sys.exit(0)
        print("Error: Administrator rights are required to modify the hosts file.")
        input("Press Enter to exit...")
        sys.exit(1)

    hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
    print(f"Reading {hosts_path}...")

    try:
        with open(hosts_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.read().splitlines()
    except Exception as e:
        print(f"Error reading hosts file: {e}")
        input("Press Enter to exit...")
        sys.exit(1)

    # Gather sites to clean from data/data.json if present
    sites_to_remove = {"youtube.com", "www.youtube.com"}
    try:
        import json
        data_json = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "data.json")
        if os.path.exists(data_json):
            with open(data_json, "r", encoding="utf-8") as f:
                data = json.load(f)
                for b in data.get("blocks", []):
                    for w in b.get("websites", []):
                        w = w.strip().lower()
                        for prefix in ("https://", "http://"):
                            if w.startswith(prefix):
                                w = w[len(prefix):]
                        w = w.split("/")[0].split(":")[0].strip(".")
                        if w:
                            sites_to_remove.add(w)
                            if w.startswith("www."):
                                sites_to_remove.add(w[4:])
                            else:
                                sites_to_remove.add("www." + w)
    except Exception:
        pass

    kept = []
    removed = []
    for line in lines:
        stripped = line.strip()
        # Check if line was created by ProductivityApp or contains any of the blocked sites
        is_blocked = False
        if "# ProductivityApp" in line:
            is_blocked = True
        else:
            parts = stripped.split()
            if len(parts) >= 2 and parts[0] in ("127.0.0.1", "::1"):
                hostnames = [h.split("#")[0].split("/")[0].lower() for h in parts[1:]]
                if any(h in sites_to_remove for h in hostnames):
                    is_blocked = True

        if is_blocked:
            removed.append(line)
        else:
            kept.append(line)

    if removed:
        print("\nRemoving the following blocked entries:")
        for r in removed:
            print(f"  - {r}")

        try:
            # Clear read-only attribute if set
            attrs = os.stat(hosts_path).st_mode
            if not (attrs & stat.S_IWRITE):
                os.chmod(hosts_path, stat.S_IWRITE)

            with open(hosts_path, "w", encoding="utf-8") as f:
                for line in kept:
                    f.write(line + "\n")
            print("Successfully updated hosts file!")
        except Exception as e:
            print(f"Error writing to hosts file: {e}")
            input("Press Enter to exit...")
            sys.exit(1)
    else:
        print("No ProductivityApp blocked entries found in hosts file.")

    flush_dns()
    print("Flushed Windows DNS resolver cache (ipconfig /flushdns).")
    print("\n-----------------------------------------------------------")
    print("SUCCESS: Websites have been unblocked.")
    print("-----------------------------------------------------------")
    print("IMPORTANT BROWSER NOTE:")
    print("If YouTube or another website still says 'Connection Refused':")
    print("1. Close and reopen your web browser (Chrome/Edge caches TCP connections).")
    print("2. Or in Chrome/Edge, open chrome://net-internals/#sockets and click")
    print("   'Flush socket pools'.")
    print("-----------------------------------------------------------")
    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()
