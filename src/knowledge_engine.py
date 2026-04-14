# src/knowledge_engine.py
import os
import json
import sqlite3
from pathlib import Path
from typing import List, Dict, Any

import faiss
import numpy as np

from .embedder import embed_text


class KnowledgeEngine:
    """
    OmniVerobrix Knowledge Engine
    --------------------------------
    - Stores chat messages in SQLite
    - Stores embeddings in FAISS
    - Supports semantic + keyword search
    - Supports ingestion of JSON chat files
    """

    def __init__(self, embed_fn, dim=768,
                 db_path="data/store.db",
                 faiss_index_path="data/faiss_index"):

        self.embed_fn = embed_fn
        self.dim = dim
        self.db_path = Path(db_path)
        self.faiss_path = Path(faiss_index_path)

        self._init_db()
        self._init_faiss()

    # ---------------------------------------------------------
    # Initialization
    # ---------------------------------------------------------

    def _init_db(self):
        self.db_path.parent.mkdir(exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_title TEXT,
                role TEXT,
                content TEXT,
                embedding BLOB
            )
        """)
        self.conn.commit()

    def _init_faiss(self):
        self.faiss_path.parent.mkdir(exist_ok=True)

        if self.faiss_path.exists():
            self.index = faiss.read_index(str(self.faiss_path))
        else:
            self.index = faiss.IndexFlatL2(self.dim)

    # ---------------------------------------------------------
    # Ingestion
    # ---------------------------------------------------------

    def ingest_folder(self, folder="incoming_chats"):
        folder = Path(folder)
        if not folder.exists():
            print(f"No folder found: {folder}")
            return

        for file in folder.glob("*.json"):
            self.ingest_chat_file(file)

        self._save_faiss()

    def ingest_chat_file(self, path: Path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"Failed to read {path}: {e}")
            return

        messages = data.get("messages", [])
        chat_title = path.stem

        for msg in messages:
            role = msg.get("role", "assistant")
            content = msg.get("content", "").strip()
            if not content:
                continue

            # Dedup check
            if self._is_duplicate(chat_title, content):
                continue

            emb = self.embed_fn(content)
            emb_bytes = np.asarray(emb, dtype=np.float32).tobytes()

            self.conn.execute(
                "INSERT INTO messages (chat_title, role, content, embedding) VALUES (?, ?, ?, ?)",
                (chat_title, role, content, emb_bytes)
            )
            self.index.add(np.array([emb], dtype=np.float32))

        self.conn.commit()

    def _is_duplicate(self, chat_title: str, content: str) -> bool:
        cur = self.conn.execute(
            "SELECT 1 FROM messages WHERE chat_title=? AND content=? LIMIT 1",
            (chat_title, content)
        )
        return cur.fetchone() is not None

    # ---------------------------------------------------------
    # Search
    # ---------------------------------------------------------

    def search(self, query: str, k=10) -> List[Dict[str, Any]]:
        query_emb = self.embed_fn(query)
        query_emb = np.array([query_emb], dtype=np.float32)

        if self.index.ntotal == 0:
            return []

        distances, indices = self.index.search(query_emb, k)

        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx < 0:
                continue

            row = self._fetch_message_by_index(idx)
            if row:
                row["score"] = float(dist)
                results.append(row)

        # Hybrid keyword boost
        for r in results:
            if query.lower() in r["content"].lower():
                r["score"] *= 0.5  # lower distance = better

        results.sort(key=lambda x: x["score"])
        return results

    def _fetch_message_by_index(self, idx: int):
        cur = self.conn.execute(
            "SELECT id, chat_title, role, content FROM messages ORDER BY id LIMIT 1 OFFSET ?",
            (idx,)
        )
        row = cur.fetchone()
        if not row:
            return None

        return {
            "id": row[0],
            "chat_title": row[1],
            "role": row[2],
            "content": row[3],
        }

    # ---------------------------------------------------------
    # Utility
    # ---------------------------------------------------------

    def list_chats(self) -> List[str]:
        cur = self.conn.execute("SELECT DISTINCT chat_title FROM messages ORDER BY chat_title")
        return [row[0] for row in cur.fetchall()]

    def _save_faiss(self):
        faiss.write_index(self.index, str(self.faiss_path))

    def close(self):
        self.conn.close()