import sys, os, json, re
sys.path.insert(0, os.path.abspath('.'))
sys.stdout.reconfigure(encoding='utf-8')
from server import PublisherEngine

engine = PublisherEngine()

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)
db_urls = set(s.get('source_url', '').strip() for s in db.get('scripts', []))

target_codes = [
    'DHy7292o-GE', 'DSODhFciOYd', 'DIKL9gZqM6_', 'DIRfksnIzoB',
    'DUdr6AqDEPn', 'DD9GzMOsZtE', 'DI4PK_6qlED', 'DdM8l12uV5Z',
    'DIb21i1IlXx', 'DHlzMLlI6Ry', 'DR7fbNlCBle', 'DcjQOwtN86T',
    'DMf5pj2oQCN', 'DdhsbU4Iw6x', 'DZX3utUt9xI', 'DdcmkgQuMXn',
    'DObgpFniAm-', 'DSp5q5XiOlJ', 'DcpswZKKnOt', 'DcginLJqSAI',
    'DcLMXYaqcyq', 'Dd0fKajq4Z7', 'DHMRcwUIAiZ', 'DJRtdV1oHYS',
    'C_8r9QeuqGO', 'DFQdHbroYkK', 'DFItKaKI-VS', 'DE2rzgOoJVJ',
    'DDclLBvIrOw'
]

transcript_path = r'C:\Users\User\.gemini\antigravity\brain\d37947c8-66d0-4e58-8673-1026fd69400a\.system_generated\logs\transcript_full.jsonl'

print(f"Scanning for {len(target_codes)} target codes...")

found_data = {}

# Check files first
files_to_check = [
    r'D:\rozetext content\top_50_viral_delneveshte_reels.txt',
    r'D:\rozetext content\top_50_viral_delneveshte_batch_01.txt',
    r'D:\rozetext content\top_50_viral_delneveshte_batch_02.txt',
    r'D:\rozetext content\top_15_viral_delneveshte_reels.txt'
]

for fp in files_to_check:
    if not os.path.exists(fp):
        continue
    with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()
    for code in target_codes:
        if code in text and code not in found_data:
            idx = text.find(code)
            block = text[max(0, idx-200):min(len(text), idx+2000)]
            found_data[code] = ('file:' + os.path.basename(fp), block)

# Also check transcript
with open(transcript_path, 'r', encoding='utf-8', errors='ignore') as f:
    for line in f:
        for code in target_codes:
            if code in line and code not in found_data:
                idx = line.find(code)
                block = line[max(0, idx-200):min(len(line), idx+2500)]
                found_data[code] = ('transcript', block)

print(f"Total found among targets: {len(found_data)}")

for code, (src, block) in found_data.items():
    # Try extract in-video text
    m_text = re.search(r'متن(?: دقیق)?(?: داخل)? ویدیو.*?:?\s*\n«?([\s\S]*?)»?\s*(?:\n\s*-|\n\s*متن دقیق کپشن|\n\s*کپشن|$)', block)
    raw_text = m_text.group(1).strip() if m_text else ""
    raw_text = re.sub(r'—\s*وحیدرضا خوش‌بیان', '', raw_text).strip()
    lines = [l.strip() for l in raw_text.split('\n') if l.strip()]
    
    dup = engine.check_duplicate_against_history(raw_text, raw_text) if raw_text else {'is_duplicate': False, 'similarity_score': 0}
    
    # check views
    m_v = re.search(r'(?:آمار|ویو|بازدید|views)[\s:]*([^\n\r]+)', block, re.IGNORECASE)
    v_str = m_v.group(1) if m_v else ""
    
    print(f"\n================ CODE: {code} [{src}] ================")
    print(f"Views: {v_str}")
    print(f"Lines: {len(lines)} | Dup: {dup['is_duplicate']} ({dup['similarity_score']:.1f}%)")
    if lines:
        print(f"Hook: {lines[0]}")
        print("Sample (first 3 lines):", " / ".join(lines[:3]))
