from src.dom_adaptive import SELECTOR_FILE

def rebuild_selectors():
    if SELECTOR_FILE.exists():
        SELECTOR_FILE.unlink()
    return True