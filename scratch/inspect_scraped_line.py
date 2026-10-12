import sys, os, json, re
sys.stdout.reconfigure(encoding='utf-8')

transcript_path = r'C:\Users\User\.gemini\antigravity\brain\d37947c8-66d0-4e58-8673-1026fd69400a\.system_generated\logs\transcript_full.jsonl'

with open(transcript_path, 'r', encoding='utf-8', errors='ignore') as f:
    for idx, line in enumerate(f):
        if 'vahidrezakhoshbayan/reel' in line and ('views":' in line or 'views\\":' in line):
            print(f"Match on line {idx}:")
            matches = re.findall(r'\{[^{}]*?"id"[^{}]*?"views"[^{}]*?\}', line)
            print(f"Found {len(matches)} items in line {idx}")
            for m in matches[:20]:
                print(" ", m)
