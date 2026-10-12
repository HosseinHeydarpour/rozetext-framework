import sys, os, json, re
sys.stdout.reconfigure(encoding='utf-8')

path = r'C:\Users\User\.gemini\antigravity\brain\3235565d-9c9f-4548-8b04-ad573c2c10ba\.system_generated\logs\transcript_full.jsonl'

test_codes = ['DbyY0F7tmAn', 'DbbPmLFNZbj', 'DPeaox9CPJk', 'DPRj9ddCF5T', 'DO_homTiPTp']

print("Searching subagent transcript for the 5 codes...")
found = {}
with open(path, 'r', encoding='utf-8', errors='ignore') as f:
    for idx, line in enumerate(f):
        for c in test_codes:
            if c in line:
                if c not in found:
                    found[c] = []
                found[c].append(idx)

for c in test_codes:
    print(f"Code {c}: found in steps {found.get(c, [])}")
