import sys
sys.path.insert(0, 'scripts')
from anti_duplication import AntiDuplicationEngine

engine = AntiDuplicationEngine()
t = """آدم زده شدم
اجتماعی بودن تو این جمع‌ها کار من نیست
نقش بازی کردن ، روابط پیچیده ، نقاب زدن
من از همه‌ی اینا متنفرم
من خیلی وقته ترجیح دادم تنها باشم یا
وقتمو با آدمای کم و امن بگذرونم
این برای من بهتره .."""

res = engine.check(t)
print('DbQ5ACmslaO Duplicate:', res['is_duplicate'], 'Score:', f"{res['similarity_score']:.1f}%")
if res.get('matched_with'):
    print('Matched with:', res['matched_with'])
