import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))
from anti_duplication import AntiDuplicationEngine

engine = AntiDuplicationEngine.get_instance()

def check_candidate(code, author, views, title, text, archetype="1"):
    res = engine.check(text)
    is_dup = res.get('is_duplicate', False)
    sim = res.get('similarity_score', 0.0)
    doc = res.get('matched_document', {}).get('identifier', '')
    lines = [l for l in text.split('\n') if l.strip()]
    status = "REJECTED (DUPLICATE)" if is_dup else ("REJECTED (HIGH SIM)" if sim >= 38.0 else "PASSED")
    print(f"[{status}] {code} | @{author} | {views} | {len(lines)} lines | sim: {sim:.1f}% with {doc}")
    return {
        "shortcode": code,
        "author": f"@{author}" if not author.startswith("@") else author,
        "views": views,
        "title": title,
        "content": text,
        "lines": len(lines),
        "is_dup": is_dup,
        "sim": sim,
        "archetype": archetype,
        "passed": status == "PASSED"
    }

if __name__ == "__main__":
    t1 = """یه چیز جالب درباره بعضی آدمها اینه که؛
تا وقتی بهشون خوبی میکنی،
براشون وقت میزاری و همیشه کوتاه میای ، دوستت دارن،
اما کافیه یه بار خودت رو انتخاب کنی یا یه نه بگی،
همون موقع چهره ی واقعیشون رو می بینی.
بعضی ها عاشق خودت نیستن؛
عاشق نسخه ای از تو هستن که به نفعشونه.
و وقتی اون آدم نباشی،
انگار همه خوبی هات رو فراموش می کنن.
بعضی آدمها وقتی از زندگیت میرن، چیزی رو ازت کم نمی کنن،
فقط ثابت می کنن که
از اول هم به اشتباه اومده بودن تو زندگیت..."""
    check_candidate("Db2jwfXohf4", "text.love400", "511K", "یه چیز جالب درباره بعضی آدمها", t1, "1")
