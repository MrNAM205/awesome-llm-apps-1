import psutil
from typing import List, Dict

class IntelligenceManager:
    """
    Intelligence: Manages the catalog of models and provider mapping.
    """
    def __init__(self):
        # Perform hardware check for system RAM
        total_ram_gb = psutil.virtual_memory().total / (1024**3)

        if total_ram_gb < 8:
            # Constrained environment: default to TinyLlama
            self.catalog = {
                "reasoning": "tinyllama",
                "extraction": "tinyllama",
                "embedding": "nomic-embed-text"
            }
        else:
            # Standard environment: use full-sized local models
            self.catalog = {
                "reasoning": "llama3",
                "extraction": "mistral",
                "embedding": "nomic-embed-text"
            }

    def get_model(self, task: str) -> str:
        """Picks the model based on the hardware profile and task type."""
        default_model = self.catalog.get("reasoning", "llama3")
        return self.catalog.get(task, default_model)

    def list_local_models(self) -> List[str]:
        """Query local runtime for available models."""
        # Logic to call engine.list_models() would go here
        return ["llama3", "mistral", "phi3", "tinyllama"]