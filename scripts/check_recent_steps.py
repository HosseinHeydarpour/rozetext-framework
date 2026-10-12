import json, sys
sys.stdout.reconfigure(encoding='utf-8')
p = r'C:\Users\User\.gemini\antigravity\brain\d37947c8-66d0-4e58-8673-1026fd69400a\.system_generated\logs\transcript.jsonl'
with open(p, 'r', encoding='utf-8', errors='ignore') as f:
    for line in f:
        try:
            d = json.loads(line)
        except Exception:
            continue
        step = d.get('step_index', 0)
        c = d.get('content', '')
        if 'CLEAN PASS' in c or 'DdEeNFfs5V3' in c or 'Dd9GQ7HsdZM' in c or 'test_final_2' in c:
            print(f"Step {step}:")
            for cl in c.splitlines()[:5]:
                print("  ", cl[:120])
