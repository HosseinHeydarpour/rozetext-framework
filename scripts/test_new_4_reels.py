import sys, os, json
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from server import ENGINE

reels = [
    {
        'id': 'DZ5TIO_tUb0',
        'page': '@heliumm.__',
        'views': '1.1M',
        'url': 'https://www.instagram.com/reel/DZ5TIO_tUb0/',
        'text': """من هیچوقت نتونستم خانوادم و در جریان
مشکلات زندگیم قرار بدم...
چون کاری از دستشون بر نمیاد ؛
و بدتر از اون مدل همدردی کردنشون هم استرس دادنه...
بعد الان اینجوری شده که ، چون در جریان مشکلاتم نیستن
فکر میکنن همه چیز عالیه :)
در صورتی که توان ذهنی من برای هیچ درد و نارحتی و
درامای بیشتر آماده نیست .
حتی این رو هم نمیتونم بهشون بگم ؛
اینکه پشت نقاب بزرگسالیمون کودکی است نیازمند عاطفه ،
گذشت ، عشق و ترسیده از هم تنهایی ، هم رابطه..."""
    },
    {
        'id': 'DZDGR5kN23g',
        'page': '@heliumm.__',
        'views': '1.4M',
        'url': 'https://www.instagram.com/reel/DZDGR5kN23g/',
        'text': """تموم شد...
نه با دعوا ، نه با فریاد ، نه حتی با یه خداحافظی درست:)
آروم تموم شد ، مثل چیزی که مدت‌ها بود هر روز
تو دلم تُرک میخورد و من وانمود میکردم هنوز سالمه..
حالا من موندم و فکرایی که ول کن نیستن ؛
و با دلی که بیشتر از حدش تحمل کرده .
تموم شد اونجایی که فهمیدم تنهایی با خودم ،
کم دردتر از با هم بودنِ بی حال و بی حسه...
اوضاع خوب نیست حالمم تعریفی نداره
اما دارم یاد میگیرم بعضی پایان‌ها لازمن حتی
اگه خیلی درد داشته باشن..."""
    },
    {
        'id': 'DZAn8Tht71I',
        'page': '@heliumm.__',
        'views': '2.3M',
        'url': 'https://www.instagram.com/reel/DZAn8Tht71I/',
        'text': """اگه یه روز خدا رو ببینم
فکر کنم اولین چیزی که ازش میپرسم همین باشه :
کدوم درد من برات لذت بخش بود ؟
کدوم لحظه‌ی گریه هام ، کدوم شب بی خوابی هام..؟
کدوم زخم بازِ روی دلم...
اونقدری قشنگ بود که هی لبخند زدی ؛
هی لبخند زدی و هی ادامش دادی :)
می‌پرسم چرا هر بار که گفتم بَسه ، بازی یه غُصه‌ی جدید
گذاشتی روی قبلی..؟
چرا هیچوقت از خودت نپرسیدی این آدمی که ساختی
چقدر ظرفیت داره ؟
اگه یه روز ببینمش فقط یه چرا دارم
یه چرای بزرگ که سال‌هاست تو گلوم گیر کرده و
هیچکس جز خودش جوابشو نمیدونه :)"""
    },
    {
        'id': 'DZ74wmvR17q',
        'page': '@heliumm.__',
        'views': '1.0M',
        'url': 'https://www.instagram.com/reel/DZ74wmvR17q/',
        'text': """چجوری ببخشمت..؟!
اون شب تا صبح فشار قلب داشتم...
انقدر زیاد که حس کردم الانه که از فشار قلب بمیرم...
انگاری قلبمو گرفته بودی تو دستات و چنگ میزدی...
چجوری ببخشمت ؟
از عصبانیت و فشار روانی کل تنم می‌لرزید ولی تو
راحت گرفتی خوابیدی...
چجوری ببخشمت ؟
وقتی بغض گلمو گرفته بود و داشت خفم میکرد...
چجوری ببخشمت ؟
با هر اتفاق کوچیکی یه دور بخاطر تو گریم میگیره...
چجوری ببخشمت ؟
وقتی یادم میاد اون همه دوستت دارمات دروغ بود...
چجوری ببخشمت ؟
موهای سرمو سفید کردی :)"""
    }
]

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

for r in reels:
    cid = r['id']
    txt = r['text']
    res_hist = ENGINE.check_duplicate_against_history(txt, txt)
    
    # DB check
    c_tokens = ENGINE._normalize_persian_tokens(txt)
    c_ngrams = ENGINE._extract_ngrams(txt, 4)
    max_sim = 0
    closest_s = None
    common_ng_count = 0
    for s in db['scripts']:
        st = (s.get('content') or '') + ' ' + (s.get('extracted_raw_text') or '')
        st_tokens = ENGINE._normalize_persian_tokens(st)
        sim = len(c_tokens & st_tokens) / max(1, min(len(c_tokens), len(st_tokens)))
        st_ngrams = ENGINE._extract_ngrams(st, 4)
        cng = len(c_ngrams & st_ngrams)
        if sim > max_sim:
            max_sim = sim
            closest_s = s.get('id')
            common_ng_count = cng
            
    print(f'=== {cid} ({r["views"]}) ===')
    print(f'  History: duplicate={res_hist["is_duplicate"]}, score={res_hist["similarity_score"]:.1f}%, match={res_hist["duplicate_of_reel"]}')
    print(f'  DB: max_sim={max_sim:.1%}, closest={closest_s}, common_4grams={common_ng_count}')
    is_clean = (not res_hist['is_duplicate']) and (max_sim < 0.40) and (common_ng_count < 2)
    print(f'  Clean?: {is_clean}')
