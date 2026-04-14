import os
import shutil
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "src"
LOG = ROOT / "shadow_cleaner.log"

SHADOW_TARGETS = [
    "knowledge_engine", "embedder", "store", "harvester",
    "config", "utils", "ingest", "browser_finder",
]

def log(msg):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(msg + "\n")
    print(msg)

def remove_if_exists(path: Path):
    if path.exists():
        try:
            if path.is_dir():
                shutil.rmtree(path)
                log(f"[CLEANED] Removed directory: {path}")
            else:
                path.unlink()
                log(f"[CLEANED] Removed file: {path}")
        except Exception as e:
            log(f"[ERROR] Failed to remove {path}: {e}")

def run_shadow_cleaner():
    log("=== Running Shadow Cleaner ===")
    for name in SHADOW_TARGETS:
        remove_if_exists(ROOT / f"{name}.py")
    
    remove_if_exists(ROOT / "__pycache__")
    remove_if_exists(SRC / "__pycache__")
    
    for pyc in ROOT.rglob("*.pyc"):
        remove_if_exists(pyc)
    
    log("=== Shadow Cleaner Complete ===")

if __name__ == "__main__":
    run_shadow_cleaner()