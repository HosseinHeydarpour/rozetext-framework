import sys, os, json
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath('.'))
from server import ENGINE

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

existing_db_texts = []
for s in db.get('scripts', []):
    txt = (s.get('content') or '') + ' ' + (s.get('extracted_raw_text') or '')
    if txt.strip():
        existing_db_texts.append((s.get('id'), s.get('title'), s.get('scheduled_date'), s.get('scheduled_slot'), txt.strip()))

text_avaye = """« خیلی از ما »
ن تو خونه پدری روز خوش دیدیم
نه تو خونه بخت خوشبخت شدیم،
ولی اگه...
تو خانواده آدم رو دوست داشته باشن؛
محبت کنن؛
کاری نکنن که آدم احساس سرباری کنه؛
شاید بشه
خونه بخت خوشبخت شد
راسته که میگن: آدم اگه خونه پدر شانس نداشته باشه
خونه بخت هم شانس نمیاره
یعنی این بود زندگی....
این بود جوونی....
همش با سختی...
هیچ و پوچ تموم شد رفت
بدون این که به کوچیکترین آرزومون برسیم......"""

lines = [l.strip() for l in text_avaye.splitlines() if l.strip()]
print(f"Lines count: {len(lines)}")
res_hist = ENGINE.check_duplicate_against_history(text_avaye, text_avaye)
print("History check:", res_hist)

c_tokens = ENGINE._normalize_persian_tokens(text_avaye)
c_ngrams = ENGINE._extract_ngrams(text_avaye, 4)
db_dup = False
for s_id, s_title, s_date, s_slot, s_txt in existing_db_texts:
    s_tokens = ENGINE._normalize_persian_tokens(s_txt)
    overlap = len(c_tokens & s_tokens) / max(1, min(len(c_tokens), len(s_tokens)))
    s_ngrams = ENGINE._extract_ngrams(s_txt, 4)
    common_ngrams = c_ngrams & s_ngrams
    if len(common_ngrams) >= 2 or overlap >= 0.40:
        db_dup = True
        print(f"DB Dup with {s_id} ({s_date}): {s_title}")
        break

if not db_dup and not res_hist['is_duplicate']:
    print(">>> SUCCESS: DaYpUkIIdSr IS 100% CLEAN AND VERIFIED! <<<")
