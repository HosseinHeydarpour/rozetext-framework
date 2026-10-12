import json
import sys
sys.stdout.reconfigure(encoding='utf-8')
from server import ENGINE

new_item_dict = {
    "title": "وقتی عصبیم و سکوت میکنم یعنی از خودم میترسم (شکار ۱.۳ میلیونی)",
    "archetype": "آرکتایپ ۵: مانیفستِ اصالت، رفتاربینی و مرزگذاری",
    "goal": "ایجاد همذات‌پنداری عمیق، سیو در گالری و بازنشر استوری",
    "extracted_raw_text": """وقتی عصبیم و سکوت میکنم
یعنی از خودم میترسم نه از کسی دیگه..
چون میدونم اگه دهن باز کنم
حرفایی میزنم که دیگه هیچ پلی پشت سرم نمیمونه.
سکوت من از سر رضایت یا کم آوردن نیست؛
دارم به حرمت و احترامی فکر میکنم
که سال‌ها براش زحمت کشیدم.
پس از سکوتم سوءاستفاده نکنید
چون پشت این آرامش، یه طوفان خاموشه..""",
    "content": """وقتی عصبیم و سکوت میکنم
یعنی از خودم میترسم نه از کسی دیگه..
چون میدونم اگه دهن باز کنم
حرفایی میزنم که دیگه هیچ پلی پشت سرم نمیمونه.
سکوت من از سر رضایت یا کم آوردن نیست؛
دارم به حرمت و احترامی فکر میکنم
که سال‌ها براش زحمت کشیدم.
پس از سکوتم سوءاستفاده نکنید
چون پشت این آرامش، یه طوفان خاموشه..""",
    "caption": """سکوتِ آدم‌های صبور علامتِ رضایت یا ضعف نیست؛ دارن حرمت‌ها رو نگه می‌دارن تا پلی خراب نشه... 🌪️ شما وقتِ عصبانیت سکوت می‌کنید یا حرف می‌زنید؟""",
    "score": 98,
    "score_breakdown": {
        "persona_fit": 20,
        "hook_power": 20,
        "pacing_watchtime": 19,
        "micdrop_saveability": 20,
        "share_trigger": 19
    },
    "persona_fit_reason": "بیان باوقار مرزهای روانی و هشدار نجیبانه درباره عواقب شکستن حرمت‌ها با ۱.۳ میلیون بازدید.",
    "source_url": "https://www.instagram.com/reel/DZQJRhRNpQG/",
    "source_page": "@vahidrezakhoshbayan",
    "source_views": "1,300,000 بازدید (1.3M — ۵۳ هزار لایک)",
    "extra_notes": "۹ سطر صریح و باوقار درباره قدرت سکوت و مرزهای روانی.",
    "scheduled_date": "2026-10-04",
    "scheduled_slot": 5,
    "is_viral_hunted": True
}

# 1. Update scripts-db.json
with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

# Unschedule old published post from Slot 5 of today
for s in db['scripts']:
    if s['id'] == 'script-1791049792917-039':
        s['scheduled_slot'] = None
        s['scheduled_date'] = '2026-09-27'  # Past archive date
        print("Archived old published script #274 away from 2026-10-04 Slot 5.")

with open('data/scripts-db.json', 'w', encoding='utf-8') as f:
    json.dump(db, f, indent=2, ensure_ascii=False)

# Add new script using ENGINE
created = ENGINE.add_script(new_item_dict)
print(f"Added new script {created['id']} to {created['scheduled_date']} Slot #{created['scheduled_slot']} ({created['recommended_time']})!")

# 2. Update data/hunted-42-reels-batch-verified.json
with open('data/hunted-42-reels-batch-verified.json', 'r', encoding='utf-8') as f:
    batch = json.load(f)

for idx, b in enumerate(batch):
    if b.get('source_url') == 'https://www.instagram.com/reel/DQXIpOODXBt/':
        batch[idx] = new_item_dict
        print(f"Replaced DQXIpOODXBt in batch at index {idx}!")

with open('data/hunted-42-reels-batch-verified.json', 'w', encoding='utf-8') as f:
    json.dump(batch, f, indent=2, ensure_ascii=False)

print("Replacement complete successfully!")
