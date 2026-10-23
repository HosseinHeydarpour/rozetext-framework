import sys
sys.path.insert(0, 'scripts')
from anti_duplication import AntiDuplicationEngine

engine = AntiDuplicationEngine()
t = """برای من قدر محبت رو دونستن
از محبت کردن ارزشمندتره
قدرشناسی واسه من خیلی مهمه و به نظرم
قدرتیه که هرکسی ندارتش !
اینکه بتونی تشکر کنی
بتونی یه جوری نشون بدی که محبتو دیدی و فهمیدی
فقط از پس یک شخصیت پخته برمیاد
اونم بین آدمایی که
فکر میکنن هرکاری میکنی وظیفته ..."""

res = engine.check(t)
print('DPHRC0yCJxg Duplicate:', res['is_duplicate'], 'Score:', f"{res['similarity_score']:.1f}%")
