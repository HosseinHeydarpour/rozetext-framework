import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

with open("C:/Users/User/.gemini/antigravity/brain/3235565d-9c9f-4548-8b04-ad573c2c10ba/.system_generated/steps/285/output.txt", "r", encoding="utf-8") as f:
    text = f.read()

start = text.find('[{"id":')
end_idx = text.rfind('}]') + 2
items = json.loads(text[start:end_idx])
print(f"Total items in step 285: {len(items)}")

for i, it in enumerate(items):
    views = it.get("views")
    item_id = it.get("id")
    url = it.get("url")
    text_snippet = it.get("text", "").replace("\n", " ")[:90]
    print(f"{i+1}. [{views}] {item_id} | {text_snippet}...")
