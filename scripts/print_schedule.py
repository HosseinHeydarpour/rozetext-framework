import json, sys
sys.stdout.reconfigure(encoding='utf-8')
with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)
scripts = [s for s in db.get('scripts', []) if s.get('scheduled_date') in ['2026-10-11', '2026-10-12']]
scripts.sort(key=lambda x: (x.get('scheduled_date', ''), x.get('scheduled_slot', 0)))

print(f"Total scheduled for 2026-10-11 and 2026-10-12: {len(scripts)}")
for s in scripts:
    print('================================================================================')
    print(f"[{s.get('scheduled_date')} | اسلات #{s.get('scheduled_slot')} | ساعت {s.get('recommended_time')}] {s.get('title')}")
    print(f"آرکتایپ: {s.get('archetype')} | هدف: {s.get('goal')}")
    print(f"مرجع: {s.get('source_page')} ({s.get('source_views')}) | لینک: {s.get('source_url')}")
    print(f"امتیاز وایرال: {s.get('score')}/100")
    print('متن کامل روی ویدیو (Direct Raw-Text):')
    print(s.get('content'))
    print('کپشن پیشنهادی:')
    print(s.get('caption'))
