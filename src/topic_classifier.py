# src/topic_classifier.py
import json
from pathlib import Path
from src.embedder import embed_text

# Predefined topic space (expandable)
TOPIC_SPACE = {
    "coding": ["python", "javascript", "code", "function", "class", "bug", "script"],
    "ai": ["model", "embedding", "llm", "agent", "prompt", "vector", "faiss"],
    "ui": ["react", "component", "ui", "frontend", "layout", "dashboard"],
    "system": ["server", "backend", "api", "route", "process", "module"],
    "workflow": ["pipeline", "automation", "task", "sync", "ingest"],
    "legal": ["contract", "trust", "property", "statute", "filing"],
    "personal": ["life", "feelings", "plans", "goals", "ideas"],
}

def classify_topics(messages):
    """
    Multi-label topic classifier using:
    - Embedding similarity
    - Keyword heuristics
    - Frequency scoring
    """
    full_text = " ".join([m["content"] for m in messages]).lower()

    # Keyword scoring
    scores = {topic: 0 for topic in TOPIC_SPACE}

    for topic, keywords in TOPIC_SPACE.items():
        for kw in keywords:
            if kw in full_text:
                scores[topic] += 1

    # Embedding similarity
    text_vec = embed_text(full_text)

    for topic in TOPIC_SPACE:
        topic_vec = embed_text(topic)
        # Dot product for similarity
        sim = float(text_vec @ topic_vec)
        scores[topic] += sim

    # Sort by score
    sorted_topics = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    # Primary = top 2, Secondary = next 3
    primary = [t for t, s in sorted_topics[:2] if s > 0]
    secondary = [t for t, s in sorted_topics[2:5] if s > 0]

    return {
        "primary_topics": primary,
        "secondary_topics": secondary,
        "scores": scores,
    }

def save_topics(title, messages, output="incoming_chats"):
    topics = classify_topics(messages)
    out_path = Path(output) / f"{title}_topics.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(topics, f, indent=2)
    return out_path