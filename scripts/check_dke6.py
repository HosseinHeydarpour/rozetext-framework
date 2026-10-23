import sys
sys.path.insert(0, 'scripts')
from anti_duplication import AntiDuplicationEngine

engine = AntiDuplicationEngine()
t = """برای من تو همون آدمی
آدمی که میون این همه خبر بد ، استرس و جنگ
میون این همه بلاتکلیفی و اینکه نمیدونی قراره چی بشه
برام مثل پناهه .
صحبت با تو منو آروم میکنه
تو میشوری میبری غم و ترس این روزارو .
آره تو برام مثل یه جای امنی
من بیشتر از خودم به فکرو نگران توام
لطفا مراقب خودت باش 🫂"""

res = engine.check(t)
print('DK-E6xoonsH Duplicate:', res['is_duplicate'], 'Score:', f"{res['similarity_score']:.1f}%")
