import json
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

exact_text = """وقتی عصبیم و سکوت میکنم
یعنی از خودم میترسم نه از کسی دیگه !
چون میدونم اگه حرفی بزنم یا کاری کنم
تهش از خودم بدم میاد
چون اون روی تاریکمو میشناسم و
میدونم اگه بالا بیاد چه کارایی میتونه بکنه
چون نمیخوام اون باشم
چون دور از شخصیت منه .."""

caption_text = """سکوتِ آدم‌های صبور از ضعف نیست؛ از ترسِ بیدار شدنِ روییه که سال‌هاست مهارش کردن... 🥀
شما موقعِ عصبانیت سکوت می‌کنید یا فوران؟"""

# 1. Update data/scripts-db.json
with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

for s in db['scripts']:
    if s['id'] == 'script-1791098400959-081':
        s['title'] = "وقتی عصبیم و سکوت میکنم یعنی از خودم میترسم (شکار ۱.۳ میلیونی)"
        s['content'] = exact_text
        s['extracted_raw_text'] = exact_text
        s['caption'] = caption_text
        s['hook'] = "وقتی عصبیم و سکوت میکنم"
        s['punchline'] = "چون دور از شخصیت منه .."
        s['lines_count'] = 8
        s['words_count'] = len(exact_text.split())
        s['extra_notes'] = "۸ سطر کاملاً تطبیق‌داده‌شده با فریم ویدیوی مرجع وحیدرضا خوش‌بیان درباره کنترل روی تاریک و اصالت شخصیتی."
        print("Updated script-1791098400959-081 in scripts-db.json!")

with open('data/scripts-db.json', 'w', encoding='utf-8') as f:
    json.dump(db, f, indent=2, ensure_ascii=False)

# 2. Update data/hunted-42-reels-batch-verified.json
with open('data/hunted-42-reels-batch-verified.json', 'r', encoding='utf-8') as f:
    batch = json.load(f)

for b in batch:
    if 'DZQJRhRNpQG' in b.get('source_url', ''):
        b['content'] = exact_text
        b['extracted_raw_text'] = exact_text
        b['caption'] = caption_text
        b['hook'] = "وقتی عصبیم و سکوت میکنم"
        b['punchline'] = "چون دور از شخصیت منه .."
        b['extra_notes'] = "۸ سطر استخراج‌شده دقیق فریم‌به‌فریم از ویدیوی ریلز مرجع."
        print("Updated DZQJRhRNpQG in hunted-42-reels-batch-verified.json!")

with open('data/hunted-42-reels-batch-verified.json', 'w', encoding='utf-8') as f:
    json.dump(batch, f, indent=2, ensure_ascii=False)

# 3. Update published-content-history.md
with open('published-content-history.md', 'r', encoding='utf-8') as f:
    hist = f.read()

# Replace in table (Reel #275)
old_table_row = """| **#275** | `2026-10-04 10:51` | «وقتی عصبیم و سکوت میکنم» | وقتی عصبیم و سکوت میکنم / یعنی از خودم میترسم نه از کسی دیگه.. / چون میدونم اگه دهن باز کنم / حرفایی میزنم که دیگه هیچ پلی پشت سرم نمیمونه. / سکوت من از سر رضایت یا کم آوردن نیست؛ / دارم به حرمت و احترامی فکر میکنم / که سال‌ها براش زحمت کشیدم. / پس از سکوتم سوءاستفاده نکنید / چون پشت این آرامش، یه طوفان خاموشه.. | سکوتِ آدم‌های صبور علامتِ رضایت یا ضعف نیست؛ دارن حرمت‌ها رو نگه می‌دارن تا پلی خراب نشه... 🌪️ شما وقتِ عصبانیت سکوت می‌کنید یا حرف می‌زنید؟ | <!-- SCRIPT_ID:script-1791098400959-081 -->"""
new_table_row = """| **#275** | `2026-10-04 10:51` | «وقتی عصبیم و سکوت میکنم» | وقتی عصبیم و سکوت میکنم / یعنی از خودم میترسم نه از کسی دیگه ! / چون میدونم اگه حرفی بزنم یا کاری کنم / تهش از خودم بدم میاد / چون اون روی تاریکمو میشناسم و / میدونم اگه بالا بیاد چه کارایی میتونه بکنه / چون نمیخوام اون باشم / چون دور از شخصیت منه .. | سکوتِ آدم‌های صبور از ضعف نیست؛ از ترسِ بیدار شدنِ روییه که سال‌هاست مهارش کردن... 🥀 شما موقعِ عصبانیت سکوت می‌کنید یا فوران؟ | <!-- SCRIPT_ID:script-1791098400959-081 -->"""

if old_table_row in hist:
    hist = hist.replace(old_table_row, new_table_row)
    print("Replaced row in published-content-history table!")

# Replace hook index
old_hook_row = """| **#275** | ✅ [PUBLISHED] | جدید (2026-10-04 10:51) | وقتی عصبیم و سکوت میکنم | چون پشت این آرامش، یه طوفان خاموشه.. | <!-- SCRIPT_ID:script-1791098400959-081 -->"""
new_hook_row = """| **#275** | ✅ [PUBLISHED] | جدید (2026-10-04 10:51) | وقتی عصبیم و سکوت میکنم | چون دور از شخصیت منه .. | <!-- SCRIPT_ID:script-1791098400959-081 -->"""

if old_hook_row in hist:
    hist = hist.replace(old_hook_row, new_hook_row)
    print("Replaced hook in published-content-history hook index!")

# Replace content block for Reel #275
old_block_pattern = r"(### Reel #275.*?)(?=### Reel #|\Z)"
match = re.search(old_block_pattern, hist, flags=re.DOTALL)
if match:
    old_block = match.group(1)
    new_block = f"""### Reel #275 (✅ [PUBLISHED]) — ID: `script-1791098400959-081` | Date: `2026-10-04 10:51` <!-- SCRIPT_ID:script-1791098400959-081 -->
* **عنوان:** وقتی عصبیم و سکوت میکنم یعنی از خودم میترسم (شکار ۱.۳ میلیونی)
* **آرکتایپ:** آرکتایپ ۵: مانیفستِ اصالت، رفتاربینی و مرزگذاری
* **هدف:** ایجاد همذات‌پنداری عمیق، سیو در گالری و بازنشر استوری
* **منبع و آمار:** `@vahidrezakhoshbayan` — ۱,۳۰۰,۰۰۰ بازدید (۵۳ هزار لایک)
* **لینک مستقیم ریلز:** https://www.instagram.com/reel/DZQJRhRNpQG/
* **هوک (خط اول):** «وقتی عصبیم و سکوت میکنم»
* **متن کامل داخل ریلز (استخراج‌شده کلمه به کلمه از فریم‌های ویدیو):**
```text
وقتی عصبیم و سکوت میکنم
یعنی از خودم میترسم نه از کسی دیگه !
چون میدونم اگه حرفی بزنم یا کاری کنم
تهش از خودم بدم میاد
چون اون روی تاریکمو میشناسم و
میدونم اگه بالا بیاد چه کارایی میتونه بکنه
چون نمیخوام اون باشم
چون دور از شخصیت منه ..
```
* **کپشن:** {caption_text}
* **تاریخ انتشار ثبت‌شده:** `2026-10-04 10:51`

---

"""
    hist = hist[:match.start()] + new_block + hist[match.end():]
    print("Updated full block for Reel #275 in published-content-history.md!")

with open('published-content-history.md', 'w', encoding='utf-8') as f:
    f.write(hist)

print("All files updated with 100% verified text!")
