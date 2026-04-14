# src/ui/organs/memory_panel.py
def render_memory_panel(memory_graph):
    return {
        "entities": list(memory_graph.keys()),
        "risk_hotspots": [
            (ent, info["risk_flags"])
            for ent, info in memory_graph.items()
            if info["risk_flags"] > 0
        ],
        "mission_activity": [
            (ent, len(info["missions"]))
            for ent, info in memory_graph.items()
        ]
    }