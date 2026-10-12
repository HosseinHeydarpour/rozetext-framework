import sys, os, json
sys.stdout.reconfigure(encoding='utf-8')

path = r'C:\Users\User\.gemini\antigravity\brain\3235565d-9c9f-4548-8b04-ad573c2c10ba\.system_generated\logs\transcript_full.jsonl'

with open(path, 'r', encoding='utf-8', errors='ignore') as f:
    for line in f:
        obj = json.loads(line)
        if obj.get('step_index') == 297:
            cnt = obj.get('content', '')
            # find DbyY0F7tmAn
            idx = cnt.find('DbyY0F7tmAn')
            print("=== DbyY0F7tmAn in Step 297 ===")
            print(cnt[idx:idx+800])
        elif obj.get('step_index') == 279:
            cnt = obj.get('content', '')
            print("=== Step 279 ===")
            print(cnt[:800])
