from typing import List, Tuple, Dict, Any, Optional
import os
import sqlite3
import faiss
import numpy as np
from pathlib import Path
import time
import json

class VectorStore:
    def __init__(self, db_path: str, index_path: str, dim: int):
        self.db_path = db_path
        self.index_path = index_path
        self.dim = dim
        self.index = self.load_index()
        self.conn = sqlite3.connect(self.db_path)
        self.create_table()

    def create_table(self):
        self.conn.execute('CREATE TABLE IF NOT EXISTS embeddings (id INTEGER PRIMARY KEY, vector BLOB, text TEXT)')
        self.conn.commit()

    def add_embedding(self, embedding: np.ndarray, text: str = "", id: int = None):
        self.validate_embedding(embedding)
        vector_blob = embedding.tobytes()
        if id is None:
            self.conn.execute('INSERT INTO embeddings (vector, text) VALUES (?, ?)', (vector_blob, text))
        else:
            self.conn.execute('INSERT OR REPLACE INTO embeddings (id, vector, text) VALUES (?, ?, ?)', (id, vector_blob, text))
        self.conn.commit()
        self.index.add(np.array([embedding]).astype('float32'))
        self.save_index()

    def load_index(self):
        if os.path.exists(self.index_path):
            return faiss.read_index(self.index_path)
        else:
            return faiss.IndexFlatL2(self.dim)

    def validate_embedding(self, embedding: np.ndarray):
        if embedding.shape != (self.dim,):
            raise ValueError(f"Embedding must have shape ({self.dim},)")

    def add_to_index(self, embeddings: List[np.ndarray], ids: List[int]):
        for embedding in embeddings:
            self.validate_embedding(embedding)
        self.index.add(np.array(embeddings).astype('float32'))
        self.save_index()

    def save_index(self):
        temp_path = f"{self.index_path}.tmp"
        try:
            faiss.write_index(self.index, temp_path)
            os.replace(temp_path, self.index_path)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def query(self, query_embedding: np.ndarray, k: int) -> List[Tuple[int, float]]:
        self.validate_embedding(query_embedding)
        distances, indices = self.index.search(np.array([query_embedding]).astype('float32'), k)
        return list(zip(indices[0], distances[0]))

    def get_text(self, id: int) -> str:
        cursor = self.conn.execute('SELECT text FROM embeddings WHERE id = ?', (id,))
        row = cursor.fetchone()
        return row[0] if row else ""

    def rebuild_index(self):
        cursor = self.conn.execute('SELECT id, vector FROM embeddings')
        rows = cursor.fetchall()
        if not rows:
            self.index = faiss.IndexFlatL2(self.dim)
            return
        expected_bytes = self.dim * np.dtype("float32").itemsize
        embeddings = np.zeros((len(rows), self.dim), dtype="float32")
        ids = []
        for i, (row_id, blob) in enumerate(rows):
            if len(blob) != expected_bytes:
                raise ValueError(f"ID {row_id}: Expected {expected_bytes} bytes, got {len(blob)}")
            embeddings[i] = np.frombuffer(blob, dtype="float32")
            ids.append(row_id)
        self.index = faiss.IndexFlatL2(self.dim)
        self.index.add(embeddings)
        self.save_index()

    def close(self):
        self.conn.close()

class ChatStore:
    def __init__(self, db_path: str):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS chats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                created_at REAL
            )
        """)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER,
                role TEXT,
                content TEXT,
                position INTEGER,
                FOREIGN KEY(chat_id) REFERENCES chats(id)
            )
        """)
        self.conn.commit()

    def save_chat(self, messages: List[Dict[str, Any]], title: Optional[str] = None) -> int:
        created_at = time.time()
        cursor = self.conn.execute(
            "INSERT INTO chats (title, created_at) VALUES (?, ?)",
            (title, created_at)
        )
        chat_id = cursor.lastrowid

        for i, msg in enumerate(messages):
            self.conn.execute(
                "INSERT INTO messages (chat_id, role, content, position) VALUES (?, ?, ?, ?)",
                (chat_id, msg.get("role", "assistant"), msg.get("content") or msg.get("text") or "", i)
            )

        self.conn.commit()
        return chat_id

    def get_chat(self, chat_id: int) -> List[Dict[str, Any]]:
        cursor = self.conn.execute(
            "SELECT role, content FROM messages WHERE chat_id = ? ORDER BY position ASC",
            (chat_id,)
        )
        return [dict(row) for row in cursor.fetchall()]

    def list_chats(self) -> List[Dict[str, Any]]:
        cursor = self.conn.execute(
            "SELECT id, title, created_at FROM chats ORDER BY created_at DESC"
        )
        return [dict(row) for row in cursor.fetchall()]

    def export_chat(self, chat_id: int, path: str):
        messages = self.get_chat(chat_id)
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"messages": messages}, f, indent=2, ensure_ascii=False)

    def delete_chat(self, chat_id: int):
        self.conn.execute("DELETE FROM messages WHERE chat_id = ?", (chat_id,))
        self.conn.execute("DELETE FROM chats WHERE id = ?", (chat_id,))
        self.conn.commit()

    def close(self):
        self.conn.close()