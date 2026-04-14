# src/reasoning_loop.py
import json
from pathlib import Path
from src.embedder import embed_text
from src.timeline_reconstructor import load_timeline

class ReasoningLoop:
    def __init__(self):
        self.graph = None
        self.timeline = None

    def load_intelligence(self):
        """Load global intelligence artifacts."""
        graph_path = Path("entities_graph.json")
        self.graph = json.load(open(graph_path, "r", encoding="utf-8")) if graph_path.exists() else {}
        self.timeline = load_timeline()

    def retrieve_relevant(self, query):
        q_vec = embed_text(query)
        results = []
        for ent, info in self.graph.items():
            ent_vec = embed_text(ent)
            sim = float(q_vec @ ent_vec)
            if sim > 0.2:
                results.append((ent, sim))
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:5]

    def synthesize(self, query, retrieved):
        synthesis = []
        for ent, score in retrieved:
            mentions = self.graph[ent].get("mentions", [])
            synthesis.append({
                "entity": ent,
                "score": score,
                "evidence": mentions[:3]
            })
        return synthesis

    def reason(self, query, synthesis):
        reasoning = []
        for item in synthesis:
            ent = item["entity"]
            rels = self.graph[ent].get("relationships", {})
            reasoning.append({
                "entity": ent,
                "inferred_relationships": list(rels.keys())[:5],
                "confidence": item["score"]
            })
        return reasoning

    def evaluate(self, query, reasoning):
        risks = []
        suggestions = []
        for r in reasoning:
            if r["confidence"] < 0.3:
                risks.append(f"Low confidence on entity {r['entity']}")
            if len(r["inferred_relationships"]) > 3:
                suggestions.append(
                    f"Entity {r['entity']} is highly connected — consider reviewing subsystem dependencies."
                )
        return risks, suggestions

    def run(self, query):
        self.load_intelligence()
        retrieved = self.retrieve_relevant(query)
        synthesis = self.synthesize(query, retrieved)
        reasoning = self.reason(query, synthesis)
        risks, suggestions = self.evaluate(query, reasoning)

        return {
            "query": query,
            "retrieved": retrieved,
            "synthesis": synthesis,
            "reasoning": reasoning,
            "risks": risks,
            "suggestions": suggestions
        }

def save_reasoning(query, result):
    Path("reasoning").mkdir(exist_ok=True)
    safe_name = "".join(c if c.isalnum() else "_" for c in query)
    out_path = Path("reasoning") / f"{safe_name}_reasoning.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    return out_path