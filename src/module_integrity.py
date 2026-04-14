import os
from pathlib import Path

REQUIRED_MODULES = [
    "knowledge_engine.py", "embedder.py", "harvester.py",
    "store.py", "config.py", "utils.py",
]

def check_integrity():
    src = Path(__file__).parent
    missing = []

    for mod in REQUIRED_MODULES:
        if not (src / mod).exists():
            missing.append(mod)

    if missing:
        print("ERROR: Missing required modules in src/:")
        for m in missing:
            print(f" - {m}")
        return False
    print("Module integrity check passed.")
    return True