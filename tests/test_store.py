import os
import pytest
import numpy as np
import faiss
import sqlite3
from src.store import VectorStore

@pytest.fixture
def setup_database(tmp_path):
    db_path = tmp_path / 'store.db'
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS embeddings (id INTEGER PRIMARY KEY, vector BLOB)')
    conn.commit()
    yield conn
    conn.close()

@pytest.fixture
def setup_faiss_index(tmp_path):
    index_path = tmp_path / 'faiss_index'
    index_path.mkdir()
    index_file = index_path / 'index.faiss'
    index = faiss.IndexFlatL2(384)  # Assuming 384-dimensional embeddings
    faiss.write_index(index, str(index_file))
    yield str(index_file)

def test_add_embedding(tmp_path, setup_database, setup_faiss_index):
    db_path = tmp_path / 'store.db'
    index_path = tmp_path / 'faiss_index' / 'index.faiss'
    store = VectorStore(str(db_path), str(index_path), 384)
    vector = np.random.rand(384).astype('float32')
    store.add_embedding(vector)
    
    cursor = setup_database.cursor()
    cursor.execute('SELECT COUNT(*) FROM embeddings')
    count = cursor.fetchone()[0]
    assert count == 1

def test_dimension_validation(tmp_path, setup_database, setup_faiss_index):
    db_path = tmp_path / 'store.db'
    index_path = tmp_path / 'faiss_index' / 'index.faiss'
    store = VectorStore(str(db_path), str(index_path), 384)
    vector = np.random.rand(384).astype('float32')
    store.add_embedding(vector)
    
    with pytest.raises(ValueError):
        store.add_embedding(np.random.rand(300).astype('float32'))  # Wrong dimension

def test_atomic_index_replacement(tmp_path, setup_database, setup_faiss_index):
    db_path = tmp_path / 'store.db'
    index_path = tmp_path / 'faiss_index' / 'index.faiss'
    store = VectorStore(str(db_path), str(index_path), 384)
    vector1 = np.random.rand(384).astype('float32')
    vector2 = np.random.rand(384).astype('float32')
    
    store.add_embedding(vector1)
    # Check that index file exists and is valid
    assert os.path.exists(str(index_path))
    index = faiss.read_index(str(index_path))
    assert index.ntotal == 1
    
    store.add_embedding(vector2)
    index = faiss.read_index(str(index_path))
    assert index.ntotal == 2