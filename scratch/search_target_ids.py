import sys, os, json, re
sys.stdout.reconfigure(encoding='utf-8')

path = r'C:\Users\User\.gemini\antigravity\brain\3235565d-9c9f-4548-8b04-ad573c2c10ba\.system_generated\logs\transcript_full.jsonl'

target_ids = [
    'DPeaox9CPJk', 'DPRj9ddCF5T', 'DO_homTiPTp', 'DHOoHu0IiOA',
    'DGvs7wdI8m9', 'DGYhwC9osq5', 'DGQzWJsoXkB', 'DF-yFaKo9mG',
    'DFavqaEIMl_', 'DFVldo0ITUD', 'DEaZbyVoEze', 'DDuqExPo0xZ',
    'DDpblWFow7g'
]

print("Searching for metadata of targets in subagent transcript...")
found_steps = {}
with open(path, 'r', encoding='utf-8', errors='ignore') as f:
    for idx, line in enumerate(f):
        for tid in target_ids:
            if tid in line:
                found_steps.setdefault(tid, []).append(idx)

for tid in target_ids:
    print(f"- {tid}: found in steps {found_steps.get(tid, [])}")
