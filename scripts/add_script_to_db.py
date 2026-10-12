import argparse
import json
import os
import sys

# Ensure root directory is on sys.path so server module can be imported
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from server import ENGINE

sys.stdout.reconfigure(encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description="Add single or 6xN batch of Viral Hunted / Generated Reel scripts to data/scripts-db.json")
    parser.add_argument("--batch-json", default=None, help="Path to JSON file containing a list of 6xN scripts to auto-schedule across N days")
    parser.add_argument("--start-date", default=None, help="Start date YYYY-MM-DD for batch scheduling")

    parser.add_argument("--title", default=None, help="Short title of the script")
    parser.add_argument("--archetype", default="آرکتایپ ۱: آدمِ همیشه قوی و بی‌صدا خوب", help="Archetype name")
    parser.add_argument("--goal", default="جذب فالوور حداکثری (Follow Magnet)", help="Algorithmic goal")
    parser.add_argument("--content", default=None, help="Manual Content (inside reel lines)")
    parser.add_argument("--caption", default="", help="Companion caption")
    parser.add_argument("--score", type=int, default=99, help="Viral readiness score out of 100")
    parser.add_argument("--date", default=None, help="Target date YYYY-MM-DD")
    parser.add_argument("--slot", type=int, default=None, help="Target slot 1..6")

    # Viral Source Metadata Arguments
    parser.add_argument("--source-url", default="", help="Direct URL to the mother Instagram reel")
    parser.add_argument("--source-page", default="", help="Mother Instagram page handle (e.g. @page)")
    parser.add_argument("--source-views", default="", help="View count on the mother page (e.g. 850,000)")
    parser.add_argument("--extracted-raw-text", default="", help="Exact verbatim text extracted from inside the mother reel video")
    parser.add_argument("--extra-notes", default="", help="Extra notes about why this reel went viral / visual & audio notes")

    args = parser.parse_args()

    if args.batch_json:
        with open(args.batch_json, "r", encoding="utf-8") as f:
            items = json.load(f)
        created_list = ENGINE.batch_import_and_schedule(items, start_date=args.start_date)
        print(f"Batch imported and scheduled {len(created_list)} reels across {(len(created_list) + 5) // 6} days!")
        for c in created_list:
            print(f" - [{c['scheduled_date']} | Slot #{c['scheduled_slot']} ({c['recommended_time']})] {c['title']} (Source: {c.get('source_page', '—')} | Views: {c.get('source_views', '—')})")
        return

    if not args.content:
        raise SystemExit("Error: Either --batch-json or --content must be provided.")

    created = ENGINE.add_script({
        "title": args.title,
        "archetype": args.archetype,
        "goal": args.goal,
        "content": args.content.replace("\\n", "\n"),
        "caption": args.caption.replace("\\n", "\n"),
        "score": args.score,
        "scheduled_date": args.date,
        "scheduled_slot": args.slot,
        "source_url": args.source_url,
        "source_page": args.source_page,
        "source_views": args.source_views,
        "extracted_raw_text": args.extracted_raw_text.replace("\\n", "\n"),
        "extra_notes": args.extra_notes
    })
    print(
        f"Added script '{created['id']}' scheduled for {created['scheduled_date']} "
        f"at {created['recommended_time']} (Slot #{created['scheduled_slot']}) | Source: {created.get('source_url') or 'Generated'}"
    )


if __name__ == "__main__":
    main()
