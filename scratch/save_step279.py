import sys, os, json, re
sys.stdout.reconfigure(encoding='utf-8')

path = r'C:\Users\User\.gemini\antigravity\brain\3235565d-9c9f-4548-8b04-ad573c2c10ba\.system_generated\logs\transcript_full.jsonl'

with open(path, 'r', encoding='utf-8', errors='ignore') as f:
    for line in f:
        obj = json.loads(line)
        if obj.get('step_index') == 279:
            cnt = obj.get('content', '')
            with open('scratch/subagent_step279.txt', 'w', encoding='utf-8') as out:
                out.write(cnt)
            print("Wrote step 279, length:", len(cnt))
