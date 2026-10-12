import sys, os, json
sys.stdout.reconfigure(encoding='utf-8')

path = r'C:\Users\User\.gemini\antigravity\brain\3235565d-9c9f-4548-8b04-ad573c2c10ba\.system_generated\logs\transcript_full.jsonl'
with open(path, 'r', encoding='utf-8', errors='ignore') as f:
    for line in f:
        obj = json.loads(line)
        if obj.get('step_index') == 655:
            tc = obj.get('tool_calls', [])
            for call in tc:
                args = call.get('args', {})
                msg = args.get('Message', '')
                with open('scratch/subagent_12_reels_full.txt', 'w', encoding='utf-8') as out:
                    out.write(msg)
                print("Written to scratch/subagent_12_reels_full.txt, length:", len(msg))
