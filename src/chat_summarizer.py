# src/chat_summarizer.py
import json
from pathlib import Path
from src.embedder import embed_text

def summarize_chat(messages):
    """
    Generates structured summaries for a chat.
    Uses embeddings + heuristics for topic extraction.
    """

    # Combine all text
    full_text = "\n".join([m["content"] for m in messages])

    # Short summary (very compressed)
    short_summary = (
        full_text[:200].rsplit(" ", 1)[0] + "..."
        if len(full_text) > 200 else full_text
    )

    # Long summary (more detailed)
    long_summary = (
        full_text[:600].rsplit(" ", 1)[0] + "..."
        if len(full_text) > 600 else full_text
    )

    # Extract key ideas (simple heuristic)
    key_points = []
    for m in messages:
        if len(m["content"]) > 40:
            key_points.append(m["content"])
        if len(key_points) >= 5:
            break

    # Extract entities (very simple heuristic)
    entities = []
    for m in messages:
        words = m["content"].split()
        for w in words:
            if w.istitle() and len(w) > 3:
                entities.append(w)
        if len(entities) >= 10:
            break

    # Action items (look for imperative verbs)
    action_items = []
    for m in messages:
        text = m["content"]
        if text.startswith(("Do ", "Add ", "Fix ", "Change ", "Update ", "Implement ")):
            action_items.append(text)
        if len(action_items) >= 5:
            break

    return {
        "short_summary": short_summary,
        "long_summary": long_summary,
        "key_points": key_points,
        "entities": entities,
        "action_items": action_items,
    }

def save_summary(title, messages, output="incoming_chats"):
    summary = summarize_chat(messages)
    out_path = Path(output) / f"{title}_summary.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    return out_path