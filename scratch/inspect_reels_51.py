import json, sys
sys.stdout.reconfigure(encoding='utf-8')
with open('scratch/reels_51.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
for i, item in enumerate(data):
    print(f"{i+1}. id={item.get('id')} views={item.get('views')} href={item.get('href')}")
