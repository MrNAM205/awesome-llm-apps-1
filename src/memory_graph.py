# src/memory_graph.py
import json
from pathlib import Path
from collections import defaultdict
from src.timeline_reconstructor import load_timeline

class MemoryGraph:
    def __init__(self):
        self.graph = defaultdict(lambda: {
            "mentions": 0,
            "relationships": defaultdict(int),
            "missions": [],
            "reasoning_refs": [],
            "timeline_refs": [],
            "topics": defaultdict(int),
            "summaries": [],
            "risk_flags": 0,
            "success_flags": 0
        })

    # ---------------------------------------------------------
    # LOAD INTELLIGENCE ARTIFACTS
    # ---------------------------------------------------------
    def load_entities(self):
        path = Path("entities_graph.json")
        return json.load(open(path, "r", encoding="utf-8")) if path.exists() else {}

    def load_timeline(self):
        return load_timeline()

    def load_missions(self):
        missions = []
        for f in Path("missions").glob("*.json"):
            with open(f, "r", encoding="utf-8") as file:
                missions.append(json.load(file))
        return missions

    def load_reasoning(self):
        traces = []
        for f in Path("reasoning").glob("*.json"):
            with open(f, "r", encoding="utf-8") as file:
                traces.append(json.load(file))
        return traces

    # ---------------------------------------------------------
    # MERGE ENTITIES
    # ---------------------------------------------------------
    def merge_entities(self, entities):
        for ent, info in entities.items():
            self.graph[ent]["mentions"] += len(info.get("mentions", []))
            for other, rel in info.get("relationships", {}).items():
                self.graph[ent]["relationships"][other] += rel.get("weight", 0)

    # ---------------------------------------------------------
    # MERGE TIMELINE
    # ---------------------------------------------------------
    def merge_timeline(self, timeline):
        for event in timeline:
            for ent in event.get("entities", []):
                self.graph[ent]["timeline_refs"].append(event)

    # ---------------------------------------------------------
    # MERGE MISSIONS
    # ---------------------------------------------------------
    def merge_missions(self, missions):
        for m in missions:
            goal = m.get("goal")
            for t in m.get("tasks", []):
                ent = t["task"].replace("Review subsystem: ", "")
                self.graph[ent]["missions"].append(goal)

            for r in m.get("risks", []):
                for ent in self.graph:
                    if ent in r:
                        self.graph[ent]["risk_flags"] += 1

    # ---------------------------------------------------------
    # MERGE REASONING
    # ---------------------------------------------------------
    def merge_reasoning(self, traces):
        for trace in traces:
            for r in trace.get("reasoning", []):
                ent = r.get("entity")
                self.graph[ent]["reasoning_refs"].append(trace.get("query"))

    # ---------------------------------------------------------
    # SAVE MEMORY GRAPH
    # ---------------------------------------------------------
    def save(self, output="memory_graph.json"):
        final = {ent: {k: (dict(v) if isinstance(v, defaultdict) else v) 
                 for k, v in info.items()} for ent, info in self.graph.items()}
        with open(output, "w", encoding="utf-8") as f:
            json.dump(final, f, indent=2)
        return output

    # ---------------------------------------------------------
    # MAIN PIPELINE
    # ---------------------------------------------------------
    def build(self):
        self.merge_entities(self.load_entities())
        self.merge_timeline(self.load_timeline())
        self.merge_missions(self.load_missions())
        self.merge_reasoning(self.load_reasoning())
        return self.save()