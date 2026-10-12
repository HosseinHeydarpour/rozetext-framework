import sys, os, glob, re, json
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from server import ENGINE

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

existing_db_texts = []
for s in db.get('scripts', []):
    t = (s.get('content') or '') + ' ' + (s.get('extracted_raw_text') or '')
    if t.strip():
        existing_db_texts.append((s.get('id'), s.get('title'), t.strip()))

d = r"C:\Users\User\.gemini\antigravity\brain\727a329c-ae5d-47f3-930f-a557f52abe67"
md_files = glob.glob(d + "/*.md")

reels_found = {}

for mf in md_files:
    if 'metadata' in mf: continue
    with open(mf, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()
        
    # Split by ## [number]. ریلز: `[shortcode]`
    sections = re.split(r'##\s*\d+\.\s*ریلز:\s*`([^`]+)`', text)
    if len(sections) > 1:
        for i in range(1, len(sections), 2):
            sc = sections[i].strip()
            body = sections[i+1]
            
            # Find text inside ```text ... ```
            tm = re.search(r'```text\s*(.*?)\s*```', body, re.DOTALL)
            if not tm:
                continue
            raw_text = tm.group(1).strip()
            lines = [l.strip() for l in raw_text.splitlines() if l.strip()]
            
            reels_found[sc] = {
                'shortcode': sc,
                'source_url': f"https://www.instagram.com/reel/{sc}/",
                'raw_text': raw_text,
                'lines': len(lines),
                'file': os.path.basename(mf)
            }

print(f"Total reels parsed from review markdown: {len(reels_found)}")

# Now let's test each reel:
clean_pool = []
for sc, r in reels_found.items():
    txt = r['raw_text']
    lines = r['lines']
    if lines < 7 or lines > 16:
        continue
    
    # Persona check
    bad_words = ['مولانا', 'شمس', 'دختر', 'پسر', 'تولد', 'نوروز', 'یلدا']
    if any(bw in txt for bw in bad_words):
        continue
        
    # History check
    res_hist = ENGINE.check_duplicate_against_history(txt, txt)
    if res_hist['is_duplicate']:
        continue
        
    # DB check
    c_tokens = ENGINE._normalize_persian_tokens(txt)
    c_ngrams = ENGINE._extract_ngrams(txt, 4)
    if len(c_tokens) < 4:
        continue
    db_dup = False
    for s_id, s_title, s_txt in existing_db_texts:
        s_tokens = ENGINE._normalize_persian_tokens(s_txt)
        overlap = len(c_tokens & s_tokens) / max(1, min(len(c_tokens), len(s_tokens)))
        s_ngrams = ENGINE._extract_ngrams(s_txt, 4)
        common_ngrams = c_ngrams & s_ngrams
        if len(common_ngrams) >= 2 or overlap >= 0.40:
            db_dup = True
            break
    if db_dup:
        continue
        
    clean_pool.append(r)

print(f"\n================ CLEAN NON-DUPLICATE REELS: {len(clean_pool)} ================\n")
for cp in clean_pool:
    print(f"[{cp['shortcode']}] Lines: {cp['lines']} | Source: {cp['file']}")
    print(cp['raw_text'].splitlines()[0][:45])
    print('-----------------------------------------')
