import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
with open('data/benchmark_accounts.json', encoding='utf-8') as f:
    d = json.load(f)
accounts = d.get('accounts', [])
print(f"Total benchmark accounts: {len(accounts)}")
for i, acc in enumerate(accounts[:30], 1):
    handle = acc.get('handle')
    fol = acc.get('followers')
    name = acc.get('name_fa')
    top = acc.get('top_views_recorded', '')
    print(f"{i:2d}. {handle:<22} | {fol:<15} | {top:<15} | {name}")
