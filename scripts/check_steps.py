import sys, json
sys.stdout.reconfigure(encoding='utf-8')
p = r"C:\Users\User\.gemini\antigravity\brain\405948d2-7b88-4cb1-837a-8cabfc4f439f\.system_generated\logs\transcript.jsonl"
with open(p, 'r', encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)
        idx = data.get('step_index', 0)
        if 130 <= idx <= 210:
            calls = data.get('tool_calls', [])
            for c in calls:
                cmd = c.get('args', {}).get('CommandLine') or c.get('args', {}).get('TargetFile')
                print(f"Step {idx}: {c.get('name')} -> {cmd}")
