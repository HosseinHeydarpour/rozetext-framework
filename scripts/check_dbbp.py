import sys
sys.path.insert(0, 'scripts')
from anti_duplication import AntiDuplicationEngine

engine = AntiDuplicationEngine()
t = """من اگه کنار کسی هم بودم و کاری هم براش کردم
فقط به خاطر خودش بوده .
هیچوقت هیچ ادمی رو برای منفعت
کنارم نگه نداشتم
دودوتا چهارتا نکردم ببینم کی بیشتر میصرفه .
من حسابگر نبودم ، دلی بودم .
برای من فقط بودن واقعی و صادقانه مهمه
آره از کسی چیزی نمیخوام
جز اینکه با دل صاف و بدون نقاب کنارم باشه .."""

res = engine.check(t)
print('DbbPmLFNZbj Duplicate:', res['is_duplicate'], 'Score:', f"{res['similarity_score']:.1f}%")
if res.get('matched_with'):
    print('Matched with:', res['matched_with'])
