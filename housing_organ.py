import json
from pathlib import Path
from typing import Dict, Any, List
from .context_governor import (
    build_context_index,
    build_situation_snapshot,
    summarize_situation,
)

KNOWLEDGE_PACK_PATH = Path("src/knowledge/situations/housing.json")

def log(msg: str) -> None:
    print(f"[HOUSING] {msg}")

def load_knowledge_pack() -> Dict[str, Any]:
    if not KNOWLEDGE_PACK_PATH.exists():
        log("No housing knowledge pack found.")
        return {}
    with open(KNOWLEDGE_PACK_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def detect_housing_intent(query: str) -> bool:
    q = query.lower()
    keywords = [
        "lease", "landlord", "tenant", "eviction", "rent", 
        "security deposit", "notice to repair", "habitability",
        "apartment", "housing dispute", "rental agreement"
    ]
    return any(k in q for k in keywords)

def build_housing_snapshot(query: str) -> Dict[str, Any]:
    ctx = build_context_index()
    # Housing touches legal, administrative, and personal domains
    domains = ["legal", "administrative", "housing", "personal"]
    snapshot = build_situation_snapshot(ctx, domains=domains)
    return {
        "snapshot": snapshot,
        "summary": summarize_situation(snapshot),
        "knowledge": load_knowledge_pack(),
    }

def explain_housing_situation(query: str) -> Dict[str, Any]:
    """
    Neutral, procedural explainer for Housing / Landlord-Tenant situations.
    """
    if not detect_housing_intent(query):
        return {"is_housing": False}

    data = build_housing_snapshot(query)
    knowledge = data["knowledge"]

    return {
        "is_housing": True,
        "situation_type": "housing_dispute",
        "situation_summary": data["summary"],
        "key_concepts": knowledge.get("key_concepts", []),
        "common_documents": knowledge.get("common_documents", []),
        "typical_steps": knowledge.get("typical_steps", []),
        "professionals_people_consult": knowledge.get("professionals", []),
        "notes": knowledge.get("notes", []),
        "snapshot": data["snapshot"]
    }

if __name__ == "__main__":
    import sys
    query = " ".join(sys.argv[1:])
    if query:
        result = explain_housing_situation(query)
        print(json.dumps(result, indent=2, ensure_ascii=False))