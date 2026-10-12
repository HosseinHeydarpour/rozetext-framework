import sys, json
sys.stdout.reconfigure(encoding='utf-8')
path = r'C:\Users\User\.gemini\antigravity\brain\3235565d-9c9f-4548-8b04-ad573c2c10ba\.system_generated\logs\transcript_full.jsonl'
with open(path, 'r', encoding='utf-8', errors='ignore') as f:
    for idx, line in enumerate(f):
        if idx in [295, 296, 297, 302]:
            obj = json.loads(line)
            print(f"=== STEP {idx} ({obj.get('type')}) ===")
            content = str(obj.get('content') or obj.get('tool_calls') or '')
            print(content[:1500])
