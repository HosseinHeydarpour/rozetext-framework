import sys, os, json
sys.stdout.reconfigure(encoding='utf-8')

path = r'C:\Users\User\.gemini\antigravity\brain\3235565d-9c9f-4548-8b04-ad573c2c10ba\.system_generated\logs\transcript_full.jsonl'

with open(path, 'r', encoding='utf-8', errors='ignore') as f:
    for line in f:
        obj = json.loads(line)
        idx = obj.get('step_index')
        if idx in [298, 301, 304, 306]:
            print(f"\n================ STEP {idx} ================")
            cnt = obj.get('content') or json.dumps(obj.get('tool_calls', []), ensure_ascii=False)
            print(cnt[:1200])
