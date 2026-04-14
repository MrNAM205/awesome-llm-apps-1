# module_migrator.py
import shutil
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "src"
LOG = ROOT / "module_migrator.log"

MODULES_THAT_BELONG_IN_SRC = [
    "knowledge_engine.py",
    "embedder.py",
    "store.py",
    "harvester.py",
    "config.py",
    "utils.py",
    "ingest.py",
    "browser_finder.py",
]

def log(msg):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(msg + "\n")
    print(msg)

def migrate_modules():
    log("=== Running Module Migrator ===")
    for filename in MODULES_THAT_BELONG_IN_SRC:
        root_file = ROOT / filename
        src_file = SRC / filename

        if root_file.exists() and not src_file.exists():
            shutil.move(str(root_file), str(src_file))
            log(f"[MOVED] {filename} → src/{filename}")
        elif root_file.exists() and src_file.exists():
            root_file.unlink()
            log(f"[DELETED] Duplicate root-level {filename}")

    for cache in ROOT.rglob("__pycache__"):
        shutil.rmtree(cache, ignore_errors=True)
        log(f"[CLEANED] Removed cache: {cache}")

    log("=== Module Migrator Complete ===")

if __name__ == "__main__":
    migrate_modules()