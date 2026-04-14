# src/mission_engine.py
import json
from pathlib import Path
from src.embedder import embed_text
from src.timeline_reconstructor import load_timeline
from src.reasoning_loop import ReasoningLoop

class MissionEngine:
    def __init__(self):
        self.graph = None
        self.timeline = None
        self.reasoner = ReasoningLoop()

    def load_intelligence(self):
        graph_path = Path("entities_graph.json")
        self.graph = json.load(open(graph_path, "r", encoding="utf-8")) if graph_path.exists() else {}
        self.timeline = load_timeline()
        self.reasoner.load_intelligence()

    def interpret_goal(self, goal):
        q_vec = embed_text(goal)
        candidates = []
        for ent in self.graph:
            ent_vec = embed_text(ent)
            sim = float(q_vec @ ent_vec)
            if sim > 0.25:
                candidates.append((ent, sim))
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[:5]

    def generate_tasks(self, goal, related_entities):
        tasks = []
        for ent, score in related_entities:
            tasks.append({
                "task": f"Review subsystem: {ent}",
                "confidence": score,
                "dependencies": [],
                "evidence": self.graph[ent].get("mentions", [])[:2]
            })
        return tasks

    def expand_subtasks(self, tasks):
        for t in tasks:
            ent = t["task"].replace("Review subsystem: ", "")
            rels = list(self.graph[ent].get("relationships", {}).keys())[:3]
            t["subtasks"] = [f"Analyze relationship with {r}" for r in rels]
        return tasks

    def assess_risks(self, tasks):
        risks = []
        for t in tasks:
            if t["confidence"] < 0.3:
                risks.append(f"Low confidence in task: {t['task']}")
            if len(t.get("subtasks", [])) > 2:
                risks.append(f"Subsystem {t['task']} has high complexity")
        return risks

    def next_steps(self, goal):
        reasoning = self.reasoner.run(goal)
        return reasoning["suggestions"]

    def build_mission(self, goal):
        self.load_intelligence()
        related = self.interpret_goal(goal)
        tasks = self.generate_tasks(goal, related)
        tasks = self.expand_subtasks(tasks)
        risks = self.assess_risks(tasks)
        suggestions = self.next_steps(goal)

        return {
            "goal": goal,
            "related_entities": related,
            "tasks": tasks,
            "risks": risks,
            "suggestions": suggestions
        }

def save_mission(goal, mission):
    Path("missions").mkdir(exist_ok=True)
    safe_name = "".join(c if c.isalnum() else "_" for c in goal)
    out_path = Path("missions") / f"{safe_name}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(mission, f, indent=2)
    return out_path