import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

scripts = db.get('scripts', [])
print(f"Total scripts: {len(scripts)}")

by_archetype = {}
for s in scripts:
    arch = s.get('archetype', 'نامشخص')
    m = re.search(r'آرکتایپ\s*[۱-۶1-6]', arch)
    arch_key = m.group(0) if m else 'نامشخص'
    by_archetype.setdefault(arch_key, []).append(s)

for arch, items in sorted(by_archetype.items()):
    urls = [it.get('source_url') for it in items if it.get('source_url')]
    print(f"{arch}: {len(items)} scripts | {len(urls)} with source_url")
    for u in urls[:2]:
        print(f"   - {u}")
