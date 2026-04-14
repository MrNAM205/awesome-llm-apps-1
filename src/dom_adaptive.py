# src/dom_adaptive.py
import json
from pathlib import Path
from selenium.webdriver.common.by import By

SELECTOR_FILE = Path("config/selectors.json")

# Candidate selectors to try
SELECTOR_CANDIDATES = [
    '[data-testid="ai-message"]',
    '[data-testid="user-message"]',
    '[data-content="ai-message"]',
    '[data-content="user-message"]',
    '[data-message]',
    'div.group\\/ai-message',
    'div.group\\/user-message',
    'message-turn',  # shadow DOM
]

def load_saved_selector():
    if SELECTOR_FILE.exists():
        try:
            with open(SELECTOR_FILE, "r") as f:
                data = json.load(f)
                return data.get("selector")
        except:
            return None
    return None

def save_selector(selector):
    SELECTOR_FILE.parent.mkdir(exist_ok=True)
    with open(SELECTOR_FILE, "w") as f:
        json.dump({"selector": selector}, f, indent=2)

def try_selector(driver, selector):
    try:
        elements = driver.find_elements(By.CSS_SELECTOR, selector)
        if elements:
            return elements
    except:
        pass
    return None

def pierce_shadow_dom(driver):
    """Fallback: extract messages from shadow DOM."""
    try:
        roots = driver.find_elements(By.CSS_SELECTOR, "chat-thread")
        for root in roots:
            shadow = driver.execute_script("return arguments[0].shadowRoot", root)
            if shadow:
                return shadow.find_elements(By.CSS_SELECTOR, "message-turn")
    except:
        return None

def get_message_elements(driver):
    """
    Adaptive selector system:
    1. Try saved selector
    2. Try all candidates
    3. Try shadow DOM
    """
    # 1. Try saved selector
    saved = load_saved_selector()
    if saved:
        elems = try_selector(driver, saved)
        if elems:
            return elems

    # 2. Try all candidates
    for selector in SELECTOR_CANDIDATES:
        elems = try_selector(driver, selector)
        if elems:
            save_selector(selector)
            return elems

    # 3. Shadow DOM fallback
    elems = pierce_shadow_dom(driver)
    if elems:
        save_selector("shadow-dom")
        return elems

    return []