import json, sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from server import ENGINE

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

db_texts = [(s.get('content') or '') + ' ' + (s.get('extracted_raw_text') or '') for s in db['scripts']]

reels = [
    # 1. C5WPI8OCK4x
    {
        'id': 'C5WPI8OCK4x',
        'page': '@heliumm.__',
        'views': '1.4M',
        'url': 'https://www.instagram.com/reel/C5WPI8OCK4x/',
        'text': """از یه سنی به بعد وقتی یکی از چشمت میوفته
دیگه نه قهر میکنی باهاش
نه بلاکش میکنی
نه رد تماس میدی..
شاید باهاش سلام احوال پرسی هم بکنی
ولی اون آدم ، دیگه برات اون جایگاه سابقش و نداره
و میشه یکی مثل بقیه
هرچقدر هم بالا بره پایین بیاد
دیگه برات تموم شده..."""
    },
    # 2. DZDRxCkNgjw
    {
        'id': 'DZDRxCkNgjw',
        'page': '@vahidrezakhoshbayan',
        'views': '1.5M',
        'url': 'https://www.instagram.com/reel/DZDRxCkNgjw/',
        'text': """آدم مورد علاقه‌ی خیلی‌ها نیستم
چون نه اهل تملقم، نه برای جلب توجه کسی
رنگ عوض می‌کنم.
من همینی‌ام که هستم،
صاف، ساده، بی‌نقاب...
شاید دایره‌ی آدم‌های دورم کوچیک باشه،
اما خیالم راحته که همون چند نفر،
خودِ واقعیم رو دوست دارن، نه نقابم رو."""
    },
    # 3. DNTYt15oqYj
    {
        'id': 'DNTYt15oqYj',
        'page': '@vahidrezakhoshbayan',
        'views': '1.6M',
        'url': 'https://www.instagram.com/reel/DNTYt15oqYj/',
        'text': """من منتظر جبران هیچکس نیستم.
خوبی کردم چون دلم خواست،
محبت کردم چون ذاتم این بود.
اگه کسی نفهمید یا نادیده گرفت،
چیزی از من کم نشده؛
اون فقط نشون داد لایق نبوده.
من پرونده‌ی آدم‌ها رو با رفتار خودشون می‌بندم،
نه با کینه، نه با دشمنی...
فقط آروم و برای همیشه."""
    },
    # 4. DZSr1vMN1mr
    {
        'id': 'DZSr1vMN1mr',
        'page': '@heliumm.__',
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
    # 5. DPjI0mTCIPs
    {
        'id': 'DPjI0mTCIPs',
        'page': '@vahidrezakhoshbayan',
        'views': '1.2M',
        'url': 'https://www.instagram.com/reel/DPjI0mTCIPs/',
        'text': """آره من ساده‌م !
من هنوز بین این همه دروغ ، دنبال صداقتم .
بین این همه سیاست ، دنبال رو راستیم .
بین این همه رابطه های عجیب ،
دنبال یه حس واقعی و وفاداری‌ام و
بین این همه قضاوت ، دنبال یه درک کوچیکم .
آره شاید از سادگیه که اینا برام مهمه
ولی وضعیت هرچی باشه
من به کمتر از صداقت و وفاداری راضی نمیشم ،
یا بهش میرسم یا تا ابد تنها میمونم ..."""
    },
    # 6. DKm6Qn6I9vQ
    {
        'id': 'DKm6Qn6I9vQ',
        'page': '@vahidrezakhoshbayan',
        'views': '1.3M',
        'url': 'https://www.instagram.com/reel/DKm6Qn6I9vQ/',
        'text': """دوست داشتن و عشقی در کار نبود
تو فقط دنبال رفع کردن کمبودهای خودت بودی
تشنه توجه بودی و من برات انتخاب کردم
نه واسه فرار از تنهایی، نه واسه سرگرمی و
نه واسه اینکه بخوام ازت استفاده کنم .
من عشقی رو بهت دادم که
لایقش نبودی و قدرشو ندونستی .
تو فقط به من صدمه زدی، اشتباهم این بود که خودم
اونقدر بهت بها دادم که تو وجودم ریشه کردی ،
اما خب ریشه‌تو توی خاطراتم خشک کردم
تو دیگه تموم شدی ..."""
    },
    # 7. DQHm9z6CMeL
    {
        'id': 'DQHm9z6CMeL',
        'page': '@vahidrezakhoshbayan',
        'views': '1.0M',
        'url': 'https://www.instagram.com/reel/DQHm9z6CMeL/',
        'text': """دروغ شنیدم و رو راست موندم
بی معرفتی دیدم و ساده گذشتم
سردی دیدم و گرم موندم
بی تفاوتی دیدم و دلسوزی کردم
کم لطفی دیدم و لطف کردم
قضاوت شدم و قضاوت نکردم !
من یاد گرفتم خوب بودنمو به خاطر رفتار آدما
کنار نذارم و مثل همیشه حرفم اینه :
من همون آدم میمونم
اما نه برای همون آدما ..."""
    },
    # 8. DPRj9ddCF5T
    {
        'id': 'DPRj9ddCF5T',
        'page': '@vahidrezakhoshbayan',
        'views': '1.0M',
        'url': 'https://www.instagram.com/reel/DPRj9ddCF5T/',
        'text': """شما تعریف کردین ، ما هم تعریف کردیم
شما از داشته هاتون ، ما هم از نداشته هامون .
شما از برنده شدناتون ، ما هم از باختامون .
شما از آدمای دورتون ، ما هم از تنهاییمون .
اره ما یاد نگرفتیم چیزی که نیستیم رو نشون بدیم
ما همینی بودیم که هستیم
بدون نقاب ، بدون ادعا ، بدون فیلم بازی کردن
شاید به چشم خیلیا نیایم
اما دلمون قرصه که پیش خودمون شرمنده نیستیم .."""
    },
    # 9. DbyY0F7tmAn
    {
        'id': 'DbyY0F7tmAn',
        'page': '@vahidrezakhoshbayan',
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
    },
    # 10. Dd9GQ7HsdZM
    {
        'id': 'Dd9GQ7HsdZM',
        'page': '@text.love400',
        'views': '1.2M',
        'url': 'https://www.instagram.com/reel/Dd9GQ7HsdZM/',
        'text': """مگه الکیه؟
بزنی زندگی یکی دیگه رو نابود کنی و بعد
رو به آسمون خوشبختیت رو از خدا طلب کنی؟!
صد بار گفتم؛ بازم میگم، نمیبخشم و نمیگذرم
میدونم باید بخشید و گذشت و سپرد به خدا
ولی من نه میبخشم،نه میگذرم، من خدامو میشناسم،
هیچ وقت نذاشت، بازم نمیزاره من بی گناه بسوزم
امیدوارم یه روز چوبشو بخوره هر کسی که خواسته
از من و قلبم سوءاستفاده کنه،
اونقدر محکم چوبشو بخوره که اون لحظه همه چیز
مثل یه فیلم از جلو چشماش رد شه،
صد سالم که شد برای حلالیت سمت من نیاین
تا ابد، تا ابد، تا ابد
آه من پشت خودتون و زندگیتونه.
حالا برو قایم کن خودتو از چوب خدا و کارما
ببینم تا کجا میتونی در بری..."""
    },
    # 11. DdEeNFfs5V3
    {
        'id': 'DdEeNFfs5V3',
        'page': '@text.love400',
        'views': '1.6M',
        'url': 'https://www.instagram.com/reel/DdEeNFfs5V3/',
        'text': """خواستم آنقدر خوب باشم
که هیچکس از من ناراحت نشود!
آنقدر مراقب حرف‌هایم باشم
که هیچکس از من نرنجد!
آنقدر ببخشم
که هیچکس مرا کینه‌ای نداند!
بعد فهمیدم دارم زندگی‌ام را
به رضایتِ آدم‌هایی می‌فروشم که
حتی اگه تمامِ وجودم را به آنها بدهم،
باز چیزی برای ایراد گرفتن پیدا خواهند کرد..."""
    }
]

for idx, r in enumerate(reels, 1):
    cid = r['id']
    txt = r['text']
    hist = ENGINE.check_duplicate_against_history(txt, txt)
    
    # DB check
    c_tokens = ENGINE._normalize_persian_tokens(txt)
    max_sim = 0
    closest_s = None
    for s in db['scripts']:
        st = (s.get('content') or '') + ' ' + (s.get('extracted_raw_text') or '')
        st_tokens = ENGINE._normalize_persian_tokens(st)
        sim = len(c_tokens & st_tokens) / max(1, min(len(c_tokens), len(st_tokens)))
        if sim > max_sim:
            max_sim = sim
            closest_s = s['id']
            
    is_clean = (not hist['is_duplicate']) and (max_sim < 0.40)
    status = "CLEAN PASS" if is_clean else "FAIL DUP"
    print(f"[{idx}] {cid} ({r['views']}) | {status} | Hist: {hist['similarity_score']:.1f}% (dup={hist['is_duplicate']}) | DB: {max_sim:.1%}")
