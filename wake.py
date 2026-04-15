import time
import threading
from typing import Callable

class WakeListener:
    """
    Wake on Command: Monitors for a trigger (Voice or CLI Hot-key) 
    to activate the Situation Engine.
    """
    def __init__(self, trigger_word: str = "jarvis"):
        self.trigger_word = trigger_word
        self.is_listening = False

    def start_text_listener(self, callback: Callable[[str], None]):
        """Simulates a background listener for command input."""
        self.is_listening = True
        def listen():
            print(f"[WAKE] Listening for command (type '{self.trigger_word} ...')")
            while self.is_listening:
                user_input = input(">> ").strip().lower()
                if user_input.startswith(self.trigger_word):
                    command = user_input.replace(self.trigger_word, "").strip()
                    print(f"[WAKE] Activation detected: '{command}'")
                    callback(command)
                time.sleep(0.1)
        
        threading.Thread(target=listen, daemon=True).start()

    def start_voice_listener(self, callback: Callable[[str], None]):
        """
        Placeholder for Speech-to-Text integration.
        Would use SpeechRecognition or pvporcupine here.
        """
        print("[WAKE] Voice listener requires additional dependencies (PyAudio).")
        pass

    def stop(self):
        self.is_listening = False