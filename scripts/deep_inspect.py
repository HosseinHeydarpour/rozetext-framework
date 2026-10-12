import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
with open('scratch_figma_post.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

def inspect_node_deep(node, prefix=''):
    name = node.get('name')
    nid = node.get('id')
    ntype = node.get('type')
    bbox = node.get('absoluteBoundingBox')
    print(f"{prefix}[{ntype}] {name} ({nid}) bbox: {bbox}")
    
    # check fills
    fills = node.get('fills', [])
    for idx, f in enumerate(fills):
        ftype = f.get('type')
        if ftype == 'IMAGE':
            print(f"{prefix}   Fill {idx}: IMAGE ref={f.get('imageRef')}")
        elif ftype == 'SOLID':
            c = f.get('color', {})
            opacity = f.get('opacity', 1.0)
            r, g, b = int(c.get('r', 0)*255), int(c.get('g', 0)*255), int(c.get('b', 0)*255)
            print(f"{prefix}   Fill {idx}: SOLID #{r:02X}{g:02X}{b:02X} opacity={opacity}")
            
    # check text
    if ntype == 'TEXT':
        style = node.get('style', {})
        font_name = style.get('fontFamily')
        font_weight = style.get('fontWeight')
        font_size = style.get('fontSize')
        line_height = style.get('lineHeightPx')
        align = style.get('textAlignHorizontal')
        chars = node.get('characters', '')
        print(f"{prefix}   Text: Font={font_name} Weight={font_weight} Size={font_size} LineH={line_height} Align={align}")
        print(f"{prefix}   Chars: {repr(chars)}")
        overrides = node.get('characterStyleOverrides', [])
        override_table = node.get('styleOverrideTable', {})
        if overrides:
            print(f"{prefix}   Overrides count: {len(overrides)}, table: {override_table}")
            
    for c in node.get('children', []):
        inspect_node_deep(c, prefix + '  ')

doc = data.get('nodes', {}).get('8568:67', {}).get('document', {})
for child in doc.get('children', []):
    if any(k in child.get('name', '') for k in ['Dark', 'Light']):
        print('='*60)
        inspect_node_deep(child)
