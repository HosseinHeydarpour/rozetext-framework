import sys, json
sys.stdout.reconfigure(encoding='utf-8')
p = r"C:\Users\User\.gemini\antigravity\brain\405948d2-7b88-4cb1-837a-8cabfc4f439f\.system_generated\logs\transcript.jsonl"
with open(p, 'r', encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)
        idx = data.get('step_index', 0)
        if 194 <= idx <= 205:
            cnt = str(data.get('content', ''))
            print(f"Step {idx} ({data.get('type')}): {cnt[:250]}")
