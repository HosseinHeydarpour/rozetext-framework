import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
with open('scratch_figma_post.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

doc = data.get('nodes', {}).get('8568:67', {}).get('document', {})

def find_node(n, nid):
    if n.get('id') == nid:
        return n
    for c in n.get('children', []):
        r = find_node(c, nid)
        if r: return r
    return None

dark_text_node = find_node(doc, '8449:16')
if dark_text_node:
    chars = dark_text_node.get('characters', '')
    overrides = dark_text_node.get('characterStyleOverrides', [])
    print(f"Total chars: {len(chars)}, overrides: {len(overrides)}")
    highlighted_segments = []
    current_segment = []
    for idx, (ch, ov) in enumerate(zip(chars, overrides)):
        if ov != 0:
            current_segment.append(ch)
        else:
            if current_segment:
                highlighted_segments.append(''.join(current_segment))
                current_segment = []
    if current_segment:
        highlighted_segments.append(''.join(current_segment))
    print("Highlighted phrases in Dark Text:")
    for h in highlighted_segments:
        print(" ->", repr(h))
