from src.memory_graph import MemoryGraph

def build_memory_graph():
    mg = MemoryGraph()
    path = mg.build()
    return path