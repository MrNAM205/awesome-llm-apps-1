import json
from pathlib import Path
from typing import List, Dict, Any
from src.store import ChatStore, VectorStore
from src.embedder import embed as embed_fn
from src.config import DIM, DATABASE_PATH, FAISS_INDEX_PATH
import numpy as np

INCOMING = Path("incoming_chats")

def load_chat_file(path: Path) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict) and "messages" in data:
        messages = data["messages"]
    elif isinstance(data, list):
        messages = data
    else:
        raise ValueError(f"Unrecognized chat format in {path}")

    normalized = []
    for m in messages:
        normalized.append({
            "role": m.get("role", "assistant"),
            "content": (m.get("content") or m.get("text") or "").strip()
        })

    return normalized

def ingest_all(chat_store: ChatStore, vector_store: VectorStore):
    INCOMING.mkdir(exist_ok=True)

    for file in INCOMING.glob("*.json"):
        print(f"Ingesting {file.name}...")

        try:
            messages = load_chat_file(file)
            chat_id = chat_store.save_chat(messages, title=file.stem)
            full_text = "\n".join([m["content"] for m in messages])

            embedding = embed_fn(full_text)
            embedding = np.array(embedding, dtype="float32")
            vector_store.add_embedding(embedding, text=full_text, id=chat_id)

            print(f"✓ Ingested {file.name} → chat_id={chat_id}")
        except Exception as e:
            print(f"× Failed {file.name}: {e}")

    print("All chats ingested.")

if __name__ == "__main__":
    c_store = ChatStore(DATABASE_PATH)
    v_store = VectorStore(DATABASE_PATH, FAISS_INDEX_PATH, DIM)
    ingest_all(c_store, v_store)
    c_store.close()
    v_store.close()