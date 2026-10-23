import sys, json
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

db = json.load(open('data/scripts-db.json', encoding='utf-8'))

raw_on_screen = """من از شنیدن یه جمله توی این دنیا
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

updated = False
for s in db['scripts']:
    if s.get('id') == 'reel-tue-04' or 'DdYw7Mhu6m_' in s.get('source_url', ''):
        s['content'] = raw_on_screen
        s['extracted_raw_text'] = raw_on_screen
        s['lines_count'] = 16
        s['words_count'] = len(raw_on_screen.split())
        s['confirmed_frame_path'] = 'downloads/frames/DdYw7Mhu6m__2s_frame.png'
        s['extra_notes'] = 'اصلاح‌شده بر اساس تصویر و فریم اورجینال ویدیو (متن کامل ۱۶ سطری روی تصویر)'
        updated = True
        print(f"Updated script {s['id']} successfully!")

if updated:
    db['meta']['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open('data/scripts-db.json', 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    print("Database saved successfully!")
else:
    print("Script not found!")
