import sys
sys.path.insert(0, 'scripts')
from anti_duplication import AntiDuplicationEngine

engine = AntiDuplicationEngine()
t = """شاید بزرگ ترین ویژگیم همین باشه که
ناراحتمو میشم ، اشکمو میریزم ، غصمو میخورم
حتی شده یه مدت خودمو غرق تنهایی میکنم
اما پا پس نمیکشم .
آره من همه جا خودم بودم و خودم و
و کسی رو نداشتم
پس نباید پشت خودمو خالی کنم .
حتی شده زخمی ادامه میدم اما نمیذارم
کسی بگه اون کم اورد ، همینطور که تا الان نذاشتم..."""

res = engine.check(t)
print('DI_5NgqITTy Duplicate:', res['is_duplicate'], 'Score:', f"{res['similarity_score']:.1f}%")
