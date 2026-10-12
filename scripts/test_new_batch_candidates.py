import sys, os, json
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from server import ENGINE

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

candidates = [
    {
        'id': 'DORNXb6CJ5D',
        'page': '@vahidrezakhoshbayan',
        'views': '2,100,000 بازدید (2.1M — ۷۴ هزار لایک)',
        'url': 'https://www.instagram.com/reel/DORNXb6CJ5D/',
        'text': """سن و سالم از خیلی چیزا گذشته !
از دشمنی کردن ،
از اهمیت دادن بیخودی به حرف و رفتار آدما
یا از اینکه مدام بخوام به چیزی اصرار کنم
آره سن و سالم از
حرص خوردن واسه چیزایی که دست من نیست
و اثبات خودم گذشته ،
الان فقط آرامش میخوام و دیگه
حوصله و وقتی برای حاشیه رفتن ندارم
فقط میخوام دلی زندگیمو بکنم
همین.."""
    },
    {
        'id': 'DNtMbWm0P4y',
        'page': '@vahidrezakhoshbayan',
        'views': '2,200,000 بازدید (2.2M — ۸۸ هزار لایک)',
        'url': 'https://www.instagram.com/reel/DNtMbWm0P4y/',
        'text': """اشتباهاتشون رو گردن نمیگیرن به کنار
آخرشم میان و تورو مقصر میکنن
آخرشم تویی که اشتباه کردی
تویی که زیادی حساسی
تویی که نمیفهمی و درکی نداری
اونا توضیحی قانعتشون نمیکنه و دنبال راهین که
دیگرانو متهم کنن و
انقدر این بازی رو تکرار میکنن تا به خودت شک کنی
اما نمیدونن این بازی های روانی
دیگه روی ما کار نمیکنه .."""
    },
    {
        'id': 'DMqPqQCIem7',
        'page': '@vahidrezakhoshbayan',
        'views': '1,200,000 بازدید (1.2M — ۵۰ هزار لایک)',
        'url': 'https://www.instagram.com/reel/DMqPqQCIem7/',
        'text': """برای من، موندن پای حرفی که زدی خیلی مهمه.
اگه میگی این ساعت میای، همون موقع بیا
اگه میگی صداقت برات مهمه ، دیگه دروغ نگو
اگه میگی آدم گفت و گوام ، وقت مشکلات حرف بزن
اگه میگی مهمم برات ، تو رفتارت هم نشون بده
اگه قول میدی، بهش وفادار باش
آره من برای احترام به تو هم که شده
رو حرفت حساب میکنم، ولی اگه خلافشو ازت ببینم
دیگه نمیتونم حرفاتو جدی بگیرم .."""
    },
    {
        'id': 'DP9UfRmCoru',
        'page': '@vahidrezakhoshbayan',
        'views': '3,700,000 بازدید (3.7M — ۱۴۲ هزار لایک)',
        'url': 'https://www.instagram.com/reel/DP9UfRmCoru/',
        'text': """من هرکاری که دوست داشتم بقیه برام بکنن رو
با تموم وجودم برای همه انجام دادم .
همدردی کردم، امید دادم،
ذوق کسی رو نکشتم،
وقتی نیاز داشتن، تنهاشون نذاشتم ،
برای کوچیک‌ترین چیزا قدردانی کردم و
سعی کردم با حرفا و کارام به کسی بدی ندم .
من همیشه در حد توانم، سهم خودمو ادا کردم
حتی وقتی هیچ برگشتی نگرفتم .
هرچند دوست داشتم این جاده گاهی دوطرفه میبود ..."""
    },
    {
        'id': 'DP1lpgrCIPE',
        'page': '@vahidrezakhoshbayan',
        'views': '1,900,000 بازدید (1.9M — ۷۴ هزار لایک)',
        'url': 'https://www.instagram.com/reel/DP1lpgrCIPE/',
        'text': """یه وقتایی از خودم میترسم
اینکه ببینی یه کسی نیازی نداری ترسناکه
اینکه هرجا بخوای چندت تنها میری ترسناکه
اینکه کسی کنارت نباشه و برات مهم نیست ترسناکه
آره ترسناکه چون
حس میکنی به چیزی درونت پژمرده شده که
باید زنده می‌موند و نمونده و
ترسناک‌تر از همه اینه که
من این ورژن ترسناکمو دوست دارم .."""
    },
    {
        'id': 'DPZW33eCHx-',
        'page': '@vahidrezakhoshbayan',
        'views': '1,100,000 بازدید (1.1M — ۴۲ هزار لایک)',
        'url': 'https://www.instagram.com/reel/DPZW33eCHx-/',
        'text': """اون روزا دیگه تموم شد.
دیگه محاله اجازه بدم کسی فکر کنه
همین که تو قلبش من فرصت داره میتونه بره و
بیاد و هرکاری تو دلش خواست بکنه و
من بازم ازش استقبال کنم و ساده رد بشم !
دیگه چهارچوب و قوانین رابطه‌هامو مشخص کردم و
به همه هم می‌فهمونم که یه سری رفتارها
منجر به ناراحت شدن و
در نهایت از دست دادن من میشه و باید رعایت کنن !
اینو خیلی خوب درک کردم که
احترام به خودم برام احترام بیشتری میاره .."""
    },
    {
        'id': 'DZQJRhRNpQG',
        'page': '@vahidrezakhoshbayan',
        'views': '1,300,000 بازدید (1.3M — ۵۳ هزار لایک)',
        'url': 'https://www.instagram.com/reel/DZQJRhRNpQG/',
        'text': """وقتی عصبیم و سکوت میکنم
یعنی از خودم میترسم نه از کسی دیگه...
چون میدونم اگه حرفی بزنم یا کاری کنم
تهش از خودم بدم میاد
چون اون روی تاریکمو میشناسم و
میدونم اگه بالا بیاد چه کارایی میتونه بکنه
چون نمیخوام اون باشم
چون دور از شخصیت منه..."""
    }
]

print(f"Auditing {len(candidates)} candidates against 233 History & 81 DB Scripts...\n")

for c in candidates:
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
