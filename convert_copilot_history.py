import csv
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# -----------------------------
# CONFIG
# -----------------------------
INPUT_FILES = [
    "copilot-chat-activity.csv",
    "copilot-in-Microsoft-365-apps-activity.csv",
    "windows-apps-copilot-activity-history.csv"
]
OUTPUT_DIR = Path("incoming_chats")
OUTPUT_DIR.mkdir(exist_ok=True)

# Split chats if messages are far apart in time (in hours)
SPLIT_THRESHOLD_HOURS = 6
ENABLE_TIME_SPLITTING = True
ENABLE_DEDUPLICATION = True

# -----------------------------
# HELPERS
# -----------------------------
def safe_filename(name: str) -> str:
    return "".join(c if c.isalnum() or c in "-_." else "_" for c in name)

def parse_timestamp(ts: str) -> datetime:
    try:
        return datetime.fromisoformat(ts.replace("Z", ""))
    except:
        return datetime.now()

# -----------------------------
# LOAD CSVs
# -----------------------------
rows = []
for file in INPUT_FILES:
    if not Path(file).exists():
        print(f"Skipping missing file: {file}")
        continue
    with open(file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

print(f"Loaded {len(rows)} rows from CSV files.")

# -----------------------------
# GROUP BY CHAT NAME
# -----------------------------
chats = defaultdict(list)
for row in rows:
    chat_name = row.get("ChatName") or "UnknownChat"
    created_at = row.get("CreatedAt") or ""
    author = row.get("Author", "").lower()
    content = row.get("MessageContent", "")
    role = "user" if author == "user" else "assistant"

    chats[chat_name].append({
        "created_at": created_at,
        "timestamp": parse_timestamp(created_at),
        "role": role,
        "content": content.strip()
    })

# -----------------------------
# PROCESS AND WRITE
# -----------------------------
for chat_name, messages in chats.items():
    messages.sort(key=lambda m: m["timestamp"])

    if ENABLE_DEDUPLICATION:
        deduped, seen = [], set()
        for m in messages:
            key = (m["role"], m["content"])
            if key not in seen:
                seen.add(key)
                deduped.append(m)
        messages = deduped

    chat_splits = []
    if ENABLE_TIME_SPLITTING:
        current, last_ts = [], None
        for m in messages:
            if last_ts and (m["timestamp"] - last_ts).total_seconds() > SPLIT_THRESHOLD_HOURS * 3600:
                chat_splits.append(current)
                current = []
            current.append(m)
            last_ts = m["timestamp"]
        if current: chat_splits.append(current)
    else:
        chat_splits = [messages]

    for idx, split in enumerate(chat_splits, start=1):
        formatted = [{"role": m["role"], "content": m["content"]} for m in split]
        path = OUTPUT_DIR / f"{safe_filename(chat_name)}_{idx:03d}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"messages": formatted}, f, indent=2, ensure_ascii=False)
        print(f"Saved: {path}")

print("Done. All chats converted into incoming_chats/")