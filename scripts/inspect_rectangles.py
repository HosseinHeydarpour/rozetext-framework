import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
with open('scratch_figma_post.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

doc = data.get('nodes', {}).get('8568:67', {}).get('document', {})
for child in doc.get('children', []):
    if 'Rectangle' in child.get('name', ''):
        nid = child.get('id')
        name = child.get('name')
        bbox = child.get('absoluteBoundingBox')
        fills = child.get('fills', [])
        color_str = ""
        for f in fills:
            if f.get('type') == 'SOLID':
                c = f.get('color', {})
                r, g, b = int(c.get('r', 0)*255), int(c.get('g', 0)*255), int(c.get('b', 0)*255)
                color_str = f"#{r:02X}{g:02X}{b:02X}"
        print(f"{name} ({nid}) Pos: x={bbox.get('x')}, y={bbox.get('y')}, w={bbox.get('width')}, h={bbox.get('height')} Color={color_str}")
