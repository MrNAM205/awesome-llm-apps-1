from sentence_transformers import SentenceTransformer
import numpy as np

# Load model once (cached globally)
_model = None

def _load_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    return _model

def embed_text(text: str):
    """
    Returns a 384‑dimensional embedding for the given text.
    Output is a numpy array of floats (FAISS‑compatible).
    """
    model = _load_model()
    # Ensure we return a single vector even if encode expects a list
    emb = model.encode([text], convert_to_numpy=True)[0]
    return emb.astype(np.float32)