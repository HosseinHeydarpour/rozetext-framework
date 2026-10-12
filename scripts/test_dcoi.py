import sys, os, json
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from server import ENGINE
db = json.load(open('data/scripts-db.json', encoding='utf-8'))

txt = """یه زمانی فکر میکردم اگه برای آدم‌ها خوب باشی،
اونا هم باهات خوب میمونن.
اگه هوای دلشون رو داشته باشی،
یه روزی هوای دلت رو دارن.
اگر پشتشون باشی،پشتت می‌ایستن.
اما زندگی یه چیز دیگه یادم داد.
اینکه بعضی آدم‌ها خوبی رو نمیفهمن، بهش عادت میکنن.
تا وقتی هستی، بودنت براشون عادیه.
تا وقتی میبخشی، فکر میکنن وظیفته.
تا وقتی میمونی، خیال میکنن هیچوقت نمیری.
تا اینکه یه روز تصمیم میگیری دیگه مثل قبل نباشی.
اون موقع تازه میفهمن چی رو از دست دادن.
و دیگه برای جبران دیر شده..."""

hist = ENGINE.check_duplicate_against_history(txt, txt)
print(f"Hist result: is_dup={hist['is_duplicate']} {hist['similarity_score']}% | {hist['history_check_badge']}")

c_tokens = ENGINE._normalize_persian_tokens(txt)
c_ngrams = ENGINE._extract_ngrams(txt, 4)
max_dbsim = 0
closest_script = None
common_ngrams_found = set()

for s in db['scripts']:
    st = (s.get('content') or '') + ' ' + (s.get('extracted_raw_text') or '')
    st_tokens = ENGINE._normalize_persian_tokens(st)
    st_ngrams = ENGINE._extract_ngrams(st, 4)
    if not st_tokens: continue
    sim = len(c_tokens & st_tokens) / max(1, min(len(c_tokens), len(st_tokens)))
    ng_match = c_ngrams & st_ngrams
    if sim > max_dbsim:
        max_dbsim = sim
        closest_script = s.get('id')
        common_ngrams_found = ng_match

print(f"DB Sim: {max_dbsim:.1%} (closest={closest_script}) | common_ngrams={len(common_ngrams_found)}")
is_clean = (not hist['is_duplicate']) and (max_dbsim < 0.40) and (len(common_ngrams_found) < 2)
print("CLEAN PASS!" if is_clean else "FAIL DUP!")
