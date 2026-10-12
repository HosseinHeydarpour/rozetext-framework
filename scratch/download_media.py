import re
import urllib.request
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\User\.gemini\antigravity\brain\d37947c8-66d0-4e58-8673-1026fd69400a\.system_generated\steps\1939\content.md', 'r', encoding='utf-8') as f:
    html = f.read()

# Search for og:image
og_images = re.findall(r'<meta property="og:image" content="([^"]+)"', html)
print("OG Image:", og_images)

# Search for any mp4 or video urls
mp4s = re.findall(r'https://[^"\'\s<>]+?\.mp4[^"\'\s<>]*', html)
print("MP4s found:", len(mp4s))
if mp4s:
    clean_url = mp4s[0].replace('&amp;', '&')
    print("MP4 URL:", clean_url[:120])
    # download it
    try:
        urllib.request.urlretrieve(clean_url, 'scratch_reel.mp4')
        print("Successfully downloaded scratch_reel.mp4")
    except Exception as e:
        print("Failed to download mp4:", e)

if og_images:
    clean_img = og_images[0].replace('&amp;', '&')
    try:
        urllib.request.urlretrieve(clean_img, 'scratch_cover.jpg')
        print("Successfully downloaded scratch_cover.jpg")
    except Exception as e:
        print("Failed to download cover:", e)
