import json, sys
sys.stdout.reconfigure(encoding='utf-8')
p = r'C:\Users\User\.gemini\antigravity\brain\3235565d-9c9f-4548-8b04-ad573c2c10ba\.system_generated\logs\transcript.jsonl'
with open(p, 'r', encoding='utf-8', errors='ignore') as f:
    for line_idx, line in enumerate(f):
        if line_idx >= 680 and line_idx <= 850:
            try:
                d = json.loads(line)
            except Exception:
                continue
            content = d.get('content', '')
            # If there's Persian text or analysis of the images
            if any(k in content for k in ['DZ5TIO_tUb0', 'DZ74wmvR17q', 'DZDGR5kN23g', 'DdeT1ecMq7y', 'DdPE-C_ODtV', 'DZAn8Tht71I']):
                for l in content.splitlines():
                    if any(w in l for w in ['متن', 'سطر', 'line', 'text', 'کپشن', 'خط']):
                        print(f"[{line_idx}] {l[:120]}")
