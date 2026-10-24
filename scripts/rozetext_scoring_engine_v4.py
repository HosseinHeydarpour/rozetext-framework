"""DRAFT v4 — NOT yet the hunting engine. v3 remains authoritative until the prospective test in engine-v4-report.md passes. """
"""Draft v4 scoring, derived ONLY from the 399 own-page posts.
Weights are deliberately coarse (steps, not fitted decimals) to avoid overfitting tiny samples.
See engine-v4-report.md for evidence and limits."""
import re

def clean_persian_text(text):
    if not text:
        return ""
    t = re.sub(r'[\u064B-\u065F\u0670]', '', text)
    t = t.replace('ي', 'ی').replace('ك', 'ک').replace('\u200c', ' ')
    t = re.sub(r'[«»\.\,\:\!\?\(\)\-\_\/؛،\s]+', ' ', t)
    return t.strip()

FAMILY=['مامان','بابا','خانواده','خواهرم','برادرم','مادرم','پدرم']
WORK=['کار','پول','سخت','تلاش','موفق']
BOUNDARY=["خطاب به کسانی که منو آزار دادن","خطاب به بعضی از دوستان و فامیل","از چشمت میوفته","نفرینت نمیکنم","دیگه مخم نمیکشه صبور نیستم","من ذاتن انسان تنهایی هستم","یه چیزی توی من عوض شده","من اگه برای کسی کاری هم کردم","مگه الکیه"]
MILESTONE=["از یه سنی به بعد","یه جایی به بعد","یه زمانی فکر میکردم"]
PREACHY=["عید من روزیه که","آدما بفهمن","بفهمن دروغ تا یه جایی","خیلی وقته از حاشیه فراریم","سرم تو کار خودمه","این اخلاقمو دوست دارم اینکه سر مشکلاتم آدم پرروییم","برعکس آدما خوبی فصل ها"]

def evaluate_script_v4(script):
    content=script.get('content','') or ''
    caption=script.get('caption','') or ''
    lines=[l.strip() for l in content.split('\n') if l.strip()]
    hook=script.get('hook','') or (lines[0] if lines else '')
    full=f"{hook} {content} {caption}"
    clean=clean_persian_text(full); clean_hook=clean_persian_text(hook)
    words=len(content.split()); nlines=len(lines)
    fp=sum(content.count(w) for w in ['من ','منم','دلم','خودم'])
    score=40; parts={}; bonuses=[]; penalties=[]
    # length / structure (strongest own-data signal, replaces fixed 83 baseline)
    if nlines>=16: parts['structure']=20
    elif nlines>=13: parts['structure']=14
    elif nlines>=11: parts['structure']=9
    elif nlines>=8: parts['structure']=5
    else: parts['structure']=0
    score+=parts['structure']
    # first-person density
    if fp>=6: parts['first_person']=15
    elif fp>=3: parts['first_person']=8
    else: parts['first_person']=0
    score+=parts['first_person']
    if clean_hook.startswith('من'): parts['hook_first_person']=5; score+=5
    else: parts['hook_first_person']=0
    # themes that separated in own data
    parts['family']=10 if any(k in content for k in FAMILY) else 0; score+=parts['family']
    parts['work']=5 if any(k in content for k in WORK) else 0; score+=parts['work']
    parts['question']=5 if ('؟' in content or '?' in content) else 0; score+=parts['question']
    # kept v3 bonuses (small-n, but direction confirmed: boundary vpd 23761, milestone vpd 10659)
    if any(clean_persian_text(b) in clean for b in BOUNDARY): bonuses.append(('boundary +12',12)); score+=12
    if any(k in clean_hook for k in MILESTONE): bonuses.append(('milestone hook +8',8)); score+=8
    # penalties that actually flopped in own data (vpd ~700-770, 0% viral)
    if words<45: penalties.append(('too short <45 words -15',-15)); score-=15
    if any(clean_persian_text(p) in clean for p in PREACHY): penalties.append(('preachy -15',-15)); score-=15
    if any(k in clean for k in ["تولدمه","تولدت مبارک","یک سال بزرگتر","سالگرد"]): penalties.append(('calendar -15',-15)); score-=15
    if any(k in clean for k in ["از زبان یک روانشناس","روانشناس میگه","تحقیقات نشون میده","۵ نشانه","تفاوت زن و مرد"]): penalties.append(('psychology lecturing -15',-15)); score-=15
    # NOTE: v3 long-text penalty (>100 words, -3) is REMOVED: those posts had median vpd 5183 and 31% viral, better than average.
    final=max(0,min(100,score))
    tier='TOP' if final>=80 else 'HIGH' if final>=70 else 'MID' if final>=55 else 'LOW'
    return {'final_score':final,'breakdown':parts,'bonuses':bonuses,'penalties':penalties,'tier':tier,
            'features':{'words':words,'lines':nlines,'first_person':fp}}
