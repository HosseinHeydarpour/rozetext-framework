import sys, os, json, re
sys.stdout.reconfigure(encoding='utf-8')

transcript_path = r'C:\Users\User\.gemini\antigravity\brain\d37947c8-66d0-4e58-8673-1026fd69400a\.system_generated\logs\transcript_full.jsonl'

lines_to_check = [252, 253, 291, 292, 360, 532, 972]

with open(transcript_path, 'r', encoding='utf-8', errors='ignore') as f:
    for idx, line in enumerate(f):
        if idx in lines_to_check:
            try:
                obj = json.loads(line)
                cnt = obj.get('content', '')
                print(f"\n================ LINE {idx} (type={obj.get('type')}, source={obj.get('source')}) ================")
                print(cnt[:1500])
            except Exception as e:
                print(f"Error parsing line {idx}:", e)
