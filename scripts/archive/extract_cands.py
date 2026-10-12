import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
log_path = 'C:/Users/User/.gemini/antigravity/brain/d37947c8-66d0-4e58-8673-1026fd69400a/.system_generated/logs/transcript_full.jsonl'
found_cands = {}

with open(log_path, 'r', encoding='utf-8') as f:
    for line in f:
        obj = json.loads(line)
        for tc in obj.get('tool_calls', []):
            cmd = tc.get('args', {}).get('CommandLine', '')
            # Match any reel patterns
            matches = re.findall(r"['\"]([A-Za-z0-9_-]{9,15})['\"]\s*,\s*(\d{6,8})\s*,\s*(?:r?['\"]{3}|['\"])(.*?)(?:['\"]{3}|['\"])", cmd, re.DOTALL)
            for code, views, txt in matches:
                if code not in found_cands and len(txt.strip().splitlines()) >= 6:
                    found_cands[code] = (int(views), txt.strip())
            # Also check if json or python lists of dicts exist in cmd
            dict_matches = re.findall(r"\{[^{}]*['\"]source_url['\"][^{}]*\}", cmd, re.DOTALL)
            # Or content fields
        content = obj.get('content', '')
        if 'source_url' in content or 'extracted_raw_text' in content:
            # Let's search in content
            pass


print('Found candidates in previous steps:', len(found_cands))
for k, (v, t) in found_cands.items():
    lines = [l.strip() for l in t.splitlines() if l.strip()]
    print(f"{k}: views={v:,}, lines={len(lines)}, hook={lines[0][:50] if lines else ''}")
