import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
with open('scratch_figma_post.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

def print_tree(node, indent=0):
    name = node.get('name', 'unnamed')
    nid = node.get('id', '')
    ntype = node.get('type', '')
    chars = ''
    if ntype == 'TEXT':
        raw = node.get('characters', '').replace('\n', ' ')
        chars = f' [Text: "{raw[:50]}..."]'
    print('  ' * indent + f'- {name} (ID: {nid}, Type: {ntype}){chars}')
    for c in node.get('children', []):
        print_tree(c, indent + 1)

doc = data.get('nodes', {}).get('8568:67', {}).get('document', {})
print_tree(doc)
