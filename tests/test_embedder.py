import pytest
from src.embedder import chunk_and_embed

def test_chunk_and_embed():
    text = "This is a test sentence to be chunked and embedded."
    chunk_size = 10
    overlap = 2

    chunks = chunk_and_embed(text, chunk_size=chunk_size, overlap=overlap)

    assert isinstance(chunks, zip) or isinstance(chunks, list)
    chunks_list = list(chunks)
    assert len(chunks_list) > 0
    for chunk_text, embedding in chunks_list:
        assert isinstance(chunk_text, str)
        assert len(chunk_text) <= chunk_size

def test_chunk_and_embed_empty_text():
    text = ""
    chunk_size = 10
    overlap = 2

    chunks = chunk_and_embed(text, chunk_size=chunk_size, overlap=overlap)

    assert chunks == []

def test_chunk_and_embed_large_text():
    text = " ".join(["This is a test sentence."] * 100)
    chunk_size = 50
    overlap = 10

    chunks = chunk_and_embed(text, chunk_size=chunk_size, overlap=overlap)

    assert isinstance(chunks, zip) or isinstance(chunks, list)
    chunks_list = list(chunks)
    assert len(chunks_list) > 0
    for chunk_text, embedding in chunks_list:
        assert isinstance(chunk_text, str)
        assert len(chunk_text) <= chunk_size

def test_chunk_and_embed_invalid_chunk_size():
    text = "This is a test sentence."
    
    with pytest.raises(ValueError):
        chunk_and_embed(text, chunk_size=0, overlap=2)