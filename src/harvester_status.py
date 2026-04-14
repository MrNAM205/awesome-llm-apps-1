# src/harvester_status.py
import time

class HarvesterStatus:
    def __init__(self):
        self.reset()

    def reset(self):
        self.connected = False
        self.selector = None
        self.total_chats = 0
        self.harvested = 0
        self.current_chat = None
        self.errors = []
        self.logs = []
        self.start_time = None

    def log(self, msg):
        timestamp = time.strftime("%H:%M:%S")
        entry = f"[{timestamp}] {msg}"
        self.logs.append(entry)
        print(entry)

    def set_selector(self, selector):
        self.selector = selector
        self.log(f"Using selector: {selector}")

    def set_connection(self, ok):
        self.connected = ok
        self.log("Chrome connected" if ok else "Chrome NOT connected")

    def set_total(self, n):
        self.total_chats = n
        self.log(f"Total chats: {n}")

    def set_current(self, title):
        self.current_chat = title
        self.log(f"Harvesting: {title}")

    def increment(self):
        self.harvested += 1
        self.log(f"Completed {self.harvested}/{self.total_chats}")

    def add_error(self, err):
        self.errors.append(err)
        self.log(f"ERROR: {err}")

status = HarvesterStatus()