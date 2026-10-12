import sys, os, json
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from server import ENGINE

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

test_cands = [
    {
        'id': 'DbGUEgZsr6E',
        'page': '@text.love400',
        'views': '5,300,000 بازدید (5.3M — ۱۲۳ هزار لایک)',
        'url': 'https://www.instagram.com/reel/DbGUEgZsr6E/',
        'text': """خطاب به بعضی دوست، آشنا و فامیلا؛
من بد نشدم من فقط فهمیدم
دورو برم چخبره،
دیدم و فهمیدم هر کسی چقدر
به فکر منفعت خودشه
شنیدم پشت سرم چی میگین
یاد گرفتم به هر کسی چه اندازه بها بدم،
نگین فلانی بد شده، نگین چقد عوض شده،
به خودتون بگین من چیکار کردم
که یه آدم دیگه شده...!"""
    },
    {
        'id': 'DZF2fkKtqE6',
        'page': '@heliumm.__',
        'views': '1,800,000 بازدید (1.8M — ۲۴ هزار لایک)',
        'url': 'https://www.instagram.com/reel/DZF2fkKtqE6/',
        'text': """واقعیت اینه :
واقعیت اینه که من از این آدم همیشگی نیستم ؛
خیلی چیزا ازم کم شده...
اعتمادم ، شورم ، حرف زدنم ، حتی خندیدنم ؛
اونها فکر میکنن خوبم چون چیزی نمیگم ،
اما نمیدونن چقدر شب‌ها با خودم جنگیدم که صبح دوباره
آدم معمولی باشم...
گاهی دلم میخواد یکی بیاد که بدون سوال ، بدون قضاوت
فقط بفهمه ، تلخی همه کسایی که من پشت این سردی ،
به دنیا دلتنگم و خستگی و حرف‌های نگفته پنهان کردم..."""
    },
    {
        'id': 'DZas23KNtjL',
        'page': '@heliumm.__',
        'views': '1,000,000 بازدید (1.0M — ۲۰ هزار لایک)',
        'url': 'https://www.instagram.com/reel/DZas23KNtjL/',
        'text': """این پست و برات میفرستم لطفا کامل بخون و
سیوش کن...
اگه یه روزی دیگه تو این دنیا نبودم دوباره ببینش و
به یادم بیوفت...
خواستم بگم مرسی که کنارم بودی...
مرسی که هوامو داشتی...
تو آدم مورد علاقه‌ی من تو این دنیا بودی اگه یه وقتایی
ناراحتت کردم ببخشید...
درسته الان کنارت نیستم ولی دارم نگات میکنم حواسم
بهت هست :)
نبینم ناراحت باشیا...
خیلی دوست دارم ❤️
تو همون آدمی بودی که حتی ۷ دقیقه بعد از مرگم
مغزم بهت فکر میکرد :)"""
    }
]

for c in test_cands:
    txt = c['text']
    lines = [l.strip() for l in txt.splitlines() if l.strip()]
    hist = ENGINE.check_duplicate_against_history(txt, txt)
    
    # DB check
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
            
    is_clean = (not hist['is_duplicate']) and (max_dbsim < 0.40) and (len(common_ngrams_found) < 2)
    status = "CLEAN PASS" if is_clean else "FAIL DUP"
    print(f"[{c['id']}] {c['views']} | Lines: {len(lines)} | {status}")
    print(f"  Hist: {hist['similarity_score']:.1f}% (dup={hist['is_duplicate']}) | DB: {max_dbsim:.1%} (closest={closest_script})")
    if not is_clean:
        print(f"  Reason: hist_dup={hist['is_duplicate']}, common_ngrams={len(common_ngrams_found)}")
    print()
