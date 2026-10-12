import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('data/hunted-42-reels-batch-verified.json', 'r', encoding='utf-8') as f:
    batch = json.load(f)

with open('published-content-history.md', 'r', encoding='utf-8') as f:
    history_text = f.read()

with open('data/scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

db_scripts = db.get('scripts', [])
published_ids = {s.get('id') for s in db_scripts if s.get('published')}
published_urls = {s.get('source_url') for s in db_scripts if s.get('published') and s.get('source_url')}

print(f"Total verified batch: {len(batch)}")
print(f"Total db scripts: {len(db_scripts)} (Published: {len(published_ids)})")

# Check status of each item in 42-batch
print("\n=== STATUS OF ALL 42 REELS IN BATCH ===")
for i, item in enumerate(batch, 1):
    url = item.get('source_url', '')
    url_code = url.split('/reel/')[-1].split('/')[0] if '/reel/' in url else ''
    in_hist = url_code and (url_code in history_text)
    is_pub_db = url in published_urls
    
    status = "PUBLISHED" if (in_hist or is_pub_db) else "AVAILABLE"
    print(f"#{i:02d} [{status}] ({item.get('source_views')}) - {item.get('title')}")
