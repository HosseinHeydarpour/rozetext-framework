import sys
sys.path.insert(0, 'scripts')
from anti_duplication import AntiDuplicationEngine

engine = AntiDuplicationEngine()
t = """دارم به خودم یاد میدم
وقتی فهمیدم کجای زندگیِ آدما وایسادم دیگه
نقش پررنگ تری بازی نکنم
فرقی هم نمیکنه اونا چقدر برام عزیزن
دارم یاد میگیرم که
گاهی وقتا تو برای بقیه اونقدر ارزش نداری که
اونا برای تو دارن و اشکالی هم نداره ..."""

res = engine.check(t)
print('Ded4vxjsQX3 Duplicate:', res['is_duplicate'], 'Score:', f"{res['similarity_score']:.1f}%")
