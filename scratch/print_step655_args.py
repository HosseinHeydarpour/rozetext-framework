import sys, os, json
sys.stdout.reconfigure(encoding='utf-8')

path = r'C:\Users\User\.gemini\antigravity\brain\3235565d-9c9f-4548-8b04-ad573c2c10ba\.system_generated\logs\transcript.jsonl'
with open(path, 'r', encoding='utf-8', errors='ignore') as f:
    for line in f:
        obj = json.loads(line)
        if obj.get('step_index') == 655:
            tc = obj.get('tool_calls', [])
            for call in tc:
                print("Tool Name:", call.get('name'))
                args = call.get('args', {})
                msg = args.get('Message', '')
                print(f"Message length: {len(msg)}")
                print("Message Content:\n", msg)
