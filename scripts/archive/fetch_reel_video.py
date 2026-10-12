import urllib.request
import json
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.9',
}

url = 'https://www.instagram.com/reel/DZQJRhRNpQG/?__a=1&__d=dis'
req = urllib.request.Request(url, headers=headers)

try:
    with urllib.request.urlopen(req) as resp:
        data = resp.read().decode('utf-8')
        try:
            j = json.loads(data)
            print("Fetched json successfully!")
            # search for video url
            items = j.get('items', [])
            if items:
                video_versions = items[0].get('video_versions', [])
                if video_versions:
                    print("Video URL:", video_versions[0]['url'])
                    urllib.request.urlretrieve(video_versions[0]['url'], 'reel_video.mp4')
                    print("Downloaded reel_video.mp4!")
        except Exception as e:
            print("Failed json parse:", e, data[:200])
except Exception as e:
    print("Request failed:", e)
