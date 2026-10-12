import sys, os, json, re
sys.stdout.reconfigure(encoding='utf-8')

path = r'C:\Users\User\.gemini\antigravity\brain\3235565d-9c9f-4548-8b04-ad573c2c10ba\.system_generated\logs\transcript_full.jsonl'

print("Scanning subagent transcript for messages and tool calls...")

with open(path, 'r', encoding='utf-8', errors='ignore') as f:
    for idx, line in enumerate(f):
        try:
            obj = json.loads(line)
        except:
            continue
        # Check send_message calls
        tc = obj.get('tool_calls', [])
        for call in tc:
            if call.get('name') == 'send_message':
                msg = call.get('args', {}).get('Message', '')
                print(f"Step {obj.get('step_index')}: send_message (len={len(msg)})")
                first_lines = msg.splitlines()[:3]
                print("   Snippet:", " | ".join(first_lines))
                # If it mentions reels, print how many reels
                m_reels = re.findall(r'https://www\.instagram\.com/reel/([A-Za-z0-9_-]+)/', msg)
                if m_reels:
                    print(f"   Contains {len(m_reels)} reel URLs: {m_reels[:5]}...")
