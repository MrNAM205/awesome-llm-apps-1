# src/global_entity_map.py
import json
from pathlib import Path
from collections import defaultdict

def load_entities_files(folder="incoming_chats"):
    """Load all *_entities.json files."""
    return list(Path(folder).glob("*_entities.json"))

def merge_entity_maps(files):
    """Build a global entity graph aligned with src/entity_map.py format."""
    graph = defaultdict(lambda: {
        "mentions": [],
        "relationships": defaultdict(lambda: {"weight": 0, "evidence": []})
    })

    for f in files:
        with open(f, "r", encoding="utf-8") as file:
            data = json.load(file)
        chat_title = f.stem.replace("_entities", "")

        # Align keys with src/entity_map.py (entity_counts and map)
        entities = data.get("entity_counts", {})
        relationships = data.get("map", {})

        for ent, count in entities.items():
            graph[ent]["mentions"].append({"chat": chat_title, "count": count})

        for a, related in relationships.items():
            for b, details in related.items():
                target = graph[a]["relationships"][b]
                target["weight"] += details.get("strength", 0)
                target["evidence"].extend(details.get("evidence", []))

    return {
        ent: {
            "mentions": info["mentions"],
            "relationships": {
                other: {"weight": rel["weight"], "evidence": list(set(rel["evidence"]))[:10]}
                for other, rel in info["relationships"].items()
            }
        }
        for ent, info in graph.items()
    }

def save_global_graph(graph, output="entities_graph.json"):
    with open(output, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)
    return output

def build_global_entity_map(folder="incoming_chats"):
    return save_global_graph(merge_entity_maps(load_entities_files(folder)))