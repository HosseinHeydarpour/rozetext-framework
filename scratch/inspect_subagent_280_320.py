import json, sys
sys.stdout.reconfigure(encoding='utf-8')

path = r'C:\Users\User\.gemini\antigravity\brain\3235565d-9c9f-4548-8b04-ad573c2c10ba\.system_generated\logs\transcript_full.jsonl'
with open(path, 'r', encoding='utf-8', errors='ignore') as f:
    for idx, line in enumerate(f):
        if 280 <= idx <= 320:
            data = json.loads(line)
            c = data.get('content', '')
            tc = str(data.get('tool_calls', ''))
            txt = c if c else tc
            if 'ogTitle' in txt or 'desc' in txt:
                print(f"=== STEP {idx} ===")
                print(txt[:1000])
