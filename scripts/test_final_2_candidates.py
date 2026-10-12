import sys, os, json
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from server import ENGINE

reels_to_test = [
    {
        'id': 'DIJ0fkOoP5I',
        'page': '@vahidrezakhoshbayan',
        'views': '2.5M',
        'url': 'https://www.instagram.com/reel/DIJ0fkOoP5I/',
        'text': """به شدت آدم رفتار بینی شدم
میدونی چیه ؟
من حرفای تو خالی زیادی شنیدم و ادعاهای زیادی دیدم
ادعای دوستی ، دوست داشتن ، ادمای بودن و
خب همشون حرف الکی بود
الان دیگه مهم نیست کی چی میگه
مهمه اینه چیکار میکنن و چقدر شبیه حرفاشون !
برات مهمم ؟ ارزش دارم ؟ نشونم بده
من خیلی وقته چشمم به رفتار و عمل ادماست
همین .."""
    },
    {
        'id': 'DUTapHFjeMV',
        'page': '@heliumm.__',
        'views': '1.5M',
        'url': 'https://www.instagram.com/reel/DUTapHFjeMV/',
        'text': """تو خانواده من همونم که
حق نداره خسته بشه
حق نداره گله کنه از دردام دفاع کنم
حق نداره بگم حالم خوب نیست
همونم که باید همه رو درک کنه ، حواسش باشه کسی
ناراحت نشه ، بهش برنخوره ..
هیچوقت هیچکس حواسش به من نیست !
بابا خودشم باور کنید ، منم آدمم ، دل دارم ..
منم سختم میشه :)"""
    }
]

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

for r in reels_to_test:
    cid = r['id']
    txt = r['text']
    hist = ENGINE.check_duplicate_against_history(txt, txt)
    
    # DB check
    c_tokens = ENGINE._normalize_persian_tokens(txt)
    max_sim = 0
    closest_s = None
    for s in db['scripts']:
        st = (s.get('content') or '') + ' ' + (s.get('extracted_raw_text') or '')
        st_tokens = ENGINE._normalize_persian_tokens(st)
        sim = len(c_tokens & st_tokens) / max(1, min(len(c_tokens), len(st_tokens)))
        if sim > max_sim:
            max_sim = sim
            closest_s = s['id']
            
    print(f"=== [{cid}] {r['page']} ({r['views']}) ===")
    print(f"Lines: {len(txt.splitlines())}")
    print(f"History Dup: {hist['is_duplicate']} (Score: {hist['similarity_score']:.1f}%)")
    print(f"DB Sim: {max_sim:.1%} (Closest: {closest_s})")
    print()
