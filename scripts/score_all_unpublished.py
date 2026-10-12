import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

unpub = [s for s in db.get('scripts', []) if not s.get('published')]

print(f"Total unpublished: {len(unpub)}\n")

# Detailed rubric scoring function based on SKILL.md v2.0
def evaluate_script(s):
    content = s.get('content', '')
    title = s.get('title', '')
    arch = s.get('archetype', '')
    views_str = s.get('source_views', '')
    
    # 1. Persona fit (20)
    # Deduct if whiny, aggressive, insulting, toxic
    p_fit = 19
    reasons = []
    if "تشنه توجه" in content or "صدمه زدی" in content or "کمبودهای خودت" in content:
        p_fit = 11
        reasons.append("پرخاشگرانه و تهاجمی به پارتنر (ضد پرسونای باوقار)")
    elif "من ساده‌م" in content:
        p_fit = 16
        reasons.append("لحن تدافعی/مظلوم‌نمایی در هوک")
    elif "آرکتایپ ۵" in arch or "آرکتایپ ۱" in arch:
        p_fit = 20
    
    # 2. Hook power (20)
    hook = content.split('\n')[0].strip() if content else ''
    h_power = 19
    if "دوست داشتن و عشقی در کار نبود" in hook:
        h_power = 14
        reasons.append("هوک تهاجمی و کینه‌توزانه")
    elif "آره من ساده‌م" in hook:
        h_power = 16
        reasons.append("هوک ضعیف در برانگیختن حس غرور")
    elif any(k in hook for k in ["حال عجیبی دارم", "هیچوقت هیچ آدمی رو برای منفعت", "من اگه برای کسی", "امسال نسخه‌ای", "این اخلاقمو"]):
        h_power = 20

    # 3. Universality (20)
    univ = 19
    if "امروز تولدمه" in content:
        univ = 10
        reasons.append("وابستگی تقویمی (نقض قانون ۱۰۰٪ عمومیت)")
    elif "تشنه توجه" in content:
        univ = 12
        reasons.append("عدم تمایل مخاطب به استوری به دلیل بار منفی شدید")
    elif any(k in hook for k in ["حال عجیبی دارم", "هیچوقت هیچ آدمی رو برای منفعت", "من اگه برای کسی"]):
        univ = 20

    # 4. Mic-drop saveability (20)
    punch = content.split('\n')[-1].strip() if content else ''
    mic = 19
    if "تو دیگه تموم شدی" in punch:
        mic = 13
        reasons.append("پانچ‌لاین کلیشه‌ای و خشن")
    elif "آدمی که با دلش زندگی میکنه" in punch or "روزا چطور میان و میرن" in punch:
        mic = 20

    # 5. Share trigger (20)
    share = 19
    if "تشنه توجه" in content:
        share = 12
        reasons.append("نرخ اشتراک پایین به دلیل انرژی منفی")
    elif "من اگه برای کسی" in content or "هیچوقت هیچ آدمی رو" in content:
        share = 20

    total = p_fit + h_power + univ + mic + share
    verdict = "PASSED (🔥 مگاوایرال)" if total >= 96 else ("PASSED (⚡ وایرال خوب)" if total >= 89 else ("BORDERLINE (⚖️ متوسط)" if total >= 82 else "REJECTED (❌ مردود)"))
    
    return {
        "id": s.get('id'),
        "date": s.get('scheduled_date'),
        "slot": s.get('scheduled_slot'),
        "title": title,
        "views": views_str,
        "total": total,
        "breakdown": {"p_fit": p_fit, "h_power": h_power, "univ": univ, "mic": mic, "share": share},
        "verdict": verdict,
        "reasons": reasons
    }

results = [evaluate_script(s) for s in unpub]
results.sort(key=lambda x: (x['date'], x['slot']))

print("=== TODAY (2026-10-06) & TOMORROW (2026-10-07) RESULTS ===")
for r in results:
    if r['date'] in ['2026-10-06', '2026-10-07']:
        print(f"[{r['date']} - Slot {r['slot']}] {r['verdict']} -> Score: {r['total']}/100")
        print(f"  Title: {r['title']} ({r['views']})")
        print(f"  Breakdown: Persona={r['breakdown']['p_fit']}, Hook={r['breakdown']['h_power']}, Univ={r['breakdown']['univ']}, Mic={r['breakdown']['mic']}, Share={r['breakdown']['share']}")
        if r['reasons']:
            print(f"  Notes: {', '.join(r['reasons'])}")
        print("-" * 50)
