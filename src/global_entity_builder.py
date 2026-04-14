import json
from pathlib import Path
from collections import defaultdict

def build_global_map(folder="incoming_chats", output_file="data/global_entity_map.json"):
    folder = Path(folder)
    global_counts = defaultdict(int)
    global_map = defaultdict(lambda: defaultdict(lambda: {"strength": 0, "evidence": []}))

    for file in folder.glob("*_entities.json"):
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
                for ent, count in data.get("entity_counts", {}).items():
                    global_counts[ent] += count
                for ent_a, relations in data.get("map", {}).items():
                    for ent_b, details in relations.items():
                        target = global_map[ent_a][ent_b]
                        target["strength"] += details["strength"]
                        target["evidence"].extend(details.get("evidence", []))
                        target["evidence"] = target["evidence"][:10]
        except Exception:
            continue

    out_path = Path(output_file)
    out_path.parent.mkdir(exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({
            "entity_counts": dict(global_counts),
            "map": {k: dict(v) for k, v in global_map.items()}
        }, f, indent=2)
    return out_path