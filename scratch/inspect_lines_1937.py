import sys, os, json
sys.stdout.reconfigure(encoding='utf-8')

transcript_path = r'C:\Users\User\.gemini\antigravity\brain\d37947c8-66d0-4e58-8673-1026fd69400a\.system_generated\logs\transcript_full.jsonl'

with open(transcript_path, 'r', encoding='utf-8', errors='ignore') as f:
    for idx, line in enumerate(f):
        if idx in [1936, 1937, 3782, 3783]:
            obj = json.loads(line)
            print(f"\nLine {idx}: type={obj.get('type')}, source={obj.get('source')}")
            cnt = obj.get('content') or json.dumps(obj.get('tool_calls', []))
            print(cnt[:1000])
