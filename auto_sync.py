import time
import subprocess
import sys

def run_sync():
    subprocess.run([sys.executable, "main.py", "--sync"], check=False)

if __name__ == "__main__":
    while True:
        run_sync()
        time.sleep(24 * 60 * 60)