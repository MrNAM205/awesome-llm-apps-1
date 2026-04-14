# src/timeline_reconstructor.py
import json
import os
from pathlib import Path
from datetime import datetime

def build_timeline(folder="incoming_chats", output_file="data/timeline.json"):
    """Builds a chronological map of operational history."""
    folder = Path(folder)
    timeline = []

    # Identify base chat files (excluding auxiliary intelligence artifacts)
    chat_files = [f for f in folder.glob("*.json") 
                  if not any(s in f.name for s in ["_summary", "_topics", "_entities"])]

    for f in chat_files:
        title = f.stem
        summary_file = folder / f"{title}_summary.json"
        topics_file = folder / f"{title}_topics.json"
        entities_file = folder / f"{title}_entities.json"

        # Use file metadata for temporal sequencing
        mtime = os.path.getmtime(f)
        timestamp = datetime.fromtimestamp(mtime).isoformat()

        entry = {
            "title": title,
            "timestamp": timestamp,
            "primary_topics": [],
            "entities": [],
            "summary": ""
        }

        if summary_file.exists():
            entry["summary"] = json.load(open(summary_file, "r")).get("short_summary", "")
        if topics_file.exists():
            entry["primary_topics"] = json.load(open(topics_file, "r")).get("primary_topics", [])
        if entities_file.exists():
            entry["entities"] = list(json.load(open(entities_file, "r")).get("entity_counts", {}).keys())

        timeline.append(entry)

    timeline.sort(key=lambda x: x["timestamp"])

    out_path = Path(output_file)
    out_path.parent.mkdir(exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(timeline, f, indent=2)
    return out_path

def load_timeline(path="data/timeline.json"):
    if Path(path).exists():
        return json.load(open(path, "r", encoding="utf-8"))
    return []