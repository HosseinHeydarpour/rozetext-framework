import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

with open("data/scripts-db.json", "r", encoding="utf-8") as f:
    db = json.load(f)

scripts = sorted(db["scripts"], key=lambda s: (s["scheduled_date"], s["scheduled_slot"]))

current_date = None
for s in scripts:
    d = s["scheduled_date"]
    if d != current_date:
        current_date = d
        print(f"\n=======================================================")
        print(f"📅 تاریخ: {current_date} ({s.get('weekday_fa', '')})")
        print(f"=======================================================")
    print(f"\n🔹 اسلات {s['scheduled_slot']} ({s['recommended_time']}) | {s['title']}")
    print(f"   • کهن‌الگو: {s.get('archetype', '')}")
    print(f"   • پیج مرجع: {s.get('source_page', '')} | بازدید دقیق: {s.get('source_views', '')}")
    print(f"   • لینک ریلز: {s.get('source_url', '')}")
    print(f"   • امتیاز وایرال: {s.get('score', 0)}/100")
    print(f"   • هوک: {s.get('hook', '')}")
    print(f"   • ضربه نهایی: {s.get('punchline', '')}")
