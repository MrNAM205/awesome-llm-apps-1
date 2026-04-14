import os
import sys

from module_migrator import migrate_modules
migrate_modules()

from shadow_cleaner import run_shadow_cleaner
run_shadow_cleaner()

print("""
===========================================
   OMNIVEROBRIX INTELLIGENCE COCKPIT v1.0
   Startup initialized — validating modules
===========================================
""")

from src.module_integrity import check_integrity
if not check_integrity():
    sys.exit(1)

import subprocess
from src.config import DIM, DATABASE_PATH, FAISS_INDEX_PATH
from src.knowledge_engine import KnowledgeEngine
from src.embedder import embed_text
from src.harvester import harvest_all_chats
from src.ingestion.segment_router import segment_and_route_all
from src.global_entity_map import build_global_entity_map
from src.timeline_reconstructor import build_timeline


def build_engine():
    return KnowledgeEngine(
        embed_fn=embed_text,
        dim=DIM,
        db_path=DATABASE_PATH,
        faiss_index_path=FAISS_INDEX_PATH,
    )


def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py --sync | --ingest | --query <text> | --list | --route")
        sys.exit(1)

    cmd = sys.argv[1]
    engine = build_engine()

    try:
        if cmd == "--sync":
            print("Step 0: Start Chrome with remote debugging:")
            print(r'& "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\ChromeDebug"')
            input("Press Enter once Copilot is open and logged in...")

            print("Step 1: Harvesting live Copilot chats...")
            harvest_all_chats()

            print("Step 2: Converting CSV history...")
            subprocess.run([sys.executable, "convert_copilot_history.py"], check=True)

            print("Step 2.5: Segmenting and routing chats...")
            segment_and_route_all()

            print("Step 3: Ingesting into Knowledge Engine...")
            engine.ingest_folder()

            print("Step 4: Building Global Entity Map...")
            graph_path = build_global_entity_map()
            print(f"Global Entity Map saved → {graph_path}")

            print("Step 5: Reconstructing Timeline...")
            timeline_path = build_timeline()
            print(f"Operational Timeline saved → {timeline_path}")

            print("Sync complete.")

        elif cmd == "--ingest":
            engine.ingest_folder()
            print("Ingest complete.")

        elif cmd == "--list":
            for chat in engine.list_chats():
                print(chat)

        elif cmd == "--route":
            segment_and_route_all()
            print("Routing complete.")

        elif cmd == "--query":
            query = " ".join(sys.argv[2:])
            results = engine.search(query)
            for r in results:
                print(r)

        else:
            print("Unknown command:", cmd)

    finally:
        engine.close()


if __name__ == "__main__":
    main()
