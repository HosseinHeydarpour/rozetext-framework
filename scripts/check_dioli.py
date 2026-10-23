import sys
sys.path.insert(0, 'scripts')
from anti_duplication import AntiDuplicationEngine

engine = AntiDuplicationEngine()
t = """از صمیم قلب دعا میکنم که
خدا برای همه انقدر پول، موقعیت و موفقیت
فراهم کنه که اصلاً وقت نداشته باشن
راجع به کسی حرف بزنن یا
فکر و ذکرشون آدمای دیگه و زندگیشون باشه.
ایشالا اول خدا به اونا بده، بعد به ما !
انقدر از ما بهتر بشن که دیگه
سرگرم زندگی خودشون باشن و ما رو فراموش کنن.
ما هم یه گوشه خوب یا بد زندگیمونو بکنیم
آمین 🤲🏼"""

res = engine.check(t)
print('DIO_li0IL5X Duplicate:', res['is_duplicate'], 'Score:', f"{res['similarity_score']:.1f}%")
