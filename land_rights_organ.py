import json
from pathlib import Path
from typing import Dict, Any, List
from .context_governor import (
    build_context_index,
    build_situation_snapshot,
    summarize_situation,
)

KNOWLEDGE_PACK_PATH = Path("src/knowledge/land_rights_pack.json")


def log(msg: str) -> None:
    print(f"[LAND] {msg}")


def load_knowledge_pack() -> Dict[str, Any]:
    if not KNOWLEDGE_PACK_PATH.exists():
        log("No land rights knowledge pack found.")
        return {}
    with open(KNOWLEDGE_PACK_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def detect_land_rights_intent(query: str) -> bool:
    q = query.lower()
    keywords = [
        "property line", "boundary", "survey", "encroachment",
        "neighbor", "land", "house on their property",
        "fence line", "right of way", "plat", "deed",
        "lot line", "property dispute"
    ]
    return any(k in q for k in keywords)


def build_land_rights_snapshot(query: str) -> Dict[str, Any]:
    ctx = build_context_index()

    # Focus domains for land rights
    domains = ["legal", "land_rights"]

    # Build snapshot
    snapshot = build_situation_snapshot(
        ctx,
        domains=domains,
        topics=[],
        entities=[]
    )

    return {
        "snapshot": snapshot,
        "summary": summarize_situation(snapshot),
        "knowledge": load_knowledge_pack(),
    }


def explain_land_rights_situation(query: str) -> Dict[str, Any]:
    """
    High-level explainer for land/property/boundary situations.
    Neutral, factual, and procedural.
    """
    if not detect_land_rights_intent(query):
        return {
            "is_land_rights": False,
            "message": "Query does not appear to involve land or property rights."
        }

    data = build_land_rights_snapshot(query)
    knowledge = data["knowledge"]

    # Build a structured explanation
    explanation = {
        "is_land_rights": True,
        "situation_summary": data["summary"],
        "key_concepts": knowledge.get("key_concepts", []),
        "common_documents": knowledge.get("common_documents", []),
        "typical_steps": knowledge.get("typical_steps", []),
        "professionals_people_consult": knowledge.get("professionals", []),
        "notes": knowledge.get("notes", []),
    }

    return explanation


if __name__ == "__main__":
    import sys
    query = " ".join(sys.argv[1:])
    result = explain_land_rights_situation(query)
    print(json.dumps(result, indent=2, ensure_ascii=False))