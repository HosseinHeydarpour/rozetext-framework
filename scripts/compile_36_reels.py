import json
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, 'scripts')
from anti_duplication import AntiDuplicationEngine

engine = AntiDuplicationEngine()

# Load DB to verify no overlaps
with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

db_urls = {s.get('source_url', '').rstrip('/') for s in db['scripts'] if s.get('source_url')}
db_codes = {u.split('/reel/')[-1].split('/')[0] for u in db_urls if '/reel/' in u}

# 1. First 23 reels from approved_24_reels.json (excluding index 20 DYhyAZUMMOl)
app24 = json.load(open('data/approved_24_reels.json', encoding='utf-8'))
approved_list = []
for i, it in enumerate(app24):
    if it['id'] in ['DYhyAZUMMOl', 'Db1UjoWMV8Q', 'DcLWPPZO0XW']:
        continue
    approved_list.append({
        'shortcode': it['id'],
        'author': it['author'],
        'views': it['views'],
        'url': it['url'],
        'text': it['text'].strip()
    })

# 2. The 6 newly approved reels from yesterday
shadi_reels = [
    {
        'shortcode': 'DdeYIgZqlG9',
        'author': '@shadighorbanyy',
        'views': '1.4M',
        'url': 'https://www.instagram.com/reel/DdeYIgZqlG9/',
        'text': """تو کاری کردی
که بچه‌ی خودم
اشک‌هایم را پاک کند؛
دست‌های کوچکش
هنوز
باید دنبالِ پروانه‌ها می‌دوید،
نه روی صورتِ مادرش
دنبالِ ردِ گریه می‌گشت.
تو فقط
مرا نشکستی؛
کودکیِ او را هم
یک شب
زودتر تمام کردی.
فکر می‌کنی
من
تو را می‌بخشم؟"""
    },
    {
        'shortcode': 'DdhIZDEK8_S',
        'author': '@shadighorbanyy',
        'views': '1.1M',
        'url': 'https://www.instagram.com/reel/DdhIZDEK8_S/',
        'text': """آن‌قدر مرد بودی
که فریاد بزنی و توهین کنی؛
اما آن‌قدر مرد نبودی
که بگویی:
«بیا درستش کنیم...
نمی‌توانم از دستت بدهم.»
صدای خشمت
دیوارها را می‌لرزاند؛
اما وقتی پایِ ماندن رسید،
غرورت
حتی اجازه نداد
نام مرا
از پشتِ رفتنم
صدا بزنی."""
    },
    {
        'shortcode': 'DdotWXnCiBy',
        'author': '@shadighorbanyy',
        'views': '779K',
        'url': 'https://www.instagram.com/reel/DdotWXnCiBy/',
        'text': """برای شکارِ من،
تله نگذار؛
کافی‌ست
آن‌قدر آرام باشی
که گمان کنم
این جنگل،
دیگر گرگی ندارد.
من
از شکارچی‌ها جان سالم به در برده‌ام؛
آنچه مرا گرفتار می‌کند،
صدایِ کسی‌ست
که شبیه پناه
راه می‌رود."""
    },
    {
        'shortcode': 'DdzFv9hCAZO',
        'author': '@shadighorbanyy',
        'views': '664K',
        'url': 'https://www.instagram.com/reel/DdzFv9hCAZO/',
        'text': """خیانتش را بخشیدم؛
حتی آن‌قدر عمیق که بعدها
نتوانستم دقیقاً به یاد بیاورم
کدام قسمتِ من
آن روز شکست.
اما خودم را نبخشیدم؛
برای همان لحظه‌ای که فهمیدم
و به جای بستنِ چمدان،
رفتم پرده‌ها را کشیدم؛
تا حقیقت
کمتر به چشم بیاید."""
    },
    {
        'shortcode': 'DeHxCX3i3xc',
        'author': '@shadighorbanyy',
        'views': '1.2M',
        'url': 'https://www.instagram.com/reel/DeHxCX3i3xc/',
        'text': """من همان قماربازی بودم
که می‌دانست
دستِ آخرش سوخته است؛
اما چون
تا آن لحظه
زیاد باخته بود،
بلند شدن از میز
برایش سخت‌تر از باختن بود.
پس ماند.
شرط را بالا برد.
و یک روز فهمید
آنچه باید نجات می‌داد،
بازی نبود؛
باقی‌مانده‌ی خودش بود."""
    },
    {
        'shortcode': 'Ded4vxjsQX3',
        'author': '@horaetemad',
        'views': '833K',
        'url': 'https://www.instagram.com/reel/Ded4vxjsQX3/',
        'text': """دارم به خودم یاد میدم
وقتی فهمیدم کجای زندگیِ آدما وایسادم دیگه
نقش پررنگ تری بازی نکنم
فرقی هم نمیکنه اونا چقدر برام عزیزن
دارم یاد میگیرم که
گاهی وقتا تو برای بقیه اونقدر ارزش نداری که
اونا برای تو دارن و اشکالی هم نداره ..."""
    }
]
approved_list.extend(shadi_reels)

# 3. The 5 newly approved reels from today
today_reels = [
    {
        'shortcode': 'DKaDbPWoKWC',
        'author': '@vahidrezakhoshbayan',
        'views': '600K',
        'url': 'https://www.instagram.com/reel/DKaDbPWoKWC/',
        'text': """شخصیتم ، نقاب و نقش بازی کردن رو تحمل نمیکنه .
چیزی که هستم رو
نمیخوام جور دیگه ای وانمود کنم .
اگه چیزی رو ندارم ادعای داشتنشو نمی کنم و
برای جلب توجه تو نقش فرو نمیرم .
ترجیح میدم با همون چند نفری راه برم
که من واقعی رو دیدن و موندن،
تا اینکه وسط جمعیتی باشم
که بخوان نقابم رو دوست داشته باشن.."""
    },
    {
        'shortcode': 'DIO_li0IL5X',
        'author': '@vahidrezakhoshbayan',
        'views': '530K',
        'url': 'https://www.instagram.com/reel/DIO_li0IL5X/',
        'text': """از صمیم قلب دعا میکنم که
خدا برای همه انقدر پول، موقعیت و موفقیت
فراهم کنه که اصلاً وقت نداشته باشن
راجع به کسی حرف بزنن یا
فکر و ذکرشون آدمای دیگه و زندگیشون باشه.
ایشالا اول خدا به اونا بده، بعد به ما !
انقدر از ما بهتر بشن که دیگه
سرگرم زندگی خودشون باشن و ما رو فراموش کنن.
ما هم یه گوشه خوب یا بد زندگیمونو بکنیم
آمین 🤲🏼"""
    },
    {
        'shortcode': 'DI_5NgqITTy',
        'author': '@vahidrezakhoshbayan',
        'views': '520K',
        'url': 'https://www.instagram.com/reel/DI_5NgqITTy/',
        'text': """شاید بزرگ ترین ویژگیم همین باشه که
ناراحتمو میشم ، اشکمو میریزم ، غصمو میخورم
حتی شده یه مدت خودمو غرق تنهایی میکنم
اما پا پس نمیکشم .
آره من همه جا خودم بودم و خودم و
و کسی رو نداشتم
پس نباید پشت خودمو خالی کنم .
حتی شده زخمی ادامه میدم اما نمیذارم
کسی بگه اون کم اورد ، همینطور که تا الان نذاشتم..."""
    },
    {
        'shortcode': 'DK-E6xoonsH',
        'author': '@vahidrezakhoshbayan',
        'views': '542K',
        'url': 'https://www.instagram.com/reel/DK-E6xoonsH/',
        'text': """برای من تو همون آدمی
آدمی که میون این همه خبر بد ، استرس و جنگ
میون این همه بلاتکلیفی و اینکه نمیدونی قراره چی بشه
برام مثل پناهه .
صحبت با تو منو آروم میکنه
تو میشوری میبری غم و ترس این روزارو .
آره تو برام مثل یه جای امنی
من بیشتر از خودم به فکرو نگران توام
لطفا مراقب خودت باش 🫂"""
    },
    {
        'shortcode': 'DPHRC0yCJxg',
        'author': '@vahidrezakhoshbayan',
        'views': '524K',
        'url': 'https://www.instagram.com/reel/DPHRC0yCJxg/',
        'text': """برای من قدر محبت رو دونستن
از محبت کردن ارزشمندتره
قدرشناسی واسه من خیلی مهمه و به نظرم
قدرتیه که هرکسی ندارتش !
اینکه بتونی تشکر کنی
بتونی یه جوری نشون بدی که محبتو دیدی و فهمیدی
فقط از پس یک شخصیت پخته برمیاد
اونم بین آدمایی که
فکر میکنن هرکاری میکنی وظیفته ..."""
    }
]
approved_list.extend(today_reels)

# 4. The 2 mega-viral clean reels to complete 36
final_two = [
    {
        'shortcode': 'DZSr1vMN1mr',
        'author': '@heliumm.__',
        'views': '1.0M',
        'url': 'https://www.instagram.com/reel/DZSr1vMN1mr/',
        'text': """هنوز قهری..؟!
باشه قهر بمون ولی به خودت برس...
غذا خوب بخور ، لباس گرم بپوش ،
مراقب خودت باش...
قهر بمون ولی شبا زود بخواب...
هنوز قهری..؟!
باشه ولی دلت گرفت به خود من بگو...
قهر بمون ولی با بقیه زیاد نخند :)
اصلا هرچقدر دلت میخواد قهر بمون ؛
ولی یادت نره هیچکس قد من دوستت نداره..."""
    },
    {
        'shortcode': 'DbyY0F7tmAn',
        'author': '@vahidrezakhoshbayan',
        'views': '1.1M',
        'url': 'https://www.instagram.com/reel/DbyY0F7tmAn/',
        'text': """تقصیر خودمونه
انقدر به بعضیا بال و پر دادیم
که فکر کردن واقعا پرواز بلدن !
انقدر بهشون بها دادیم
که خودشونم باورشون شد خبریه .
باید یاد بگیریم با هرکس
دقیقا مثل خودش رفتار کنیم
نه بیشتر ، نه کمتر .
احترام به کسی که لایقش نیست
خیانت به خودته .."""
    }
]
approved_list.extend(final_two)

# 5. Replacements for excluded reels (DcjQOwtN86T and DcJelWZKk0u)
replacements = [
    {
        'shortcode': 'DcjQOwtN86T',
        'author': '@vahidrezakhoshbayan',
        'views': '601K',
        'url': 'https://www.instagram.com/reel/DcjQOwtN86T/',
        'text': """شاید یه مرحله از رشد همین باشه که
تو خیلی چیزارو میفهمی اما خودتو درگیر نمیکنی
میفهمی راجع بهت حرف میزنن
نقاب‌هارو میفهمی
نیت‌های پشت بعضی رفتارهارو میفهمی
میفهمی اما برات اهمیتی نداره.
تو دیگه نه وقت این بچه‌بازیارو داری نه حوصلشو.
فقط جایگاه هرکسی برات یادآوری میشه و
تمرکزت برمیگرده رو زندگی و هدفات .."""
    },
    {
        'shortcode': 'DcJelWZKk0u',
        'author': '@shadighorbanyy',
        'views': '2.8M',
        'url': 'https://www.instagram.com/reel/DcJelWZKk0u/',
        'text': """بخشی از من
از تو متنفر است؛
بخشی هنوز با شنیدن نامت
سرش را برمی‌گرداند؛
بخشی روز تولدت را از حفظ است؛
و بخشی هنوز می‌داند
کدام خاطره کجای قلبم دفن شده.
اما عجیب اینجاست:
در تمامِ این «من»،
دیگر هیچ‌کس تو را دوست ندارد.
تو فراموش نشده‌ای؛
فقط دیگر دوست‌داشتنی نیستی."""
    }
]
approved_list.extend(replacements)

print(f"Total compiled reels: {len(approved_list)}")
print("-" * 65)

all_passed = True
seen_codes = set()
for i, r in enumerate(approved_list):
    sc = r['shortcode']
    txt = r['text']
    lines = [l.strip() for l in txt.split('\n') if l.strip()]
    lcnt = len(lines)
    in_db = sc in db_codes
    is_dup_code = sc in seen_codes
    seen_codes.add(sc)
    
    res = engine.check(txt)
    is_dup = res['is_duplicate']
    score = res['similarity_score']
    
    status = "PASS"
    if in_db or is_dup_code or is_dup or not (7 <= lcnt <= 16):
        status = "FAIL"
        all_passed = False
        
    print(f"[{i+1:02d}] {sc:<12} | {r['author']:<22} | {r['views']:<6} | Lines: {lcnt:2d} | Sim: {score:4.1f}% | {status}")
    if status == "FAIL":
        print(f"     Reason: InDB={in_db}, DupCode={is_dup_code}, DupHist={is_dup}, Lines={lcnt}")

print("-" * 65)
print(f"Overall Status: {'ALL 36 REELS FULLY VALIDATED AND PASSED' if all_passed else 'SOME FAILED'}")

# Save to verified json
with open('data/verified_36_reels_clean.json', 'w', encoding='utf-8') as f:
    json.dump(approved_list, f, ensure_ascii=False, indent=2)
print("Saved to data/verified_36_reels_clean.json")
