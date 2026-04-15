import json
import requests
from typing import Dict, Any, Optional

class InferenceEngine:
    """
    The Engine: Manages the inference runtime (Ollama, llama.cpp, etc.)
    and auto-detects hardware capabilities.
    """
    def __init__(self, endpoint: str = "http://127.0.0.1:11434/api/generate"):
        self.endpoint = endpoint

    def generate(self, model: str, prompt: str, system_prompt: str = "") -> Optional[Dict[str, Any]]:
        """Standardized interface for text generation."""
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "system": system_prompt,
                "stream": False,
                "format": "json"
            }
            response = requests.post(self.endpoint, json=payload, timeout=30)
            if response.status_code == 200:
                content = response.json().get("response", "{}")
                return json.loads(content)
        except Exception as e:
            print(f"[ENGINE ERROR] {e}")
        return None

    def get_hardware_profile(self) -> Dict[str, Any]:
        """Stub for hardware auto-detection logic."""
        return {
            "gpu_detected": True,
            "vram_gb": 8,
            "recommended_runtime": "ollama"
        }