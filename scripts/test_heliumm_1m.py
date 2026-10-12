import sys, os, json
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from server import ENGINE

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

cands = [
    {
        'id': 'DSNZ6tMDaJx',
        'page': '@heliumm.__',
        'views': '4,460,000 بازدید (4.46M)',
        'url': 'https://www.instagram.com/reel/DSNZ6tMDaJx/',
        'text': """من هیچوقت نتونستم خانواده‌ام رو در جریان
مشکلات زندگیم قرار بدم...
چون کاری از دستشون بر نمیاد ؛
و بدتر از اون مدل همدردی کردنشون هم استرس دادنه...
بعد الان اینجوری شده که ،
چون در جریان مشکلاتم نیستن فکر میکنن همه چیز عالیه :)
در صورتی که توان ذهنی من برای
هیچ درد و ناراحتی و درامای بیشتر آماده نیست !
حتی این رو هم نمیتونم بهشون بگم...
اینکه پشت نقاب بزرگسالیمون
کودکی است نیازمند عاطفه ، گذشت ، عشق و
ترسیده از هم تنهایی ، هم رابطه..."""
    },
    {
        'id': 'DRAa3nwDQ8I',
        'page': '@heliumm.__',
        'views': '1,860,000 بازدید (1.86M)',
        'url': 'https://www.instagram.com/reel/DRAa3nwDQ8I/',
        'text': """عاشق نسخه الانمم :)
چون تیکه تیکه‌شو خودم ساختم...
من از هر مشکلی یه تیکه به نفع خودم بیرون کشیدم و
به خودم اضافه کردم...
الان آدمیم که میدونه کجا احساسی باشه و کجا منطقی
با کی بگرده و از کی فاصله بگیره
چطور متمرکز بمونه و خودشو خرج وابستگی‌ها و
چیزای الکی نکنه...
من خود الانمو دوست دارم
چون راه آسونی رو تا اینجا جلو نیومده..."""
    },
    {
        'id': 'DSAgO_1jbpc',
        'page': '@heliumm.__',
        'views': '3,010,000 بازدید (3.01M)',
        'url': 'https://www.instagram.com/reel/DSAgO_1jbpc/',
        'text': """حالا که همه چی تموم شده بزار
بهت یچیزی بگم...
من تمام نقطه ضعفامو بهت گفته بودم ،
بهت گفته بودم چه کارایی رو انجام نده ،
بهت گفته بودم چجوری اذیت میشم و
دقیقاً با همونا اذیتم کردی :)
خیلی جاها تو میدونستی اگر اون کارو بکنی من خورد میشم
و برات مهم نبود و انجامش دادی...
هیچ گله‌ایم نیست تقصیر خودم بود :)
من باید یجور رفتار میکردم که انگار هیچی
برام مهم نیست...
من جدی گرفتمت ، فکر میکردم شبیه حرفاتی
فکر میکردم آدم موندن و ساختنی ولی نبودی...
با همون نقطه ضعفایی که ازم داشتی
اذیتم کردی...❤️‍🩹🥀"""
    },
    {
        'id': 'DVBsqRSjaim',
        'page': '@heliumm.__',
        'views': '2,590,000 بازدید (2.59M)',
        'url': 'https://www.instagram.com/reel/DVBsqRSjaim/',
        'text': """اگه یه روز خدارو ببینم
فکر کنم اولین چیزی که ازش بپرسم همین باشه :
کدوم درد من برات لذت‌بخش بود...؟
کدوم لحظه‌ی گریه‌هام ، کدوم شب بی‌خوابی‌هام ،
کدوم زخم باز روی دلم...
اونقدری قشنگ بود که هی لبخند زدی ؛
هی لبخند زدی و هی ادامش دادی...
میپرسم چرا هر بار که گفتم بسه باز یه غصه‌ی جدید
گذاشتی روی قبلی...!
چرا هیچوقت از خودت نپرسیدی !
این آدمی که ساختی چقدر ظرفیت داره..؟
اگه یه روز ببینمش ، فقط یه (( چرا )) دارم
یه چرای بزرگ که سال‌هاست تو گلوم گیر کرده و
هیچکس جز خودش جوابشو نمیدونه...💔"""
    },
    {
        'id': 'DOQzXm-CMis',
        'page': '@heliumm.__',
        'views': '1,660,000 بازدید (1.66M)',
        'url': 'https://www.instagram.com/reel/DOQzXm-CMis/',
        'text': """امشب یکم تو خودم بودم....
حال نداشتم با هیشکی حرف بزنم خسته بودم ، یکمم کلافه...
بعد چند ساعت قبل خواب اومدم گوشیمو چک کردم
دیدم نه پیامی از کسی دارم نه زنگی :)
هیشکی حتی نفهمید من حالم خوب نیس
هیشکی نگرانم نبود...
انگاری من تنها بودم تو این دنیای به این بزرگی ،
هیشکیو نداشتمو تنها بودم...
حس بدیه ؛
همین شد که بالشمو بغل کردمو خوابیدم :)) تنها...🥀
همونجوری خسته و ناراحت..."""
    },
    {
        'id': 'DSsY-q4DeMQ',
        'page': '@heliumm.__',
        'views': '2,190,000 بازدید (2.19M)',
        'url': 'https://www.instagram.com/reel/DSsY-q4DeMQ/',
        'text': """دیگه ازت هیچی نمیخوام ، منتظر هم نیستم
زنگ زدنت...
برای اومدنت...
دوست داشتنت...
اگه قبلاً بود برای همه اینا هرکاری میکردم ؛
اما...
اما الان حوصله هیچ کاری رو ندارم
از دوست نداشتنم نیست :)
دیگه احساسی ندارم...
هرجا که هستی همونجا بمون
متعلق به همونجا باش ."""
    }
]

print("=== AUDITING HELIUMM 1M+ CANDIDATES ===")
for c in cands:
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
