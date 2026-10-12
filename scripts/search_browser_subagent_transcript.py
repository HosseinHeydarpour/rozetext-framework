import json, sys, os, re
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from server import ENGINE

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

db_texts = [(s.get('content') or '') + ' ' + (s.get('extracted_raw_text') or '') for s in db['scripts']]
db_urls = {s.get('source_url', '').rstrip('/') for s in db['scripts'] if s.get('source_url')}
db_codes = {u.split('/reel/')[-1].split('/')[0] for u in db_urls if '/reel/' in u}

already_selected = {
    'C5WPI8OCK4x', 'DZDRxCkNgjw', 'DZSr1vMN1mr', 'DPjI0mTCIPs', 
    'DKm6Qn6I9vQ', 'DPRj9ddCF5T', 'DbyY0F7tmAn', 'Dd9GQ7HsdZM', 'DdEeNFfs5V3'
}

codes = [
    ('DOnUbbeiGfj', '4.7M', '@blacktext'),
    ('DdeT1ecMq7y', '1M+', '@text.love400'),
    ('DdPE-C_ODtV', '1M+', '@text.love400'),
    ('DdlvvoVsbv', '1M', '@delltherapy'),
    ('DZ5TIO_tUb0', '1.1M', '@heliumm.__'),
    ('DZ74wmvR17q', '1M', '@heliumm.__'),
    ('DZAn8Tht71I', '1M+', '@heliumm.__'),
    ('DZDGR5kN23g', '1.4M', '@heliumm.__'),
    ('DZXLPfVi2Ea', '1.9M', '@imazhart'),
    ('DZfpEkiPl1q', '3.7M', '@imazhart'),
    ('C92muGvCeQU', '12.6M', '@heliumm.__')
]

p = r'C:\Users\User\.gemini\antigravity\brain\3235565d-9c9f-4548-8b04-ad573c2c10ba\.system_generated\logs\transcript.jsonl'
full_p = r'C:\Users\User\.gemini\antigravity\brain\3235565d-9c9f-4548-8b04-ad573c2c10ba\.system_generated\logs\transcript_full.jsonl'

print("Searching transcript of browser subagent for these codes...")

found_texts = {}

with open(p, 'r', encoding='utf-8', errors='ignore') as f:
    for line_idx, line in enumerate(f):
        for c, v, acc in codes:
            if c in line:
                try:
                    d = json.loads(line)
                    c_text = d.get('content', '')
                    if c not in found_texts:
                        found_texts[c] = []
                    found_texts[c].append((line_idx, c_text))
                except Exception:
                    pass

for c, v, acc in codes:
    print(f"\n=== Code: {c} ({v} - {acc}) ===")
    in_db = (c in db_codes) or (c in already_selected)
    print(f"In DB: {in_db}")
    entries = found_texts.get(c, [])
    print(f"Mentions in transcript: {len(entries)}")
    for lidx, txt in entries[:3]:
        # print snippet
        lines = [l for l in txt.splitlines() if len(l.strip()) > 5]
        print(f"  Line {lidx}: {len(lines)} lines")
        for sl in lines[:6]:
            print(f"    {sl[:100]}")
