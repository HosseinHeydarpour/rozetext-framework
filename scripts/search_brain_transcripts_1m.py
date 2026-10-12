import sys, os, re, json
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from server import ENGINE

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

# DB scripts
existing_db = []
for s in db.get('scripts', []):
    t = (s.get('content') or '') + ' ' + (s.get('extracted_raw_text') or '')
    if t.strip():
        existing_db.append(t.strip())

brain_dir = r"C:\Users\User\.gemini\antigravity\brain"
reel_regex = re.compile(r'https?://(?:www\.)?instagram\.com/reel/([A-Za-z0-9_-]+)/?', re.IGNORECASE)

# Let's collect candidates with text
found_candidates = {}

for root, dirs, files in os.walk(brain_dir):
    for f in files:
        if f.endswith(('.md', '.txt', '.json', '.jsonl')):
            p = os.path.join(root, f)
            try:
                with open(p, 'r', encoding='utf-8', errors='ignore') as fp:
                    content = fp.read()
            except Exception:
                continue
                
            for m in reel_regex.finditer(content):
                code = m.group(1)
                if code in found_candidates:
                    continue
                # Search window
                start = max(0, m.start() - 1500)
                end = min(len(content), m.end() + 2500)
                win = content[start:end]
                
                # Check for 1M+ views
                has_1m = False
                view_str = ""
                for vm in re.finditer(r'(\d+(?:\.\d+)?\s*(?:M|میلیون))', win, re.IGNORECASE):
                    val = vm.group(1)
                    if '0.' not in val:
                        has_1m = True
                        view_str = val
                        break
                if not has_1m:
                    continue
                    
                # Look for raw text or content
                # Search for "content": "..." or "extracted_raw_text": "..." or blocks
                extracted_text = None
                cm = re.search(r'["\'](?:content|extracted_raw_text)["\']:\s*"""(.*?)"""', win, re.DOTALL)
                if not cm:
                    cm = re.search(r'["\'](?:content|extracted_raw_text)["\']:\s*"([^"\\]*(?:\\.[^"\\]*)*)"', win, re.DOTALL)
                    if cm:
                        extracted_text = cm.group(1).encode('utf-8').decode('unicode_escape', errors='ignore')
                else:
                    extracted_text = cm.group(1)
                    
                if not extracted_text:
                    # Look for markdown block
                    bm = re.search(r'\*\*متن.*?:\*\*\s*(.*?)(?:\n\n|\Z|\*\*)', win, re.DOTALL)
                    if bm:
                        extracted_text = bm.group(1)
                        
                if not extracted_text or not extracted_text.strip():
                    continue
                    
                extracted_text = extracted_text.replace('\\n', '\n').strip()
                lines = [l.strip() for l in extracted_text.splitlines() if l.strip()]
                if len(lines) < 7 or len(lines) > 16:
                    continue
                    
                # Check duplicates
                res_hist = ENGINE.check_duplicate_against_history(extracted_text, extracted_text)
                if res_hist['is_duplicate']:
                    continue
                    
                c_tokens = ENGINE._normalize_persian_tokens(extracted_text)
                c_ngrams = ENGINE._extract_ngrams(extracted_text, 4)
                if len(c_tokens) < 4:
                    continue
                    
                db_dup = False
                for dbt in existing_db:
                    s_tokens = ENGINE._normalize_persian_tokens(dbt)
                    overlap = len(c_tokens & s_tokens) / max(1, min(len(c_tokens), len(s_tokens)))
                    s_ngrams = ENGINE._extract_ngrams(dbt, 4)
                    common_ngrams = c_ngrams & s_ngrams
                    if len(common_ngrams) >= 2 or overlap >= 0.40:
                        db_dup = True
                        break
                if db_dup:
                    continue
                    
                # Persona check
                bad_words = ['مولانا', 'شمس تبریزی', 'شمس', 'دختر', 'پسر', 'تولد', 'روز زن', 'روز مادر', 'روز پدر', 'یلدا', 'نوروز']
                if any(bw in extracted_text for bw in bad_words):
                    continue
                    
                # Page check
                if '@halekhoub' in win or 'halekhoub' in win:
                    continue
                    
                found_candidates[code] = {
                    'code': code,
                    'views': view_str,
                    'lines': len(lines),
                    'text': extracted_text,
                    'source': f
                }

print(f"\n================ FOUND {len(found_candidates)} VERIFIED CANDIDATES ================\n")
for c, item in found_candidates.items():
    print(f"[{c}] Views: {item['views']} | Lines: {item['lines']} | File: {item['source']}")
    print(item['text'][:120].replace('\n', ' / '))
    print('----------------------------------------')
