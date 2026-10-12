import json, sys
sys.stdout.reconfigure(encoding='utf-8')
p = r'C:\Users\User\.gemini\antigravity\brain\d37947c8-66d0-4e58-8673-1026fd69400a\.system_generated\logs\transcript.jsonl'
with open(p, 'r', encoding='utf-8', errors='ignore') as f:
    for line_idx, line in enumerate(f):
        try:
            d = json.loads(line)
        except Exception:
            continue
        c = d.get('content', '')
        if '3235565d-9c9f-4548-8b04-ad573c2c10ba' in c:
            print(f"Step {d.get('step_index')}: (idx={line_idx})")
            print(c[:400])
            print('-'*50)
