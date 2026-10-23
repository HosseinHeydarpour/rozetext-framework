import sys
sys.path.insert(0, 'scripts')
from anti_duplication import AntiDuplicationEngine

engine = AntiDuplicationEngine()
t = """من برای همه بودم،
برای خانواده ام هر چه از دستم برآمد کردم
برای دوستانم وقت گذاشتم، کنارشان ماندم،
هر وقت کسی زمین خورد، دستش رو گرفتم
هر وقت کسی شکست، کنارش،نشستم،
هر وقت کسی نیاز داشت، خودم رو فراموش کردم،
اما حالا که خودم خسته ام،
هیچ کس نپرسید تو خوبی؟
شاید اشتباه من همین بود،
آنقدر بی صدا خوبی کردم،
که همه فکر کردند،
خوب بودن من وظیفه ام است.
من هیچ وقت منت محبت هایم را نگذاشتم،
فقط دلم میخواست یک بار، فقط یک بار
کسی بفهمد پشت این آدم همیشه قوی،
یک دل خسته هم هست،
دلی که تمام عمر برای همه تپید،
اما هیچ کس برای تپیدن آن نایستاد..."""

res = engine.check(t)
print('DeHZ8jssKkR Duplicate:', res['is_duplicate'], 'Score:', f"{res['similarity_score']:.1f}%")
if res.get('matched_with'):
    print('Matched with:', res['matched_with'])
