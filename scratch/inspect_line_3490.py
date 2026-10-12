import sys, os, json
sys.stdout.reconfigure(encoding='utf-8')

transcript_path = r'C:\Users\User\.gemini\antigravity\brain\d37947c8-66d0-4e58-8673-1026fd69400a\.system_generated\logs\transcript_full.jsonl'

with open(transcript_path, 'r', encoding='utf-8', errors='ignore') as f:
    for idx, line in enumerate(f):
        if 3485 <= idx <= 3495:
            obj = json.loads(line)
            print(f"Line {idx}: type={obj.get('type')}, source={obj.get('source')}")
            cnt = json.dumps(obj, ensure_ascii=False)
            print("  ", cnt[:400])
