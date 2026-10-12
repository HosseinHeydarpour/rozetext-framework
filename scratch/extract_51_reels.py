import json

path = r'C:\Users\User\.gemini\antigravity\brain\3235565d-9c9f-4548-8b04-ad573c2c10ba\.system_generated\logs\transcript_full.jsonl'
with open(path, 'r', encoding='utf-8', errors='ignore') as f:
    for idx, line in enumerate(f):
        if idx == 279:
            data = json.loads(line)
            content = data.get('content', '')
            s = content.find('```json')
            e = content.find('```', s + 7)
            raw = content[s+7:e].strip()
            parsed = json.loads(raw)
            reels = parsed.get('millionReels', [])
            print(f'Total reels: {len(reels)}')
            for r in reels:
                print(f"{r['id']}: {r['views']}")
            with open('scratch/reels_51.json', 'w', encoding='utf-8') as out:
                json.dump(reels, out, ensure_ascii=False, indent=2)
            break
