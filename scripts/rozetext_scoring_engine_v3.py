"""
RozeText Content Scoring Engine v3.0 — updated for content rules v4.1 (24 Oct 2026).
In v4.1, the old slot multipliers (1.05x / 0.88x) are abolished and no score
tier guarantees any view range. A score is a priority ranking only; compare
actual results to the recent 30-day median, not to these tiers.
====================================
Calibrated on 358 Instagram reels from @rozetext.ir (including 66 latest reels from Oct 2026).
Solves:
 1. Score inflation & compression (prevents artificial 97-99 grouping)
 2. Source view halo effect (decouples external view counts from intrinsic text power)
 3. Preachy/Moralizing penalty (catches generic advice that flops on explore)
 4. Passive-aggressive boundary recognition (boosts dignified closure & boundary setting)
 5. Instant rule-breaker vetoes (birthday/calendar, psychology lecturing, whiny victimhood)
 6. Circadian slot contextual calibration (factors in publication hour effect)
"""

import re
import math

def clean_persian_text(text: str) -> str:
    if not text:
        return ""
    # Remove diacritics
    t = re.sub(r'[\u064B-\u065F\u0670]', '', text)
    # Standardize characters
    t = t.replace('ي', 'ی').replace('ك', 'ک').replace('\u200c', ' ')
    t = re.sub(r'[«»\.\,\:\!\?\(\)\-\_\/؛،\s]+', ' ', t)
    return t.strip()

def evaluate_script_v3(script: dict, slot: int = None) -> dict:
    content = script.get('content', '') or ''
    title = script.get('title', '') or ''
    caption = script.get('caption', '') or ''
    hook = script.get('hook', '') or (content.split('\n')[0].strip() if content else '')
    archetype = script.get('archetype', '') or ''
    scheduled_slot = slot or script.get('scheduled_slot')
    
    full_text = f"{hook} {content} {caption}"
    clean_full = clean_persian_text(full_text)
    clean_hook = clean_persian_text(hook)
    lines = [l.strip() for l in content.split('\n') if l.strip()]
    punchline = lines[-1] if lines else ""
    clean_punch = clean_persian_text(punchline)
    
    words_count = len(clean_full.split())
    lines_count = len(lines)
    
    # ----------------------------------------------------
    # Baseline Components (Max 20 each -> Base 100)
    # ----------------------------------------------------
    p_fit = 17
    h_power = 16
    univ = 18
    mic = 16
    share = 16
    
    penalties = []
    bonuses = []
    
    # ====================================================
    # 1. HARD VETOES & INSTANT PENALTIES (Zero Tolerance)
    # ====================================================
    # A. Calendar / Birthday / Niche Event
    if any(k in clean_full for k in ["تولدمه", "تولدت مبارک", "یک سال بزرگتر", "سالگرد"]):
        univ -= 15
        p_fit -= 5
        penalties.append(("نقض قانون عمومیت ۱۰۰٪: تم تقویمی/تولد", -20))
        
    # B. Psychology lecturing / Third-person teaching / Advice column
    if any(k in clean_full for k in ["از زبان یک روانشناس", "روانشناس میگه", "تحقیقات نشون میده", "۵ نشانه", "تفاوت زن و مرد"]):
        p_fit -= 12
        h_power -= 8
        penalties.append(("نقض پرسونای راوی: لحن آموزشی/روانشناسی زرد", -20))
        
    # C. Preachy / Moral Advice Cliché (نصیحت اخلاقی شعاری)
    preachy_patterns = [
        "عید من روزیه که", "آدما بفهمن", "بفهمن دروغ تا یه جایی",
        "خیلی وقته از حاشیه فراریم", "سرم تو کار خودمه",
        "این اخلاقمو دوست دارم اینکه سر مشکلاتم آدم پرروییم",
        "برعکس آدما خوبی فصل ها"
    ]
    if any(clean_persian_text(p) in clean_full for p in preachy_patterns):
        p_fit -= 6
        h_power -= 5
        share -= 4
        penalties.append(("لحن پندواندرز/شعاری (خطر اسکیپ در اکسپلور)", -15))

    # D. Whiny / Defensive Victimhood (مظلوم‌نمایی تدافعی)
    if "اره من ساده م" in clean_hook or "بین این همه دروغ دنبال صداقتم" in clean_full:
        p_fit -= 4
        h_power -= 4
        penalties.append(("هوک تدافعی و مظلوم‌نمایی فاقد غرور", -8))

    # ====================================================
    # 2. VIRAL CATALYSTS & BONUSES (Empirically Proven)
    # ====================================================
    # A. Relatable Milestone Hook ("از یه سنی به بعد...")
    if any(k in clean_hook for k in ["از یه سنی به بعد", "یه جایی به بعد", "یه زمانی فکر میکردم"]):
        h_power += 4
        univ += 2
        bonuses.append(("هوک بلوغ فکری و نقطه عطف سنتی (+۶)", 6))
        
    # B. Dignified Boundary Setting & Closure (خطاب به آزاردهندگان/تسویه‌حساب باوقار)
    boundary_patterns = [
        "خطاب به کسانی که منو آزار دادن",
        "خطاب به بعضی از دوستان و فامیل",
        "از چشمت میوفته",
        "نفرینت نمیکنم",
        "دیگه مخم نمیکشه صبور نیستم",
        "من ذاتن انسان تنهایی هستم",
        "یه چیزی توی من عوض شده",
        "من اگه برای کسی کاری هم کردم",
        "مگه الکیه"
    ]
    if any(clean_persian_text(b) in clean_full for b in boundary_patterns):
        share += 4
        mic += 3
        p_fit += 2
        bonuses.append(("محرک فوق‌العاده اشتراک دایرکت: مرزبندی باوقار و اقتدار (+۹)", 9))

    # C. Generosity Without Regret (خوبی بدون پشیمانی و با کرامت)
    if any(k in clean_full for k in ["برای دل خودم کردم", "منتظر جبران هیچکس نیستم", "وظیفه م نبود"]):
        p_fit += 2
        mic += 2
        bonuses.append(("اصالت در بخشش و بی منتی (+۴)", 4))

    # D. First-Person Confession vs Third-person
    if any(k in clean_hook for k in ["من", "دلم", "فهمیدم", "یاد گرفتم"]):
        h_power += 1
        p_fit += 1
    elif any(k in clean_hook for k in ["آدما", "همه", "روانشناس"]):
        h_power -= 2

    # E. Structural Length Check
    # Ideal: 45 to 80 words
    if words_count < 35:
        p_fit -= 3
        penalties.append(("متن خیلی کوتاه و کم‌عمق", -3))
    elif words_count > 100:
        mic -= 3
        penalties.append(("متن خیلی طولانی و خسته‌کننده", -3))

    # Cap individual components at [0, 20]
    p_fit = max(0, min(20, p_fit))
    h_power = max(0, min(20, h_power))
    univ = max(0, min(20, univ))
    mic = max(0, min(20, mic))
    share = max(0, min(20, share))
    
    raw_score = p_fit + h_power + univ + mic + share
    
    # ====================================================
    # 3. SLOT EFFECT (v4.1: abolished as a multiplier)
    # ====================================================
    # v4 abolished the old 1.05x / 0.88x slot multipliers, and v4.1 keeps
    # that abolition. Slot fit is already handled by the publisher's
    # 6-slot archetype affinity; do not inflate or deflate the score here.
    slot_multiplier = 1.0
    slot_note = "v4.1: ضریب اسلات لغو شده است؛ نمره فقط اولویت‌بندی است، نه پیش‌بینی بازدید"

    final_score = int(round(raw_score * slot_multiplier))
    final_score = max(0, min(100, final_score))
    
    # Verdict assignment — priority tiers only, no view forecast (v4.1)
    if final_score >= 96:
        verdict = "🔥 اولویت اول انتشار"
        tier = "VIRAL_GOLD"
        expected_views = "بدون پیش‌بینی بازدید — فقط اولویت انتشار؛ با میانه ۳۰ روز اخیر مقایسه شود"
    elif final_score >= 89:
        verdict = "⚡ اولویت بالا"
        tier = "HIGH_MID"
        expected_views = "بدون پیش‌بینی بازدید — فقط اولویت انتشار؛ با میانه ۳۰ روز اخیر مقایسه شود"
    elif final_score >= 80:
        verdict = "📈 انتشار عادی"
        tier = "MID"
        expected_views = "بدون پیش‌بینی بازدید — فقط اولویت انتشار؛ با میانه ۳۰ روز اخیر مقایسه شود"
    else:
        verdict = "❌ رد"
        tier = "REJECTED"
        expected_views = "بدون پیش‌بینی بازدید — رد بر اساس اولویت"

    return {
        "final_score": final_score,
        "raw_score": raw_score,
        "slot_multiplier": slot_multiplier,
        "slot_note": slot_note,
        "breakdown": {
            "persona_fit": p_fit,
            "hook_power": h_power,
            "universality": univ,
            "micdrop_saveability": mic,
            "share_trigger": share
        },
        "verdict": verdict,
        "tier": tier,
        "expected_views": expected_views,
        "penalties": penalties,
        "bonuses": bonuses
    }
