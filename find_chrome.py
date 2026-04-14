import os

def find_chrome_path():
    """Automatically locate the Chrome executable on Windows."""
    possible_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome SxS\Application\chrome.exe"),
        os.path.expandvars(r"%LOCALAPPDATA%\Chromium\Application\chrome.exe"),
        r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
    ]

    for path in possible_paths:
        if os.path.exists(path):
            return path

    # Deep fallback search
    search_roots = [
        r"C:\Users", r"C:\Program Files", r"C:\Program Files (x86)", r"C:\ProgramData"
    ]
    for root in search_roots:
        if not os.path.exists(root): continue
        for dirpath, _, filenames in os.walk(root):
            if "chrome.exe" in filenames:
                return os.path.join(dirpath, "chrome.exe")
    
    return None

if __name__ == "__main__":
    chrome_path = find_chrome_path()
    if chrome_path:
        print(f"Chrome found at: {chrome_path}")
    else:
        print("Chrome not found on this system.")