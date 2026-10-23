import sys
sys.path.insert(0, 'scripts')
from anti_duplication import AntiDuplicationEngine

engine = AntiDuplicationEngine()
t = """به شدت آدم رفتار بینی شدم
میدونی دیگه گوشم از حرف پره
من حرفای تو خالی زیادی شنیدم و ادعاهای زیادی دیدم
ادعای دوستی ، دوست داشتن ، ادعای بودن و
خب همشون حرف الکی بود .
الان دیگه مهم نیست کی چی میگه
مهم اینه چیکار میکنن و چقدر شبیه حرفاشونن !
برات مهمم ؟ ارزش دارم ؟ نشونم بده
من خیلی وقته چشمم به رفتار و عمل آدماست
همین ..."""

res = engine.check(t)
print('DaGOw9oNrHy Duplicate:', res['is_duplicate'], 'Score:', f"{res['similarity_score']:.1f}%")
if res.get('matched_with'):
    print('Matched with:', res['matched_with'])
