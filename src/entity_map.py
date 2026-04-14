# src/entity_map.py
import json
from pathlib import Path
from collections import defaultdict

def extract_entities_and_relations(messages):
    """
    Extracts entities and maps relationships:
    Entity -> Related Entities -> Strength -> Evidence
    """
    entities = defaultdict(int)
    relationships = defaultdict(lambda: defaultdict(lambda: {"strength": 0, "evidence": []}))
    
    for msg in messages:
        content = msg["content"]
        # Heuristic: Title Case words > 3 chars (excluding sentence starters handled by set)
        words = [w.strip(".,!?;:()\"") for w in content.split()]
        msg_entities = set()
        for w in words:
            if len(w) > 3 and w[0].isupper() and any(c.islower() for c in w[1:]):
                entities[w] += 1
                msg_entities.add(w)
        
        # Map relationships (co-occurrence in same message)
        ent_list = list(msg_entities)
        for i in range(len(ent_list)):
            for j in range(i + 1, len(ent_list)):
                a, b = sorted([ent_list[i], ent_list[j]])
                relationships[a][b]["strength"] += 1
                if len(relationships[a][b]["evidence"]) < 3:
                    relationships[a][b]["evidence"].append(content[:100] + "...")

    return {
        "entity_counts": dict(entities),
        "map": {k: dict(v) for k, v in relationships.items()}
    }

def save_entity_map(title, messages, output="incoming_chats"):
    data = extract_entities_and_relations(messages)
    out_path = Path(output) / f"{title}_entities.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return out_path