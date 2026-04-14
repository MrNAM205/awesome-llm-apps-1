# src/ui/organs/reasoning_panel.py
def render_reasoning_panel(result):
    return {
        "query": result["query"],
        "retrieved": result["retrieved"],
        "risks": result["risks"],
        "suggestions": result["suggestions"],
        "reasoning": result["reasoning"],
    }