import os

def find_chrome_path_deep():
    search_roots = [
        r"C:\Users",
        r"C:\Program Files",
        r"C:\Program Files (x86)",
        r"C:\ProgramData"
    ]

    for root in search_roots:
        print(f"Scanning: {root}")
        if not os.path.exists(root): continue
        for dirpath, _, filenames in os.walk(root):
            if "chrome.exe" in filenames:
                full_path = os.path.join(dirpath, "chrome.exe")
                print("FOUND:", full_path)
                return full_path
    return None

if __name__ == "__main__":
    path = find_chrome_path_deep()
    if not path:
        print("\nChrome not found anywhere on this system.")