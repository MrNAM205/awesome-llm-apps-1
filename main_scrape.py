# main_scrape.py
import sys
import json
from src.copilot_scraper import scrape_copilot_chat, scrape_all_chats

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python main_scrape.py <chat_url> <output.json>")
        print("  python main_scrape.py --all <output.json>")
        return

    if sys.argv[1] == "--all":
        output = sys.argv[2] if len(sys.argv) > 2 else "all_chats.json"
        scrape_all_chats(output)
        return

    url = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) > 2 else "output.json"
    messages = scrape_copilot_chat(url)

    with open(output, "w", encoding="utf-8") as f:
        json.dump(messages, f, indent=2, ensure_ascii=False)
    print(f"Saved to {output}")


if __name__ == "__main__":
    main()
