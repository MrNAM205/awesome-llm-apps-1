from typing import Dict, Any
from .context_governor import (
    build_context_index,
    build_situation_snapshot,
    summarize_situation,
)
from .land_rights_organ import explain_land_rights_situation
from .authority_retriever import search_authorities_hybrid
from .foia_organ import explain_foia_situation
from .housing_organ import explain_housing_situation
from .bond_intelligence_organ import explain_bond_situation


def log(msg: str) -> None:
    print(f"[SITUATION] {msg}")


# ---------- Situation detection ----------

def detect_situation_type(query: str) -> str:
    q = query.lower()

    # Land / property / boundary
    if any(k in q for k in [
        "property line", "boundary", "survey", "encroachment",
        "neighbor", "house on their property", "house on their land",
        "fence line", "right of way", "plat", "deed",
        "lot line", "property dispute", "tear down my house"
    ]):
        return "land_rights"

    # Traffic / citations / court
    if any(k in q for k in [
        "ticket", "citation", "traffic court", "speeding",
        "expired tag", "pulled over", "court date", "traffic stop"
    ]):
        return "traffic_court"

    # FOIA / Records Request
    if any(k in q for k in [
        "foia", "public records", "disclosure", "sunshine law", "records request"
    ]):
        return "foia_request"

    # Housing / Landlord-Tenant
    if any(k in q for k in [
        "lease", "landlord", "tenant", "eviction", "rent", "security deposit"
    ]):
        return "housing"

    # Municipal Bond / CUSIP Intelligence
    if any(k in q for k in [
        "cusip", "municipal bond", "emma", "commercial paper", "state file number"
    ]):
        return "bond_intelligence"

    # Fallback
    return "general"


# ---------- Situation handlers ----------

def handle_land_rights(query: str, ctx: Dict[str, Any]) -> Dict[str, Any]:
    # Use the dedicated organ (knowledge + snapshot)
    land_res = explain_land_rights_situation(query)

    # Also build a focused snapshot for land/legal domains
    snapshot = build_situation_snapshot(
        ctx,
        domains=["legal", "land_rights"],
        topics=land_res.get("topics", []),
        entities=[]
    )

    return {
        "situation_type": "land_rights",
        "situation_summary": land_res.get("situation_summary")
            or summarize_situation(snapshot),
        "key_concepts": land_res.get("key_concepts", []),
        "common_documents": land_res.get("common_documents", []),
        "typical_steps": land_res.get("typical_steps", []),
        "professionals_people_consult": land_res.get("professionals_people_consult", []),
        "notes": land_res.get("notes", []),
        "snapshot": snapshot,
    }


def handle_traffic_court(query: str, ctx: Dict[str, Any]) -> Dict[str, Any]:
    # Focused snapshot for legal/administrative domains
    snapshot = build_situation_snapshot(
        ctx,
        domains=["legal", "administrative"],
        topics=[],
        entities=[]
    )

    # Factual knowledge could also be loaded from a JSON pack as done with land_rights
    return {
        "situation_type": "traffic_court",
        "situation_summary": summarize_situation(snapshot),
        "key_concepts": [
            "A traffic citation is a written notice alleging a violation of traffic rules.",
            "A court date is typically assigned for administrative processing.",
            "Documentation helps clarify the circumstances of the citation."
        ],
        "common_documents": [
            "The citation/ticket itself", "Vehicle registration", 
            "Driver's license", "Proof of insurance"
        ],
        "typical_steps": [
            "People often start by reading the citation carefully.",
            "They check the court date and location.",
            "They gather relevant documents such as registration and insurance."
        ],
        "professionals_people_consult": ["Court clerk", "Traffic court personnel"],
        "notes": ["Traffic matters often follow a predictable administrative process."],
        "snapshot": snapshot,
    }


# ---------- Main entrypoint ----------

def explain_situation(query: str) -> Dict[str, Any]:
    ctx = build_context_index()
    situation_type = detect_situation_type(query)
    log(f"Detected situation type: {situation_type}")

    if situation_type == "land_rights":
        report = handle_land_rights(query, ctx)
    elif situation_type == "traffic_court":
        report = handle_traffic_court(query, ctx)
    elif situation_type == "foia_request":
        report = explain_foia_situation(query)
    elif situation_type == "housing":
        report = explain_housing_situation(query)
    elif situation_type == "bond_intelligence":
        report = explain_bond_situation(query)
    else:
        snapshot = build_situation_snapshot(ctx)
        report = {
            "situation_type": "general",
            "situation_summary": summarize_situation(snapshot),
            "snapshot": snapshot
        }

    # Attach authorities (local + optional web)
    report["authorities"] = search_authorities_hybrid(query)
    return report