"""
Unified Anti-Duplication Engine for RozeText
============================================
Checks candidate text against:
1. All 292+ historical reels published on @rozetext.ir (from reports/06-10-2026-report.md & published-content-history.md)
2. All scheduled or drafted scripts in data/scripts-db.json

Matching strategy:
- Persian text normalization (half-space, arabic characters, punctuation)
- Token Jaccard overlap (> 38%)
- 4-gram sliding phrase match
- Hook & first 2 lines exact/fuzzy match (> 65%)
"""

import os
import re
import json
from typing import Dict, Any, List, Optional, Tuple

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
HISTORY_PATH = os.path.join(BASE_DIR, "published-content-history.md")
DB_PATH = os.path.join(BASE_DIR, "data", "scripts-db.json")

PERSIAN_STOPWORDS = {
    "از", "به", "در", "که", "با", "برای", "رو", "را", "من", "تو", "او", "ما", "شما",
    "این", "آن", "هم", "اما", "ولی", "نه", "شد", "بود", "کرد", "است", "هست", "نیست",
    "یک", "یه", "چون", "تا", "اگر", "اگه", "چه", "چی", "چرا", "همه", "هیچ", "دیگه",
    "روی", "توی", "کن", "کنم", "کنه", "باشه", "شدن", "کردن", "بودن"
}

class AntiDuplicationEngine:
    _instance = None

    def __init__(self):
        self.corpus: List[Dict[str, Any]] = []
        self._load_corpus()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = AntiDuplicationEngine()
        return cls._instance

    @staticmethod
    def normalize_persian(text: str) -> str:
        if not text:
            return ""
        t = text.lower()
        # Normalizations
        t = t.replace("ي", "ی").replace("ك", "ک").replace("ة", "ه").replace("ۀ", "ه")
        t = t.replace("\u200c", " ").replace("‌", " ") # half space to space
        t = re.sub(r"[!?,.:;،؛\-\–\—\(\)\[\]\{\}\'\"«»\*\=\_\/\\~`\^\#\@\$\%\&]+", " ", t)
        t = re.sub(r"\s+", " ", t).strip()
        return t

    @classmethod
    def extract_tokens(cls, text: str) -> set:
        norm = cls.normalize_persian(text)
        words = norm.split()
        # Filter very short stopwords/letters and general Persian stopwords
        return {w for w in words if len(w) >= 2 and w not in PERSIAN_STOPWORDS}

    @classmethod
    def extract_ngrams(cls, text: str, n: int = 4) -> set:
        norm = cls.normalize_persian(text)
        words = norm.split()
        if len(words) < n:
            return set()
        return {" ".join(words[i : i + n]) for i in range(len(words) - n + 1)}

    def _load_corpus(self):
        seen_identifiers = set()
        
        # 1. Load from all reports/*.md
        import glob
        report_files = sorted(glob.glob(os.path.join(REPORTS_DIR, "*.md")))
        for rep_path in report_files:
            try:
                with open(rep_path, "r", encoding="utf-8") as f:
                    rep_text = f.read()
                blocks = re.split(r"Reel #(\d+)", rep_text)[1:]
                for i in range(0, len(blocks), 2):
                    r_num = int(blocks[i])
                    body = blocks[i+1]
                    m_id = re.search(r"• Reel ID:\s*([^\n\r]+)", body)
                    reel_id = m_id.group(1).strip() if m_id else f"rep_{r_num}"
                    m_date = re.search(r"• Date:\s*([^\n\r]+)", body)
                    m_content = re.search(r"• Manual Content:\s*(.*?)(?=• AI Prediction|\Z)", body, re.DOTALL)
                    m_caption = re.search(r"• Caption:\s*([^\n\r]+)", body)
                    
                    content = m_content.group(1).strip() if m_content else ""
                    caption = m_caption.group(1).strip() if m_caption else ""
                    full_text = f"{content} {caption}".strip()
                    
                    if full_text and reel_id not in seen_identifiers:
                        seen_identifiers.add(reel_id)
                        tokens = self.extract_tokens(full_text)
                        ngrams = self.extract_ngrams(full_text, 4)
                        hook = content.split("\n")[0].strip() if content else caption[:40]
                        self.corpus.append({
                            "source": f"report_{os.path.basename(rep_path)}",
                            "reel_number": r_num,
                            "reel_id": reel_id,
                            "date": m_date.group(1).strip() if m_date else "",
                            "hook": hook,
                            "content": content,
                            "caption": caption,
                            "tokens": tokens,
                            "ngrams": ngrams
                        })
            except Exception as e:
                print(f"[AntiDuplication] Error reading report {rep_path}: {e}")

        # 2. Load from published-content-history.md
        if os.path.exists(HISTORY_PATH):
            try:
                with open(HISTORY_PATH, "r", encoding="utf-8") as f:
                    hist_text = f.read()
                blocks = re.split(r"### Reel #(\d+)", hist_text)[1:]
                for i in range(0, len(blocks), 2):
                    r_num = int(blocks[i])
                    body = blocks[i+1]
                    m_id = re.search(r"ID:\s*`([^`]+)`", body)
                    reel_id = m_id.group(1).strip() if m_id else f"hist_{r_num}"
                    
                    if reel_id in seen_identifiers:
                        continue
                    seen_identifiers.add(reel_id)
                    
                    m_hook = re.search(r"\*\*هوک \(خط اول\):\*\*\s*«([^»]+)»", body)
                    m_body = re.search(r"\*\*متن کامل داخل ریلز.*?:\*\*\s*(.*?)(?:\*\s*\*\*کپشن|\Z)", body, re.DOTALL)
                    m_cap = re.search(r"\*\*کپشن:\*\*\s*(.*?)(?:\*\s*\*\*ایده|\Z)", body, re.DOTALL)
                    
                    content = m_body.group(1).strip() if m_body else ""
                    caption = m_cap.group(1).strip() if m_cap else ""
                    hook = m_hook.group(1).strip() if m_hook else (content.split("\n")[0] if content else "")
                    full_text = f"{hook} {content} {caption}".strip()
                    
                    if full_text:
                        tokens = self.extract_tokens(full_text)
                        ngrams = self.extract_ngrams(full_text, 4)
                        self.corpus.append({
                            "source": "rozetext_history_md",
                            "reel_number": r_num,
                            "reel_id": reel_id,
                            "hook": hook,
                            "content": content,
                            "caption": caption,
                            "tokens": tokens,
                            "ngrams": ngrams
                        })
            except Exception as e:
                print(f"[AntiDuplication] Error reading history markdown: {e}")

        # 3. Load from data/scripts-db.json (all active, scheduled, or published items)
        if os.path.exists(DB_PATH):
            try:
                with open(DB_PATH, "r", encoding="utf-8") as f:
                    db = json.load(f)
                for s in db.get("scripts", []):
                    s_id = s.get("id")
                    content = s.get("content", "") or ""
                    hook = s.get("hook", "") or ""
                    caption = s.get("caption", "") or ""
                    full_text = f"{hook} {content} {caption}".strip()
                    if full_text and s_id not in seen_identifiers:
                        seen_identifiers.add(s_id)
                        tokens = self.extract_tokens(full_text)
                        ngrams = self.extract_ngrams(full_text, 4)
                        self.corpus.append({
                            "source": "scripts_db",
                            "script_id": s_id,
                            "scheduled_date": s.get("scheduled_date"),
                            "scheduled_slot": s.get("scheduled_slot"),
                            "hook": hook,
                            "content": content,
                            "caption": caption,
                            "tokens": tokens,
                            "ngrams": ngrams
                        })
            except Exception as e:
                print(f"[AntiDuplication] Error reading scripts-db: {e}")

        print(f"[AntiDuplication] Loaded {len(self.corpus)} reference documents into anti-duplication corpus.")

    def check(self, candidate_text: str, ignore_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Check if candidate_text is duplicated against any document in the corpus.
        Returns detailed duplication report.
        """
        if not candidate_text or not candidate_text.strip():
            return {"is_duplicate": False, "similarity_score": 0.0, "reason": "متن خالی"}

        c_tokens = self.extract_tokens(candidate_text)
        c_ngrams = self.extract_ngrams(candidate_text, 4)
        c_lines = [l.strip() for l in candidate_text.splitlines() if l.strip()]
        c_hook = c_lines[0] if c_lines else ""
        c_hook_tokens = self.extract_tokens(c_hook)

        if len(c_tokens) < 4:
            return {"is_duplicate": False, "similarity_score": 0.0, "reason": "متن بسیار کوتاه"}

        best_score = 0.0
        best_match = None
        match_reason = ""

        for doc in self.corpus:
            # Skip self if ignore_id is passed
            if ignore_id and (doc.get("reel_id") == ignore_id or doc.get("script_id") == ignore_id):
                continue

            d_tokens = doc["tokens"]
            if not d_tokens:
                continue

            # 1. Jaccard token overlap
            intersection = len(c_tokens & d_tokens)
            smaller_len = min(len(c_tokens), len(d_tokens))
            overlap_pct = (intersection / max(1, smaller_len)) * 100

            # 2. 4-gram sliding phrase match
            d_ngrams = doc["ngrams"]
            common_ngrams = c_ngrams & d_ngrams
            has_ngram_match = len(common_ngrams) >= 2

            # 3. Hook match
            d_hook = doc.get("hook", "")
            d_hook_tokens = self.extract_tokens(d_hook)
            hook_inter = len(c_hook_tokens & d_hook_tokens) if c_hook_tokens and d_hook_tokens else 0
            hook_sim = (hook_inter / max(1, min(len(c_hook_tokens), len(d_hook_tokens)))) if c_hook_tokens and d_hook_tokens else 0

            # Composite scoring
            score = overlap_pct
            if has_ngram_match:
                score = max(score, 68.0)
            if hook_sim >= 0.75 and overlap_pct >= 28.0:
                score = max(score, 75.0)

            if score > best_score:
                best_score = score
                best_match = doc
                if has_ngram_match:
                    match_reason = f"تطابق عبارت ۴ کلمه‌ای مشترک: «{list(common_ngrams)[0]}»"
                elif hook_sim >= 0.75:
                    match_reason = f"تطابق سطر اول/هوک: «{d_hook[:40]}...»"
                else:
                    match_reason = f"هم‌پوشانی واژگانی بالای {overlap_pct:.1f}%"

        # Threshold: 38%
        is_duplicate = best_score >= 38.0

        res = {
            "is_duplicate": is_duplicate,
            "similarity_score": round(best_score, 1),
            "match_reason": match_reason if is_duplicate else "",
            "matched_document": None
        }

        if best_match:
            doc_id = best_match.get("reel_id") or best_match.get("script_id") or f"Reel #{best_match.get('reel_number')}"
            res["matched_document"] = {
                "source": best_match.get("source"),
                "identifier": doc_id,
                "reel_number": best_match.get("reel_number"),
                "date": best_match.get("date") or best_match.get("scheduled_date"),
                "hook": best_match.get("hook"),
                "content_snippet": best_match.get("content", "")[:120]
            }

        return res

def verify_candidate_anti_duplication(candidate_text: str, ignore_id: Optional[str] = None) -> Dict[str, Any]:
    """Helper function to directly check text"""
    engine = AntiDuplicationEngine.get_instance()
    return engine.check(candidate_text, ignore_id=ignore_id)

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    engine = AntiDuplicationEngine.get_instance()
    test_text = """امشب فهمیدم تنهام...
نه از نبود آدم‌ها از زیاد بودن فاصله‌ها پشت لبخندها...
فهمیدم بعضی شونه‌ها فقط برای عکس خوبن
نه برای تکیه دادن..."""
    
    result = engine.check(test_text)
    print("Test Result:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
