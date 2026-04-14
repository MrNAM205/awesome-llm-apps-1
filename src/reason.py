from src.reasoning_loop import ReasoningLoop, save_reasoning

def run_reasoning(query):
    loop = ReasoningLoop()
    result = loop.run(query)
    path = save_reasoning(query, result)
    return result, path