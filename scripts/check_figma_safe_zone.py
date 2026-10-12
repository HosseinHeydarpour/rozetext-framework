import urllib.request
import json
import sys

import os

sys.stdout.reconfigure(encoding='utf-8')
token = os.environ.get('FIGMA_TOKEN', '')
file_key = 'WY3tdDSMwF6WiXVQRwY4t1'
url = f'https://api.figma.com/v1/files/{file_key}?depth=6'

req = urllib.request.Request(url, headers={'X-Figma-Token': token})
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode('utf-8'))

for page in data.get('document', {}).get('children', []):
    for sec in page.get('children', []):
        for c in sec.get('children', []):
            name = c.get('name')
            nid = c.get('id')
            ntype = c.get('type')
            bbox = c.get('absoluteBoundingBox')
            print(f"Sec: {sec.get('name')} | Node: {name} ({nid}, {ntype}) | BBox: {bbox}")
