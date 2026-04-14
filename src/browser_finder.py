import os
import shutil

def find_chrome():
    possible = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        rf"C:\Users\{os.getlogin()}\AppData\Local\Google\Chrome\Application\chrome.exe",
        rf"C:\Users\{os.getlogin()}\AppData\Local\Google\Chrome SxS\Application\chrome.exe",
    ]
    for path in possible:
        if os.path.exists(path):
            return path
    return None

def find_edge():
    # Edge is always installed here on Windows
    paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
    ]
    for path in paths:
        if os.path.exists(path):
            return path
    return shutil.which("msedge")

def detect_browser():
    chrome = find_chrome()
    if chrome:
        return ("chrome", chrome)
    edge = find_edge()
    if edge:
        return ("edge", edge)
    return (None, None)