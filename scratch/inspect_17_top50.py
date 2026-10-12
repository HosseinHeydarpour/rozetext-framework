import sys, os, json
sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('./scratch'))
sys.stdout.reconfigure(encoding='utf-8')
import parse_top50_correct

print('=== ALL 17 1M+ REELS IN TOP 50 REELS TXT ===')
for c in parse_top50_correct.candidates:
    print(f"- {c['code']} ({c['page']}) | inDB={c['in_db']} | Dup={c['is_dup']} ({c['sim']:.1f}%) | {c['views_str']}")
    print(f"   Hook: {c['raw_text'].splitlines()[0]}")
