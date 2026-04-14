# src/ui/organs/mission_panel.py
def render_mission_panel(mission):
    return {
        "goal": mission["goal"],
        "tasks": mission["tasks"],
        "risks": mission["risks"],
        "suggestions": mission["suggestions"],
        "related_entities": mission["related_entities"]
    }