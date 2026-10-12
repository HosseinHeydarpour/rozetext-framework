import sys, os, json, re
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from server import ENGINE

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

candidates = {
    'DKC2DqwiyM_': '''ما که هرچی آدم درست و حسابی و اصیل دیدیم،
از رفتارش فهمیدیم نه ادعا و حرفاش
آدمایی که لازم نیست خودشونو توضیح بدن
و خوب بودنشون خودش همه چی رو میرسونه .
نه دنبال تاییدن، نه دنبال جلب توجه.
کارشونو میکنن حرفشونو نمیزنن،
اصلاً اصالت یه چیزیه که
توی رفتار و عمل طرف معلوم میشه
نه از رو حرف و ادعا و شعار ...''',

    'DJeyrN9oAxI': '''راستش اولویت‌هام عوض شده،
الان آرامش روح و روانم برام از هر چیزی مهم‌تره،
دیگه نمیتونم مثل قبل الکی مدارا کنم،
هیچی نگم، عکس‌العمل نشون ندم،
یا بگم بیخیال و هر کاری خواست بکنه
الان اگه فقط ذره‌ای حس کنم
جایی داره بهم آسیب میزنه اونجا رو ترک می‌کنم و
اگه کسی باعثش باشه،
با احترام برای همیشه ازش فاصله میگیرم ...''',

    'DMVWoiaor6o': '''اینو از ته دل میگم که
هرجایی بهتر از بودن کنار من بود برین
هرجا بیشتر بهتون خوش میگذشت برین
هرجایی بیشتر براتون سود داشت برین
با هرکس دیگه ای خوشحال ترین برین
اینو از رو ناراحتی نمیگم نه !
من میخوام جایی که دوست دارین باشین
چون وقتی دلتون اینجا و با من نیست
دیگه موندنتون معنی نداره ..''',

    'DKm6Qn6I9VQ': '''دوست داشتن و عشقی در کار نبود
تو فقط دنبال رفع کردن کمبودهای خودت بودی
تشنه توجه بودی و من برات انتخاب کردم
نه واسه فرار از تنهایی، نه واسه سرگرمی و
نه واسه اینکه بخوام ازت استفاده کنم .
من عشقی رو بهت دادم که
لایقش نبودی و قدرشو ندونستی .
تو فقط به من صدمه زدی، اشتباهم این بود که خودم
اونقدر بهت بها دادم که تو وجودم ریشه کردی ،
اما خب ریشه‌تو توی خاطراتم خشک کردم
تو دیگه تموم شدی ...'''
}

for sc, text in candidates.items():
    print(f'=== Testing candidate {sc} ===')
    res_hist = ENGINE.check_duplicate_against_history(text, text)
    print('History result:', res_hist['is_duplicate'], f"{res_hist['similarity_score']}%", res_hist['history_check_badge'])
    
    # Check against all DB scripts
    c_tokens = ENGINE._normalize_persian_tokens(text)
    c_ngrams = ENGINE._extract_ngrams(text, 4)
    db_dup = False
    for s in db.get('scripts', []):
        stext = s.get('content', '') + ' ' + s.get('extracted_raw_text', '')
        s_tokens = ENGINE._normalize_persian_tokens(stext)
        s_ngrams = ENGINE._extract_ngrams(stext, 4)
        if not s_tokens: continue
        overlap = len(c_tokens & s_tokens) / max(1, min(len(c_tokens), len(s_tokens)))
        common_ngrams = c_ngrams & s_ngrams
        if len(common_ngrams) >= 2 or overlap >= 0.40:
            print(f'  DB DUPLICATE with script [{s.get("id")}] "{s.get("title")}": overlap={overlap:.2f}, ngrams={common_ngrams}')
            db_dup = True
    if not db_dup:
        print('  DB Check: PASSED (No duplicates in DB!)')
