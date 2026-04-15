import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from collections import defaultdict
import datetime as _dt
from src.primitives.engine import InferenceEngine
from src.primitives.intelligence import IntelligenceManager

MEMORY_ROOT = Path("memory")
ENTITY_MAP_PATH = Path("data/entity_map.json")
TIMELINE_PATH = Path("data/timeline.json")

engine = InferenceEngine()
intel = IntelligenceManager()

def log(msg: str) -> None:
    print(f"[CTX] {msg}")


# ---------- Low-level loaders ----------

def _load_json(path: Path) -> Optional[Any]:
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_all_segments() -> List[Dict[str, Any]]:
    segments: List[Dict[str, Any]] = []
    if not MEMORY_ROOT.exists():
        return segments

    for domain_dir in MEMORY_ROOT.iterdir():
        seg_dir = domain_dir / "segments"
        if not seg_dir.exists():
            continue
        for p in seg_dir.glob("*.json"):
            try:
                obj = _load_json(p)
                if isinstance(obj, dict):
                    obj.setdefault("domain", domain_dir.name)
                    segments.append(obj)
            except Exception as e:
                log(f"Error loading segment {p}: {e}")
    return segments


def _load_entity_map() -> Dict[str, Any]:
    data = _load_json(ENTITY_MAP_PATH)
    return data if isinstance(data, dict) else {}


def _load_timeline() -> List[Dict[str, Any]]:
    data = _load_json(TIMELINE_PATH)
    return data if isinstance(data, list) else []


# ---------- Core context structures ----------

def build_context_index() -> Dict[str, Any]:
    """
    Build an in-memory index over segments, entities, topics, and sources.
    This is the core 'overstanding' structure the governor uses.
    """
    segments = _load_all_segments()
    entity_map = _load_entity_map()
    timeline = _load_timeline()

    by_domain: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    by_topic: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    by_source: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    by_entity: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

    for seg in segments:
        domain = seg.get("domain", "unknown")
        by_domain[domain].append(seg)

        for t in seg.get("topics", []) or []:
            by_topic[t].append(seg)

        src = seg.get("source_id", "unknown")
        by_source[src].append(seg)

        for ent in seg.get("entities", []) or []:
            by_entity[ent].append(seg)

    ctx = {
        "segments": segments,
        "by_domain": dict(by_domain),
        "by_topic": dict(by_topic),
        "by_source": dict(by_source),
        "by_entity": dict(by_entity),
        "entity_map": entity_map,
        "timeline": timeline,
    }

    log(
        f"Context index built: {len(segments)} segments, "
        f"{len(by_domain)} domains, {len(by_topic)} topics, "
        f"{len(by_entity)} entities."
    )
    return ctx


# ---------- Query helpers ----------

def find_segments_by_topic(ctx: Dict[str, Any], topic: str) -> List[Dict[str, Any]]:
    return ctx.get("by_topic", {}).get(topic, [])


def find_segments_by_domain(ctx: Dict[str, Any], domain: str) -> List[Dict[str, Any]]:
    return ctx.get("by_domain", {}).get(domain, [])


def find_segments_by_entity(ctx: Dict[str, Any], entity: str) -> List[Dict[str, Any]]:
    return ctx.get("by_entity", {}).get(entity, [])


def find_segments_by_source(ctx: Dict[str, Any], source_id: str) -> List[Dict[str, Any]]:
    return ctx.get("by_source", {}).get(source_id, [])


# ---------- Situation snapshot ----------

def build_situation_snapshot(
    ctx: Dict[str, Any],
    *,
    topics: Optional[List[str]] = None,
    entities: Optional[List[str]] = None,
    domains: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Build a 'situation snapshot' – the minimal set of segments, entities,
    and timeline entries relevant to a given focus.
    """
    topics = topics or []
    entities = entities or []
    domains = domains or []

    seg_set: Dict[str, Dict[str, Any]] = {}

    for t in topics:
        for seg in find_segments_by_topic(ctx, t):
            seg_set[seg["segment_id"]] = seg

    for e in entities:
        for seg in find_segments_by_entity(ctx, e):
            seg_set[seg["segment_id"]] = seg

    for d in domains:
        for seg in find_segments_by_domain(ctx, d):
            seg_set[seg["segment_id"]] = seg

    segments = list(seg_set.values())

    # Pull relevant timeline entries (very simple: match source_id)
    timeline = ctx.get("timeline", [])
    relevant_sources = {s.get("source_id") for s in segments if s.get("source_id")}
    relevant_timeline = [
        ev for ev in timeline if ev.get("source_id") in relevant_sources
    ]

    # Pull relevant entities from entity_map
    entity_map = ctx.get("entity_map", {})
    relevant_entities = {
        name: data
        for name, data in entity_map.items()
        if name in entities or any(name in (s.get("entities") or []) for s in segments)
    }

    snapshot = {
        "segments": segments,
        "timeline": relevant_timeline,
        "entities": relevant_entities,
        "topics": topics,
        "domains": domains,
    }

    log(
        f"Situation snapshot: {len(segments)} segments, "
        f"{len(relevant_timeline)} timeline events, "
        f"{len(relevant_entities)} entities."
    )
    return snapshot


# ---------- High-level 'overstanding' API ----------

def summarize_situation(snapshot: Dict[str, Any]) -> str:
    """
    Lightweight textual summary of what the system 'knows' about a situation.
    This is intentionally simple and local-model-friendly.
    """
    segs = snapshot.get("segments", [])
    ents = snapshot.get("entities", {})
    topics = snapshot.get("topics", [])
    domains = snapshot.get("domains", [])

    lines: List[str] = []

    if topics:
        lines.append(f"Topics: {', '.join(topics)}")
    if domains:
        lines.append(f"Domains: {', '.join(domains)}")
    if ents:
        lines.append(f"Entities: {', '.join(sorted(ents.keys()))}")

    lines.append(f"Segment count: {len(segs)}")

    # Include a few short excerpts
    for seg in segs[:5]:
        text = seg.get("text", "").strip().replace("\n", " ")
        if len(text) > 200:
            text = text[:197] + "..."
        lines.append(f"- [{seg.get('domain', 'unknown')}] {text}")

    return "\n".join(lines)


def infer_intent_from_query(ctx: Dict[str, Any], query: str) -> Dict[str, Any]:
    """
    Infers intent using a local LLM with keyword matching as a fallback.
    """
    available_topics = list(ctx.get("by_topic", {}).keys())
    available_entities = list(ctx.get("entity_map", {}).keys())
    
    # 1. Attempt LLM Reasoning
    prompt = f"""
    Task: Analyze user query intent for a personal intelligence system.
    User Query: "{query}"

    Identify relevant topics, domains, and entities from the provided lists.
    Valid Domains: ["technical", "legal", "personal", "media", "land_rights", "administrative"]
    Available Topics: {available_topics[:100]}
    Available Entities: {available_entities[:100]}

    Return ONLY a JSON object:
    {{
      "topics": ["matching topics"],
      "domains": ["matching domains"],
      "entities": ["matching entities"]
    }}
    """
    
    model = intel.get_model("reasoning")
    llm_res = engine.generate(model, prompt)
    
    if llm_res:
        return {
            "topics": [t for t in llm_res.get("topics", []) if t in available_topics],
            "domains": [d for d in llm_res.get("domains", []) if d in ["technical", "legal", "personal", "media", "land_rights", "administrative"]],
            "entities": [e for e in llm_res.get("entities", []) if e in available_entities]
        }

    # 2. Fallback: Keyword Matching Logic
    log("Using keyword fallback for intent detection.")
    q = query.lower()
    topics: List[str] = []
    domains: List[str] = []
    entities: List[str] = []

    # Topic hints
    for t in ctx.get("by_topic", {}).keys():
        if t.lower() in q:
            topics.append(t)

    # Domain hints
    if any(k in q for k in ["law", "statute", "probate", "court", "affidavit"]):
        domains.append("legal")
    if any(k in q for k in ["ticket", "citation", "court date", "expired tag"]):
        domains.append("administrative")
    if any(k in q for k in ["boundary", "survey", "deed", "plat", "encroachment", "land"]):
        domains.append("land_rights")
    if any(k in q for k in ["python", "selenium", "wsl", "driver", "gpu"]):
        domains.append("technical")
    if any(k in q for k in ["youtube", "video", "channel"]):
        domains.append("media")

    # Situation hints
    if any(k in q for k in ["boundary", "encroachment", "property line"]):
        topics.append("boundary_dispute")
    if "neighbor" in q and "property" in q:
        topics.append("boundary_dispute")

    # Entity hints (simple substring match)
    for name in ctx.get("entity_map", {}).keys():
        if name.lower() in q:
            entities.append(name)

    return {
        "topics": list(dict.fromkeys(topics)),
        "domains": list(dict.fromkeys(domains)),
        "entities": list(dict.fromkeys(entities)),
    }


def get_context_for_query(query: str) -> Dict[str, Any]:
    """
    Main entrypoint: given a user query, build a situation snapshot
    that other organs (actions, UI, future writer) can use.
    """
    ctx = build_context_index()
    focus = infer_intent_from_query(ctx, query)
    snapshot = build_situation_snapshot(
        ctx,
        topics=focus["topics"],
        entities=focus["entities"],
        domains=focus["domains"],
    )
    return {
        "focus": focus,
        "snapshot": snapshot,
        "summary": summarize_situation(snapshot),
        "generated_at": _dt.datetime.utcnow().isoformat() + "Z",
    }


# ---------- CLI / debug ----------

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m src.reasoner.context_governor \"your question or task\"")
        raise SystemExit(1)

    query = " ".join(sys.argv[1:])
    log(f"Query: {query}")
    ctx_result = get_context_for_query(query)
    print("\n=== FOCUS ===")
    print(json.dumps(ctx_result["focus"], indent=2, ensure_ascii=False))
    print("\n=== SUMMARY ===")
    print(ctx_result["summary"])