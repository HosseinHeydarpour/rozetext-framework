import json, sys
sys.stdout.reconfigure(encoding='utf-8')

path = r'C:\Users\User\.gemini\antigravity\brain\3235565d-9c9f-4548-8b04-ad573c2c10ba\.system_generated\logs\transcript_full.jsonl'
with open(path, 'r', encoding='utf-8', errors='ignore') as f:
    for idx, line in enumerate(f):
        if 610 <= idx <= 630:
            data = json.loads(line)
            c = data.get('content', '')
            tc = str(data.get('tool_calls', ''))
            print(f"=== STEP {idx} ===")
            if c:
                print(c[:1500])
            if tc:
                print(tc[:1500])
