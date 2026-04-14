from fastapi import APIRouter, Request
from typing import List, Dict, Any
import subprocess
import sys
from src.harvester import harvest_all_chats
from knowledge_engine import KnowledgeEngine
from src.embedder import embed
from src.config import DIM, DATABASE_PATH, FAISS_INDEX_PATH

router = APIRouter()

@router.get("/timeline")
async def get_timeline(request: Request) -> Dict[str, List[Dict[str, Any]]]:
    """Fetches all chats from the KnowledgeEngine for the navigation spine."""
    # Access the shared engine instance from app state
    engine = request.app.state.engine
    chats = engine.list_chats()
    return {"chats": chats}

@router.post("/harvest")
async def harvest_now(request: Request):
    """Triggers the authoritative Harvest -> Convert -> Ingest pipeline."""
    harvest_all_chats()
    subprocess.run([sys.executable, "convert_copilot_history.py"], check=True)
    
    engine = request.app.state.engine
    engine.ingest_folder()
    return {"status": "success"}