import json
import sys
sys.path.insert(0, ".")
from server import PublisherEngine

sys.stdout.reconfigure(encoding="utf-8")

engine = PublisherEngine()

with open("C:/Users/User/.gemini/antigravity/brain/3235565d-9c9f-4548-8b04-ad573c2c10ba/.system_generated/steps/285/output.txt", "r", encoding="utf-8") as f:
    text = f.read()

start = text.find('[{"id":')
end_idx = text.rfind('}]') + 2
items = json.loads(text[start:end_idx])

# Also add the one from yeharf (DdPDb35qWnW - 1.6M)
items.append({
    "id": "DdPDb35qWnW",
    "url": "https://www.instagram.com/reel/DdPDb35qWnW/",
    "views": "1.6M",
    "text": "یه زمانی فکر می‌کردم.. هر چی بیشتر خوبی کنم، بیشتر قدرم رو می‌دونن؛ اما فهمیدم بعضیا خوبی رو محبت نمی‌دونن، وظیفه میدونن. از امروز نه دنبال تایید کسی‌ام، نه برای موندن کسی خودمو تغییر میدم. هر کس ارزشم رو فهمید، خوش اومد؛ هر کس نفهمید، راهش از من جداست. یاد گرفتم آرامشم رو به هیچکس قرض ندم؛ چون حال خوبم از هر رابطه‌ای با ارزش تره 🌱"
})

print(f"Total candidates: {len(items)}")

non_duplicates = []
duplicates = []

for it in items:
    txt = it.get("text", "")
    res = engine.check_duplicate_against_history(txt, txt)
    if res["is_duplicate"]:
        duplicates.append((it["id"], it["views"], res["duplicate_of_reel"], res["matched_hook"]))
    else:
        non_duplicates.append(it)

print(f"Duplicates found against 269 published reels: {len(duplicates)}")
for d in duplicates:
    print(f" - {d[0]} ({d[1]}): dup of {d[2]} ({d[3]})")

print(f"\nNon-duplicate candidates available: {len(non_duplicates)}")
for i, nd in enumerate(non_duplicates):
    print(f"{i+1}. [{nd['views']}] {nd['id']} | {nd['text'][:60]}...")
