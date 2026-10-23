import sys
sys.path.insert(0, 'scripts')
from anti_duplication import AntiDuplicationEngine

engine = AntiDuplicationEngine()
t = """من همان قماربازی بودم
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

res = engine.check(t)
print('DeHxCX3i3xc Duplicate:', res['is_duplicate'], 'Score:', f"{res['similarity_score']:.1f}%")
