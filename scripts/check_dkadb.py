import sys
sys.path.insert(0, 'scripts')
from anti_duplication import AntiDuplicationEngine

engine = AntiDuplicationEngine()
t = """شخصیتم ، نقاب و نقش بازی کردن رو تحمل نمیکنه .
چیزی که هستم رو
نمیخوام جور دیگه ای وانمود کنم .
اگه چیزی رو ندارم ادعای داشتنشو نمی کنم و
برای جلب توجه تو نقش فرو نمیرم .
ترجیح میدم با همون چند نفری راه برم
که من واقعی رو دیدن و موندن،
تا اینکه وسط جمعیتی باشم
که بخوان نقابم رو دوست داشته باشن.."""

res = engine.check(t)
print('DKaDbPWoKWC Duplicate:', res['is_duplicate'], 'Score:', f"{res['similarity_score']:.1f}%")
