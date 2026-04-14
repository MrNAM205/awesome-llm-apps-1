import os
import json
from pathlib import Path
from typing import List, Dict, Any

INCOMING_DIR = Path("incoming_chats")
MEMORY_ROOT = Path("memory")

DOMAINS = ["technical", "legal", "personal", "media"]


def log(msg: str) -> None:
    print(f"[SEGMENT] {msg}")


def ensure_dirs() -> None:
    for d in DOMAINS:
        (MEMORY_ROOT / d / "segments").mkdir(parents=True, exist_ok=True)


# ---------- Core helpers ----------

def load_chat(path: Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def flatten_messages(chat: Dict[str, Any]) -> str:
    """
    Simple first pass: concatenate all messages into one text block.
    Later you can get fancy (per-role, per-turn, etc.).
    """
    msgs = chat.get("messages") or chat
    # Support both {"messages": [...]} and plain list
    if isinstance(msgs, list):
        texts = []
        for m in msgs:
            if isinstance(m, dict):
                texts.append(m.get("content", "").strip())
            else:
                texts.append(str(m).strip())
        return "\n\n".join(t for t in texts if t)
    return ""


# ---------- Segmentation + classification stubs ----------

def segment_text(text: str) -> List[Dict[str, Any]]:
    """
    For now: naive segmentation by paragraphs.
    Later: replace with LLM-based topic segmentation.
    """
    segments = []
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    offset = 0
    for idx, p in enumerate(paragraphs):
        start = text.find(p, offset)
        end = start + len(p)
        segments.append(
            {
                "index": idx,
                "text": p,
                "span": [start, end],
            }
        )
        offset = end
    return segments


def classify_segment(text: str) -> Dict[str, Any]:
    """
    Placeholder classifier.
    Later: replace with LLM or rules.
    """
    lower = text.lower()

    if any(k in lower for k in ["statute", "probate", "contract", "law", "court"]):
        domain = "legal"
    elif any(k in lower for k in ["gpu", "python", "selenium", "wsl", "driver", "chrome"]):
        domain = "technical"
    elif any(k in lower for k in ["family", "feel", "relationship", "friend"]):
        domain = "personal"
    elif any(k in lower for k in ["video", "youtube", "watch", "channel"]):
        domain = "media"
    else:
        domain = "technical"  # default bias for current use

    # Very simple topic extraction stub
    topics: List[str] = []
    if "wsl" in lower:
        topics.append("WSL")
    if "selenium" in lower:
        topics.append("Selenium")
    if "probate" in lower:
        topics.append("Probate law")
    if "youtube" in lower:
        topics.append("YouTube workflow")

    return {
        "domain": domain,
        "topics": topics,
        "situations": [],   # fill later with better logic
        "entities": [],     # hook into your entity extractor later
    }


# ---------- Routing ----------

def route_segment(segment: Dict[str, Any]) -> Path:
    domain = segment["domain"]
    if domain not in DOMAINS:
        domain = "technical"
    safe_id = segment["segment_id"].replace(":", "_").replace("#", "_")
    out_path = MEMORY_ROOT / domain / "segments" / f"{safe_id}.json"
    return out_path


def process_chat_file(path: Path) -> None:
    chat = load_chat(path)

    # Support both schemas: {"title":..., "messages":[...]} or plain list
    title = chat.get("title") or path.stem
    source_id = f"chat:{title}"

    text = flatten_messages(chat)
    if not text.strip():
        log(f"Skipping empty chat: {path.name}")
        return

    raw_segments = segment_text(text)
    if not raw_segments:
        log(f"No segments found for: {path.name}")
        return

    for seg in raw_segments:
        idx = seg["index"]
        seg_text = seg["text"]
        span = seg["span"]

        cls = classify_segment(seg_text)

        segment_obj = {
            "source_id": source_id,
            "segment_id": f"{source_id}#{idx}",
            "source_type": "chat",
            "text": seg_text,
            "span": span,
            "domain": cls["domain"],
            "topics": cls["topics"],
            "situations": cls["situations"],
            "entities": cls["entities"],
        }

        out_path = route_segment(segment_obj)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(segment_obj, f, ensure_ascii=False, indent=2)

        log(f"Segment routed → {out_path}")


def segment_and_route_all() -> None:
    ensure_dirs()
    if not INCOMING_DIR.exists():
        log("No incoming_chats directory found.")
        return

    files = sorted(INCOMING_DIR.glob("*.json"))
    if not files:
        log("No chat JSON files found in incoming_chats.")
        return

    log(f"Segmenting and routing {len(files)} chats...")
    for path in files:
        process_chat_file(path)
    log("Segmentation + routing complete.")