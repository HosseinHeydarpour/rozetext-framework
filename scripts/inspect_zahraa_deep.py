import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('downloads/zahraa_deep_high.json', encoding='utf-8') as f:
    data = json.load(f)

# Load existing approved
with open('data/approved_24_reels.json', encoding='utf-8') as f:
    app24 = json.load(f)
app_ids = {a['id'] for a in app24}
app_ids.update({'DdeYIgZqlG9', 'DdhIZDEK8_S', 'DdotWXnCiBy', 'DdzFv9hCAZO', 'DeHxCX3i3xc', 'Ded4vxjsQX3'})

print(f"Total in zahraa_deep_high: {len(data)}")
for it in data:
    code = it.get('code')
    vstr = it.get('views_str')
    vnum = it.get('views_num')
    frame_exists = os.path.exists(f"downloads/frames/{code}_frame.png")
    is_app = code in app_ids
    print(f"{code:<15} | {vstr:<6} | {vnum:10,.0f} | App: {str(is_app):<5} | Frame: {frame_exists}")
