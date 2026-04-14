# src/ui/organs/harvester_dashboard.py
def render_harvester_dashboard(status):
    return {
        "connected": status.connected,
        "selector": status.selector,
        "total_chats": status.total_chats,
        "harvested": status.harvested,
        "current_chat": status.current_chat,
        "errors": status.errors[-5:],  # last 5 errors
        "logs": status.logs[-20:],     # last 20 log lines
    }