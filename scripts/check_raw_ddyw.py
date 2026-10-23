import sys, json
sys.stdout.reconfigure(encoding='utf-8')
from anti_duplication import AntiDuplicationEngine

original_raw = """من از شنیدن یه جمله توی این دنیا
به شدت می ترسم...
انقدر که حتی فکر کردن بهش تمام وجودم را می لرزونه!
اینکه یک نفر با دل شکسته به آدم بگه:
به خدا واگذارت کردم...!
حقیقتش اینه که حتی اگر به زبون هم نگه
و فقط توی دلش تو رو به خدا بسپاره،
بازم تاوان عجیبی داره...
چون خدا صفتی داره به نام "جبار"....
یک انتقام گیرنده ی عجیب و غریب
که وقتی کار به خودش سپرده بشه،
جوری حق اون مظلوم رو پس میگیره
که باور کردنی نیست!
بترسید از روزی که خدای جبار وارد بازی بشه،
دیگه معلوم نیست چه تاوان سنگینی
قراره سر راهتون قرار بگیره..."""

engine = AntiDuplicationEngine.get_instance()
res = engine.check(original_raw)
print('Duplicate:', res['is_duplicate'])
print('Score:', res['similarity_score'])
print('Match reason:', res.get('match_reason'))
if res.get('matched_document'):
    print('Matched doc snippet:', res['matched_document'].get('content_snippet', '')[:100])
