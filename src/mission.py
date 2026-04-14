# src/api/mission.py
from src.mission_engine import MissionEngine, save_mission

def run_mission(goal):
    engine = MissionEngine()
    mission = engine.build_mission(goal)
    path = save_mission(goal, mission)
    return mission, path