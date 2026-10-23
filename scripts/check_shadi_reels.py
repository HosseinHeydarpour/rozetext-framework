import sys
sys.path.insert(0, 'scripts')
from anti_duplication import AntiDuplicationEngine

engine = AntiDuplicationEngine()

cands = [
    {
        "id": "DdHKlyLKHs4",
        "views": "1.5M",
        "author": "@shadighorbanyy",
        "url": "https://www.instagram.com/reel/DdHKlyLKHs4/",
        "text": """یک روز
به سراغ خودم رفتم.
دیدم سال‌هاست
هرکس چیزی از من برداشته
و رفته؛
یکی اعتمادم را،
یکی آرامشم را،
یکی آن آدمی را
که پیش از دوست داشتن
بودم.
هرچه مانده بود
از دستِ دیگران پس گرفتم،
زیر بغلم زدم
و راه افتادم.
هیچ‌کس نفهمید.
آدم وقتی واقعاً می‌رود
دیگر در را به هم نمی‌کوبد؛
فقط چیزی را
که متعلق به خودش بوده
با خود می‌برد."""
    },
    {
        "id": "DdeYIgZqlG9",
        "views": "1.4M",
        "author": "@shadighorbanyy",
        "url": "https://www.instagram.com/reel/DdeYIgZqlG9/",
        "text": """تو کاری کردی
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
        "id": "DdhIZDEK8_S",
        "views": "1.1M",
        "author": "@shadighorbanyy",
        "url": "https://www.instagram.com/reel/DdhIZDEK8_S/",
        "text": """آن‌قدر مرد بودی
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
        "id": "DdotWXnCiBy",
        "views": "779K",
        "author": "@shadighorbanyy",
        "url": "https://www.instagram.com/reel/DdotWXnCiBy/",
        "text": """برای شکارِ من،
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
        "id": "DdzFv9hCAZO",
        "views": "664K",
        "author": "@shadighorbanyy",
        "url": "https://www.instagram.com/reel/DdzFv9hCAZO/",
        "text": """خیانتش را بخشیدم؛
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
    }
]

print(f"{'ID':<15} | {'Views':<6} | {'Status':<10} | {'Max Sim':<8} | {'Best Match ID'}")
print("-" * 65)

passed = []
for c in cands:
    res = engine.check(c['text'])
    is_dup = res["is_duplicate"]
    status = "FAIL" if is_dup else "PASS"
    score = res["similarity_score"]
    bm = res.get("matched_with", {})
    bm_id = bm.get("reel_id") or bm.get("script_id", "none")
    print(f"{c['id']:<15} | {c['views']:<6} | {status:<10} | {score:5.1f}%   | {bm_id}")
    if not is_dup:
        passed.append(c)

print(f"\nTotal passed: {len(passed)} / {len(cands)}")
