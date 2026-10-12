import os
import sys
import json
from post_maker import render_cover, render_post_text, clean_hook_text, get_slot_theme

sys.stdout.reconfigure(encoding='utf-8')

with open(r'd:\rozetext-framework\data\scripts-db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

# Find 2026-10-07 slot 1 and slot 4
scripts = {s.get('scheduled_slot'): s for s in db.get('scripts', []) if s.get('scheduled_date') == '2026-10-07'}

os.makedirs('tests/output', exist_ok=True)

for slot in [1, 4]:
    s = scripts.get(slot)
    if not s:
        print(f"Slot {slot} not found")
        continue
    theme = get_slot_theme(slot)
    hook = clean_hook_text(s.get('hook'), s.get('title'), s.get('content'))
    print(f"Slot {slot} ({theme}): Hook = {hook}")
    
    # Render cover
    im_c = render_cover(hook, theme)
    p_c = f"tests/output/test_slot_{slot}_cover.png"
    im_c.save(p_c)
    print(f"Saved cover: {p_c}")
    
    # Render text
    im_t = render_post_text(s.get('content'), s.get('hook'), s.get('punchline'), theme)
    p_t = f"tests/output/test_slot_{slot}_text.png"
    im_t.save(p_t)
    print(f"Saved text: {p_t}")

print("Test rendering finished successfully!")
