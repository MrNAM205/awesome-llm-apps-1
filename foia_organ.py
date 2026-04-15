import json
from pathlib import Path
from typing import Dict, Any, List
from .context_governor import (
    build_context_index,
    build_situation_snapshot,
    summarize_situation,
)

KNOWLEDGE_PACK_PATH = Path("src/knowledge/situations/foia.json")

def log(msg: str) -> None:
    print(f"[FOIA] {msg}")

def load_knowledge_pack() -> Dict[str, Any]:
    if not KNOWLEDGE_PACK_PATH.exists():
        log("No FOIA knowledge pack found.")
        return {}
    with open(KNOWLEDGE_PACK_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def detect_foia_intent(query: str) -> bool:
    q = query.lower()
    keywords = [
        "foia", "public records", "freedom of information", 
        "records request", "government data", "sunshine law",
        "requesting documents from", "disclosure"
    ]
    return any(k in q for k in keywords)

def build_foia_snapshot(query: str) -> Dict[str, Any]:
    ctx = build_context_index()
    # FOIA touches administrative and legal domains
    domains = ["administrative", "legal", "foia"]
    snapshot = build_situation_snapshot(ctx, domains=domains)
    return {
        "snapshot": snapshot,
        "summary": summarize_situation(snapshot),
        "knowledge": load_knowledge_pack(),
    }

def explain_foia_situation(query: str) -> Dict[str, Any]:
    """
    Neutral, procedural explainer for Public Records / FOIA requests.
    """
    if not detect_foia_intent(query):
        return {"is_foia": False}

    data = build_foia_snapshot(query)
    knowledge = data["knowledge"]

    return {
        "is_foia": True,
        "situation_type": "foia_request",
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
        result = explain_foia_situation(query)
        print(json.dumps(result, indent=2, ensure_ascii=False))