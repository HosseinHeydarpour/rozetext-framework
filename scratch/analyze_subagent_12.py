import sys, os, re, json
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath('.'))
from server import PublisherEngine

engine = PublisherEngine()

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

db_urls = set(s.get('source_url', '').strip() for s in db.get('scripts', []))

with open('scratch/subagent_12_reels_full.txt', 'r', encoding='utf-8') as f:
    text = f.read()

# Split by reel items: ### 1. or ### ۱.
blocks = re.split(r'\n(?=###\s*[۰-۹\d]+\.)', text)
print(f"Total blocks in subagent message: {len(blocks)}")

for i, b in enumerate(blocks):
    m_url = re.search(r'https://www\.instagram\.com/reel[s]?/([A-Za-z0-9_-]+)/?', b)
    if not m_url:
        continue
    url = m_url.group(0)
    code = m_url.group(1)
    
    m_views = re.search(r'بازدید دقیق.*?:\s*\*?([^\n\r\*]+)', b)
    v_str = m_views.group(1).strip() if m_views else ""
    
    m_page = re.search(r'آیدی پیج.*?:\s*`?@?([A-Za-z0-9_\.]+)`?', b)
    p_str = m_page.group(1) if m_page else ""
    
    m_arch = re.search(r'آرکتایپ.*?:\s*\*?([^\n\r\*]+)', b)
    arch = m_arch.group(1).strip() if m_arch else ""
    
    # extract code block
    m_code = re.search(r'```text\s*([\s\S]*?)```', b)
    raw = m_code.group(1).strip() if m_code else ""
    lines = [l.strip() for l in raw.splitlines() if l.strip()]
    
    dup = engine.check_duplicate_against_history(raw, raw)
    in_db = url in db_urls or code in str(db_urls)
    
    print(f"\n================ REEL #{i} [{code}] ================")
    print(f"URL: {url} | Page: @{p_str} | Views: {v_str}")
    print(f"Lines count: {len(lines)} | In DB: {in_db} | Dup: {dup['is_duplicate']} ({dup['similarity_score']:.1f}%) | Closest: Reel #{dup.get('duplicate_of_reel')}")
    print(f"Archetype: {arch}")
    print(f"Hook: {lines[0] if lines else ''}")
