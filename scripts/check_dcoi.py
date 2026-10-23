import sys
sys.path.insert(0, 'scripts')
from anti_duplication import AntiDuplicationEngine

engine = AntiDuplicationEngine()
t = """یه زمانی فکر میکردم اگه برای آدم‌ها خوب باشی،
اونا هم باهات خوب میمونن.
اگه هوای دلشون رو داشته باشی،
یه روزی هوای دلت رو دارن.
اگر پشتشون باشی،پشتت می‌ایستن.
اما زندگی یه چیز دیگه یادم داد.
اینکه بعضی آدم‌ها خوبی رو نمیفهمن،بهش عادت میکنن.
تا وقتی هستی، بودنت براشون عادیه.
تا وقتی میبخشی، فکر میکنن وظیفته.
تا وقتی میمونی، خیال میکنن هیچوقت نمیری.
تا اینکه یه روز تصمیم میگیری دیگه مثل قبل نباشی.
اون موقع تازه میفهمن چی رو از دست دادن.
و دیگه برای جبران دیر شده..."""

res = engine.check(t)
print('DcoiLlvssrD Duplicate:', res['is_duplicate'], 'Score:', f"{res['similarity_score']:.1f}%")
if res.get('matched_with'):
    print('Matched with:', res['matched_with'])
