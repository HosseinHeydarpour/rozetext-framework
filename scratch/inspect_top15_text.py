import sys, os, re
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath('.'))
from server import PublisherEngine

engine = PublisherEngine()

with open(r'D:\rozetext content\top_15_viral_delneveshte_reels.txt', 'r', encoding='utf-8') as f:
    text = f.read()

codes = ['DG8jFKGIWjY', 'DHMRcwUIAiZ', 'DHT4-A2tfLW', 'DDsB74pN7u8', 'DHwBbAooihl']

for c in codes:
    idx = text.find(c)
    block = text[max(0, idx-100):min(len(text), idx+1500)]
    m_text = re.search(r'متن(?: دقیق)?(?: داخل)? ویدیو.*?:?\s*\n«?([\s\S]*?)»?\s*(?:\n\s*-|\n\s*متن دقیق کپشن|\n\s*کپشن|\n\s*---|$)', block)
    raw = m_text.group(1).strip() if m_text else ""
    lines = [l.strip() for l in raw.splitlines() if l.strip()]
    dup = engine.check_duplicate_against_history(raw, raw)
    print(f"\n=== CODE: {c} ===")
    print(f"Lines count: {len(lines)}")
    print(f"Dup: {dup['is_duplicate']} ({dup['similarity_score']:.1f}%) | Closest: Reel #{dup.get('duplicate_of_reel')}")
    print("Full text:")
    print(raw)
