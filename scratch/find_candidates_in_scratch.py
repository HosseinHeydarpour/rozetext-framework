import sys, os, re, json, glob
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath('.'))
from server import PublisherEngine

engine = PublisherEngine()

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

all_db_urls = set()
all_db_codes = set()
for s in db.get('scripts', []):
    u = s.get('source_url', '')
    if u:
        all_db_urls.add(u.strip())
        code = u.strip().rstrip('/').split('/')[-1]
        all_db_codes.add(code)

already_picked = {
    'C5WPI8OCK4x', 'DZDRxCkNgjw', 'DNTYt15oqYj', 'DZSr1vMN1mr',
    'DPjI0mTCIPs', 'DKm6Qn6I9vQ', 'DQHm9z6CMeL'
}

print(f"Scanning all scratch files...")

scratch_files = glob.glob('scratch/*.py') + glob.glob('scratch/*.txt')

found_candidates = {}

for sf in scratch_files:
    if os.path.basename(sf) in ['scan_all_txt_for_million.py', 'inspect_transcript_lines.py', 'scan_transcript_for_reels.py', 'search_unused_transcript_reels.py']:
        continue
    try:
        with open(sf, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception:
        continue
        
    # Find all reel codes
    codes = set(re.findall(r'https?://(?:www\.)?instagram\.com/reel[s]?/([A-Za-z0-9_-]+)/?', content))
    for code in codes:
        if code in all_db_codes or code in already_picked or code in found_candidates:
            continue
        # Find context
        idx = content.find(code)
        block = content[max(0, idx-300):min(len(content), idx+1500)]
        
        # Check views
        m_v = re.search(r'(\d+(?:\.\d+)?\s*(?:M|میلیون))', block)
        m_dig = re.findall(r'[\d,٬]{7,}', block)
        views_str = ""
        is_m = False
        if m_v and '0.' not in m_v.group(1):
            views_str = m_v.group(1)
            is_m = True
        elif m_dig:
            views_str = m_dig[0]
            is_m = True
            
        if not is_m:
            continue
            
        # Try extract text
        m_t = re.search(r'(?:extracted_raw_text|content|متن دقیق داخل ویدیو|متن ویدیو)[\s\'":=«]+([\s\S]*?)(?:[\'"]\s*,|»|\n\s*caption|\n\s*متن دقیق کپشن|\n\s*score|$)', block)
        raw_text = m_t.group(1).strip() if m_t else ""
        raw_text = re.sub(r'—\s*وحیدرضا خوش‌بیان', '', raw_text).strip()
        lines = [l.strip() for l in raw_text.splitlines() if l.strip()]
        
        if len(lines) >= 6:
            dup = engine.check_duplicate_against_history(raw_text, raw_text)
            if not dup['is_duplicate']:
                found_candidates[code] = {
                    'code': code,
                    'file': os.path.basename(sf),
                    'views': views_str,
                    'lines': len(lines),
                    'sim': dup['similarity_score'],
                    'hook': lines[0] if lines else '',
                    'text': raw_text
                }

print(f"\nFresh 1M+ candidates found in scratch: {len(found_candidates)}")
for c, info in found_candidates.items():
    print(f"- {c} [{info['views']}] from {info['file']} | Lines: {info['lines']} | Sim: {info['sim']:.1f}%")
    print(f"   Hook: {info['hook']}")
