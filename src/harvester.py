import os
import re
import time
import json
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

# ---------------------------------------------------------
# FILENAME SANITIZER
# ---------------------------------------------------------
def sanitize_filename(name):
    return re.sub(r'[<>:"/\\|?*]', '', name)


# ---------------------------------------------------------
# ENSURE SIDEBAR IS EXPANDED
# ---------------------------------------------------------
def ensure_sidebar_expanded(driver):
    """
    Copilot collapses the sidebar by default.
    The chat list only exists when expanded.
    """
    # If expanded content exists, we're good
    try:
        driver.find_element(By.CSS_SELECTOR, 'div[data-testid="sidebar-expanded-content"]')
        return
    except:
        pass

    # Try to click the "Open sidebar" button
    try:
        toggle = driver.find_element(
            By.CSS_SELECTOR,
            'button[data-testid="sidebar-toggle-button"][aria-label="Open sidebar"]'
        )
        driver.execute_script("arguments[0].click();", toggle)
        time.sleep(1)
    except:
        print("[WARN] Could not expand sidebar.")

    # Wait for expanded content to appear
    for _ in range(10):
        try:
            driver.find_element(By.CSS_SELECTOR, 'div[data-testid="sidebar-expanded-content"]')
            return
        except:
            time.sleep(0.2)

    print("[WARN] Sidebar may still be collapsed.")


# ---------------------------------------------------------
# SIDEBAR FINDER (RESILIENT)
# ---------------------------------------------------------
def find_sidebar(driver):
    selectors = [
        'div[data-testid="sidebar-container"]',
        '[role="navigation"]',
        'aside'
    ]

    for sel in selectors:
        try:
            el = driver.find_element(By.CSS_SELECTOR, sel)
            print(f"[Sidebar] Found using selector: {sel}")
            return el
        except:
            pass

    raise Exception("Sidebar not found — Copilot UI changed again.")


# ---------------------------------------------------------
# SCROLL THE REAL CHAT LIST (NOT THE TOP MENU)
# ---------------------------------------------------------
def scroll_chat_list(driver):
    """
    The chat list scrolls inside:
        div[data-testid="sidebar-expanded-content"]
    """
    try:
        scroll_area = driver.find_element(
            By.CSS_SELECTOR,
            'div[data-testid="sidebar-expanded-content"]'
        )
    except:
        print("[WARN] Could not find chat list scroll area.")
        return

    last_height = -1
    while True:
        driver.execute_script(
            "arguments[0].scrollTop = arguments[0].scrollHeight;",
            scroll_area
        )
        time.sleep(1)

        new_height = driver.execute_script(
            "return arguments[0].scrollHeight;",
            scroll_area
        )

        if new_height == last_height:
            break

        last_height = new_height


# ---------------------------------------------------------
# GET CHAT LINKS FROM SIDEBAR
# ---------------------------------------------------------
def get_chat_links(driver):
    ensure_sidebar_expanded(driver)
    sidebar = find_sidebar(driver)

    scroll_chat_list(driver)

    chat_list = driver.find_element(
        By.CSS_SELECTOR,
        'div[data-testid="sidebar-expanded-content"] [role="listbox"]'
    )

    entries = chat_list.find_elements(By.CSS_SELECTOR, '[role="option"]')

    chats = []
    for e in entries:
        title = e.get_attribute("aria-label") or "Untitled Chat"
        chats.append((title, e))

    print(f"→ Found {len(chats)} chats.")
    return chats


# ---------------------------------------------------------
# SCROLL CHAT WINDOW TO TOP (LOAD ALL MESSAGES)
# ---------------------------------------------------------
def scroll_chat_to_top(driver):
    try:
        chat_area = driver.find_element(By.CSS_SELECTOR, "div[role='main']")
    except NoSuchElementException:
        print("[WARN] Could not find chat message container.")
        return

    last_height = None
    while True:
        driver.execute_script("arguments[0].scrollTop = 0;", chat_area)
        time.sleep(1)

        new_height = driver.execute_script(
            "return arguments[0].scrollHeight;",
            chat_area
        )

        if new_height == last_height:
            break

        last_height = new_height


# ---------------------------------------------------------
# EXTRACT MESSAGES FROM CHAT
# ---------------------------------------------------------
def extract_messages(driver):
    scroll_chat_to_top(driver)

    msg_nodes = driver.find_elements(By.CSS_SELECTOR, '[data-message-author]')
    messages = []

    for node in msg_nodes:
        role = node.get_attribute("data-message-author")
        text = node.text.strip()
        if text:
            messages.append({"role": role, "content": text})

    return messages


# ---------------------------------------------------------
# SAVE JSON
# ---------------------------------------------------------
def save_json(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


# ---------------------------------------------------------
# MAIN HARVEST LOOP
# ---------------------------------------------------------
def harvest_all_chats(driver=None):
    if driver is None:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        opts = Options()
        opts.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        driver = webdriver.Chrome(options=opts)

    ensure_sidebar_expanded(driver)
    chats = get_chat_links(driver)
    print(f"[{time.strftime('%H:%M:%S')}] Total chats: {len(chats)}\n")

    for i, (title, element) in enumerate(chats, start=1):
        print(f"[{i}/{len(chats)}] → Opening chat: {title}")
        safe_title = sanitize_filename(title)

        # Skip if already harvested
        if os.path.exists(f"incoming_chats/{safe_title}.json"):
            print(f"[{time.strftime('%H:%M:%S')}] Harvesting: {title}")
            print("   Skipping (already harvested).")
            print(f"[{time.strftime('%H:%M:%S')}] Completed {i}/{len(chats)}\n")
            continue

        try:
            driver.execute_script("arguments[0].click();", element)
            time.sleep(2)

            print(f"[{time.strftime('%H:%M:%S')}] Harvesting: {title}")

            messages = extract_messages(driver)

            if not messages:
                print("   Chat empty, skipping.\n")
                continue

            save_json(messages, f"incoming_chats/{safe_title}.json")
            print(f"   Saved → incoming_chats/{safe_title}.json")

            # Summaries, topics, entities
            from src.summarizer import summarize_chat
            from src.topic_classifier import classify_topics
            from src.entity_extractor import extract_entities

            summary = summarize_chat(messages)
            save_json(summary, f"incoming_chats/{safe_title}_summary.json")
            print(f"   Summary saved → incoming_chats/{safe_title}_summary.json")

            topics = classify_topics(messages)
            save_json(topics, f"incoming_chats/{safe_title}_topics.json")
            print(f"   Topics saved → incoming_chats/{safe_title}_topics.json")

            entities = extract_entities(messages)
            save_json(entities, f"incoming_chats/{safe_title}_entities.json")
            print(f"   Entity Map saved → incoming_chats/{safe_title}_entities.json")

            print(f"[{time.strftime('%H:%M:%S')}] Completed {i}/{len(chats)}\n")

        except Exception as e:
            print(f"[ERROR] Failed to harvest chat '{title}': {e}\n")
            continue
