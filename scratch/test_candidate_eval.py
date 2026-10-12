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

def evaluate_candidate(code, url, page, views, text):
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    line_count = len(lines)
    
    res_hist = ENGINE.check_duplicate_against_history(lines[0] if lines else '', text)
    
    c_tokens = ENGINE._normalize_persian_tokens(text)
    c_ngrams = ENGINE._extract_ngrams(text, 4)
    db_dup = False
    closest_db = None
    for s_id, s_title, s_date, s_slot, s_txt in existing_db_texts:
        s_tokens = ENGINE._normalize_persian_tokens(s_txt)
        overlap = len(c_tokens & s_tokens) / max(1, min(len(c_tokens), len(s_tokens)))
        s_ngrams = ENGINE._extract_ngrams(s_txt, 4)
        common_ngrams = c_ngrams & s_ngrams
        if len(common_ngrams) >= 2 or overlap >= 0.40:
            db_dup = True
            closest_db = f"{s_id} ({s_date} slot {s_slot}): {s_title}"
            break
            
    bad_words = ['مولانا', 'شمس تبریزی', 'شمس', 'دختر', 'پسر', 'تولد', 'روز زن', 'روز مادر', 'روز پدر', 'یلدا', 'نوروز']
    bad_persona = any(bw in text for bw in bad_words) or '@halekhoub' in page
    
    print(f"=== Candidate: [{code}] ===")
    print(f"URL: {url}")
    print(f"Page: {page} | Views: {views} | Lines: {line_count}")
    print(f"History Dup: {res_hist['is_duplicate']} (sim={res_hist['similarity_score']:.1f}%) | Closest: {res_hist.get('duplicate_of_reel')}")
    print(f"DB Dup: {db_dup} | Closest: {closest_db}")
    print(f"Bad Persona: {bad_persona}")
    
    is_valid = (7 <= line_count <= 16) and not res_hist['is_duplicate'] and not db_dup and not bad_persona
    print(f"OVERALL RESULT: {'>>> VERIFIED PASSED <<<' if is_valid else 'FAILED'}")
    print("-" * 50)
    return is_valid

# Test C5WPI8OCK4x
evaluate_candidate(
    code='C5WPI8OCK4x',
    url='https://www.instagram.com/reel/C5WPI8OCK4x/',
    page='@heliumm.__',
    views='1,400,000+ ویو (1.4M)',
    text='''از یه سنی به بعد وقتی یکی از چشمت میوفته
دیگه نه قهر میکنی باهاش
نه بلاکش میکنی
نه رد تماس میدی..
شاید باهاش سلام احوال پرسی هم بکنی
ولی اون آدم ، دیگه برات اون جایگاه سابقش و نداره
و میشه یکی مثل بقیه
هرچقدر هم بالا بره پایین بیاد
دیگه برات تموم شده...'''
)
