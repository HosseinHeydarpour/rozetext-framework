import sys, os, json
sys.stdout.reconfigure(encoding='utf-8')

path = r'C:\Users\User\.gemini\antigravity\brain\3235565d-9c9f-4548-8b04-ad573c2c10ba\.system_generated\logs\transcript.jsonl'
lines = []
with open(path, 'r', encoding='utf-8', errors='ignore') as f:
    for line in f:
        lines.append(line)
print(f"Total steps in browser subagent: {len(lines)}")
for l in lines[-5:]:
    obj = json.loads(l)
    print(f"Step {obj.get('step_index')}: type={obj.get('type')}, source={obj.get('source')}")
    if obj.get('content'):
        print("  Content:", obj.get('content')[:200])
