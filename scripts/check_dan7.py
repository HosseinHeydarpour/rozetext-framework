import sys
sys.path.insert(0, 'scripts')
from anti_duplication import AntiDuplicationEngine

engine = AntiDuplicationEngine()
t = """این اخلاقِمو دوست دارم
اینکه سر مشکلاتم آدمِ پررویی‌ام.
می‌شینم غصه‌مو می‌خورم و با ناراحتیم سر می‌کنم
اما بعدش یه جوری بلند می‌شم و
با یه نسخه جدیدی از خودم ادامه میدم که
انگار اصلا من نبودم که
تا دو روز پیش لب پرتگاه فروپاشی بودم.
آره شاید بزرگ‌ترین ویژگی‌م همین باشه:
ادامه دادن اونم وقتی که ادامه دادن محاله..."""

res = engine.check(t)
print('DaN7SayomTk Duplicate:', res['is_duplicate'], 'Score:', f"{res['similarity_score']:.1f}%")
if res.get('matched_with'):
    print('Matched with:', res['matched_with'])
