import sys, os, re
sys.stdout.reconfigure(encoding='utf-8')

with open(r'D:\rozetext content\top_50_viral_delneveshte_reels.txt', 'r', encoding='utf-8') as f:
    text = f.read()

blocks = re.split(r'\n-{20,}\n|\n={20,}\n', text)

for i, b in enumerate(blocks):
    m_url = re.search(r'https://www\.instagram\.com/reel[s]?/([A-Za-z0-9_-]+)/?', b)
    if not m_url:
        continue
    code = m_url.group(1)
    m_v = re.search(r'آمار:\s*([^\n\r]+)', b)
    v_str = m_v.group(1) if m_v else "NO_VIEW"
    m_p = re.search(r'پیج\s*([A-Za-z0-9_\.]+|@[A-Za-z0-9_\.]+)', b)
    p_str = m_p.group(1) if m_p else "NO_PAGE"
    print(f"#{i:02d} [{code}] ({p_str}): {v_str}")
