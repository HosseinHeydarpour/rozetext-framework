import json
import os
import re
import shutil
import threading
import sys
from datetime import datetime
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse
from media_downloader import (
    download_reel_and_extract_media,
    open_in_explorer,
    extract_audio_from_local_video,
    list_system_downloaded_reels
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, "scripts"))
try:
    import post_maker
except ImportError:
    post_maker = None



BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "scripts-db.json")
STORIES_DB_PATH = os.path.join(DATA_DIR, "stories-db.json")
ROOT_HISTORY_PATH = os.path.join(BASE_DIR, "published-content-history.md")
SKILL_HISTORY_PATH = os.path.join(
    BASE_DIR, ".agents", "skills", "rozetext-persona-dna", "references", "published-content-history.md"
)

DB_LOCK = threading.Lock()

# Content rules version for this publisher build: v4.1 (24 Oct 2026).
# v4.1 keeps the 6-slot schedule (09:30, 12:15, 15:00, 18:15, 21:00, 23:45 IRST)
# and the Direct Raw-Text viral-copy policy. The v4.0 3-slot test and the
# Original-First policy were cancelled by the page owner in v4.1.

def get_posts_output_dir(shamsi_str: str) -> str:
    """Returns the preferred posts output directory (D:\رز تکست\<shamsi_date> with fallback to outputs/posts)."""
    d_dir = r"D:\رز تکست"
    if os.path.exists(d_dir) or os.path.exists("D:\\"):
        return os.path.join(d_dir, shamsi_str)
    return os.path.join(BASE_DIR, "outputs", "posts", shamsi_str)

# Instagram Insights ONLINE_FOLLOWERS_AVG matrix (historical, from @rozetext.ir live dashboard - October 2026; page was about 88,491 followers on 24 Oct 2026, so re-measure this matrix before treating its absolute online counts as current)
WEEKDAY_INSIGHTS = {
    0: {"name_fa": "دوشنبه", "peak": 19159, "avg": 14351, "slots": {1: 12448, 2: 16217, 3: 17859, 4: 16836, 5: 19159, 6: 18702}},
    1: {"name_fa": "سه‌شنبه", "peak": 19590, "avg": 14743, "slots": {1: 12934, 2: 16684, 3: 18379, 4: 17327, 5: 19590, 6: 19029}},
    2: {"name_fa": "چهارشنبه", "peak": 20121, "avg": 15133, "slots": {1: 12861, 2: 17145, 3: 18872, 4: 17886, 5: 20121, 6: 19860}},
    3: {"name_fa": "پنج‌شنبه", "peak": 20355, "avg": 15433, "slots": {1: 12078, 2: 17853, 3: 19453, 4: 18108, 5: 20184, 6: 20355}},
    4: {"name_fa": "جمعه", "peak": 21970, "avg": 16438, "slots": {1: 14008, 2: 19116, 3: 20471, 4: 19691, 5: 21970, 6: 20951}},
    5: {"name_fa": "شنبه (شروع پرقدرت هفته 🔥)", "peak": 22565, "avg": 16686, "slots": {1: 14462, 2: 18696, 3: 20771, 4: 19857, 5: 22565, 6: 21669}},
    6: {"name_fa": "یکشنبه (اوج مطلق هفته 🔥)", "peak": 23060, "avg": 17071, "slots": {1: 14853, 2: 19250, 3: 21312, 4: 20188, 5: 23060, 6: 22113}},
}

# 6 Daily Publishing Slots in Iran Standard Time (IRST +03:30)
DAILY_6_SLOTS = [
    {
        "slot": 1,
        "time_irst": "09:30",
        "window_label": "۰۹:۳۰ صبح (موج اول: شروع روز و مسیر کار)",
        "dashboard_bucket": "9p (08:30–11:29 IRST)",
        "best_archetypes": ["آرکتایپ ۵", "آرکتایپ ۶"],
        "reason": "مناسب برای مانیفست‌های اصالت، آرامش، رفتاربینی و شروع روز با حس قدرت."
    },
    {
        "slot": 2,
        "time_irst": "12:15",
        "window_label": "۱۲:۱۵ ظهر (موج دوم: تایم استراحت ظهرگاهی)",
        "dashboard_bucket": "12a (11:30–14:29 IRST)",
        "best_archetypes": ["آرکتایپ ۳", "آرکتایپ ۶"],
        "reason": "تایم چک کردن گوشی در میانه روز؛ عالی برای پست‌های آدم امن و مینی‌داستان‌های دیالوگی."
    },
    {
        "slot": 3,
        "time_irst": "15:00",
        "window_label": "۱۵:۰۰ بعدازظهر (موج سوم: اوج استراحت عصر)",
        "dashboard_bucket": "3a (14:30–17:29 IRST)",
        "best_archetypes": ["آرکتایپ ۱", "آرکتایپ ۴"],
        "reason": "جهش آنلاین بودن فالوورها تا ۱۶,۶۲۰ نفر؛ عالی برای گلایه‌های رابطه و خستگی روزانه."
    },
    {
        "slot": 4,
        "time_irst": "18:15",
        "window_label": "۱۸:۱۵ عصر (موج چهارم: پیش‌راه‌اندازی شبانه)",
        "dashboard_bucket": "6a (17:30–20:29 IRST)",
        "best_archetypes": ["آرکتایپ ۳"],
        "reason": "کاشت پست پیش از شروع پیک شبانه برای جمع کردن موتور Share در دایرکت (تقدیم‌نامه به خواهر / پارتنر / رفیق)."
    },
    {
        "slot": 5,
        "time_irst": "21:00",
        "window_label": "۲۱:۰۰ شب 🔥 (موج پنجم: بمب اول پیک مطلق شبانه)",
        "dashboard_bucket": "9a (20:30–23:29 IRST)",
        "best_archetypes": ["آرکتایپ ۱", "آرکتایپ ۳", "آرکتایپ ۴", "آرکتایپ ۵"],
        "reason": "شلوغ‌ترین ساعت کل شبانه‌روز در داشبورد شما (تا ۱۷,۶۸۲ آنلاین) + بالاترین نرخ تبدیل به وایرال میلیونی (قوی‌ترین بمب روز شما)."
    },
    {
        "slot": 6,
        "time_irst": "23:45",
        "window_label": "۲۳:۴۵ شب 🔥 (موج ششم: بمب دوم نیمه‌شب و دلتنگی)",
        "dashboard_bucket": "12p (23:30–02:29 IRST)",
        "best_archetypes": ["آرکتایپ ۱", "آرکتایپ ۲"],
        "reason": "ساعت خلوت، بی‌خوابی و بغض شبانه؛ بالاترین نرخ تبدیل به فالو و Save در کل پیج (تنهایی سنگ صبور / خداحافظی باوقار)."
    }
]


SLOT_ARCHETYPE_AFFINITY = {
    # اسلات ۱ (۰۹:۳۰ صبح): آرکتایپ ۵ و ۶ (اصالت، رفتاربینی، داستان کوتاه و شروع روز با حس قدرت)
    1: {5: 120, 6: 120, 3: 40, 4: -800, 1: -1000, 2: -1000},
    # اسلات ۲ (۱۲:۱۵ ظهر): آرکتایپ ۳ و ۶ (آدم امن، رفیق، مینی‌روایت دونفره و قدردانی)
    2: {3: 120, 6: 115, 1: 65, 4: 40, 5: 30, 2: -800},
    # اسلات ۳ (۱۵:۰۰ بعدازظهر): آرکتایپ ۱ و ۴ (خستگی روزانه، گلایه در رابطه و مرزگذاری صریح)
    3: {1: 120, 4: 120, 3: 50, 5: 40, 6: 20, 2: -200},
    # اسلات ۴ (۱۸:۱۵ عصر): منحصراً آرکتایپ ۳ (تقدیم‌نامه به خواهر / پارتنر / رفیق برای موتور Share دایرکت)
    4: {3: 130, 6: 60, 5: 30, 4: 20, 1: 10, 2: -800},
    # اسلات ۵ (۲۱:۰۰ شب 🔥): قوی‌ترین بمب روز شما (آرکتایپ ۱، ۳، ۴ یا ۵ مگاوایرال با بالاترین نمره روز)
    5: {1: 125, 3: 125, 4: 125, 5: 130, 2: 50, 6: 30},
    # اسلات ۶ (۲۳:۴۵ شب 🔥): آرکتایپ ۱ و ۲ (تنهایی سنگ صبور / خداحافظی باوقار و رهایی بدون اصرار)
    6: {2: 130, 1: 125, 5: 40, 4: 30, 3: 20, 6: -800},
}


def extract_archetype_num(arch_str: str, content: str = "", title: str = "") -> int:
    """Extracts integer archetype (1..6) accurately from string or semantic cues."""
    combined_txt = f"{title} {content}"
    if any(k in combined_txt for k in ["پدرم واسه مامانم", "بی مناسبت گل خریده", "خانواده", "کودک درون"]):
        return 6
    if any(k in combined_txt for k in ["واگذارت کردم", "نفرینت نمیکنم", "تقاص", "کارما", "به خدا سپردم", "روزگار نقاب", "روزگار بهترین قاضی"]):
        return 5
    if any(k in combined_txt for k in ["بی احترامی ازتون ببینم", "اتفاقا به من اعتماد نکنید", "حدفتون میکنم", "حذفتون میکنم"]):
        return 4
    if any(k in combined_txt for k in ["خداحافظی", "به سلامت", "تموم شد نه با دعوا", "اصراری واسه نگه داشتن", "میرم عقب تر"]):
        return 2

    FA_TO_EN = {'۱': '1', '۲': '2', '۳': '3', '۴': '4', '۵': '5', '۶': '6'}
    s = str(arch_str or "")
    for fa_d, en_d in FA_TO_EN.items():
        s = s.replace(fa_d, en_d)

    m = re.search(r"(?:آرکتایپ|Archetype|\bArch\b)?\s*([1-6])", s)
    if m:
        return int(m.group(1))

    if any(k in combined_txt for k in ["عاشقت شدم", "تولدت مبارک", "دوستت دارم", "کنارم بمون", "نور زندگی", "پارتنر"]):
        return 3
    if any(k in combined_txt for k in ["خسته", "کسی نمیپرسه", "تنهایی", "پیر میشن"]):
        return 1

    return 1


def optimize_daily_basket_slots(scripts: list) -> list:
    """
    Given a list of scripts for a single day (up to 6), calculates the globally optimal
    assignment of scripts to slots (1..6) using max-weight permutation matching to guarantee
    circadian and archetype affinity (e.g. Archetype 5/6 in Slot 1, Archetype 2/1 in Slot 6).
    """
    import itertools
    n = len(scripts)
    if n == 0:
        return []

    target_slots = list(range(1, min(6, n) + 1))
    best_score = -float("inf")
    best_assignment = None

    if n <= 6:
        for perm in itertools.permutations(target_slots):
            score = 0
            for i, slot_idx in enumerate(perm):
                sc = scripts[i]
                arch = extract_archetype_num(sc.get('archetype', ''), sc.get('content', ''), sc.get('title', ''))
                viral_score = float(sc.get('score') or 90)
                aff = SLOT_ARCHETYPE_AFFINITY[slot_idx].get(arch, 0)
                if slot_idx == 5:
                    aff += (viral_score - 90) * 2
                score += aff
            if score > best_score:
                best_score = score
                best_assignment = perm

        result = []
        for i, slot_idx in enumerate(best_assignment):
            c = dict(scripts[i])
            c['scheduled_slot'] = slot_idx
            result.append(c)
        result.sort(key=lambda x: x['scheduled_slot'])
        return result
    else:
        top6 = scripts[:6]
        res = optimize_daily_basket_slots(top6)
        res.extend(scripts[6:])
        return res


def recommend_slot_for_archetype(archetype_str: str, occupied_slots: set, content: str = "", title: str = "") -> int:
    """Recommends the best available slot (1..6) for a given archetype ensuring strict circadian fit."""
    arch_num = extract_archetype_num(archetype_str, content, title)

    # Priority ordered slot preferences by archetype:
    # Slot 1: Strictly 5 or 6 (Morning strength/warmth). Strictly avoid 1, 2, 4.
    # Slot 6: Strictly 2 or 1 (Midnight quiet/farewell).
    if arch_num == 5:
        pref = [1, 5, 4, 3, 2, 6]  # Archetype 5 is top morning dignity & prime night
    elif arch_num == 6:
        pref = [1, 2, 4, 3, 5, 6]  # Archetype 6 is top morning warmth & lunch
    elif arch_num == 3:
        pref = [4, 2, 5, 3, 6, 1]  # Archetype 3 is evening forward & lunch dialogue
    elif arch_num == 4:
        pref = [3, 5, 4, 2, 6, 1]  # Archetype 4 is afternoon boundaries
    elif arch_num == 1:
        pref = [5, 3, 6, 4, 2, 1]  # Archetype 1 is night & afternoon (never slot 1)
    elif arch_num == 2:
        pref = [6, 5, 3, 4, 2, 1]  # Archetype 2 is midnight farewell (never slot 1)
    else:
        pref = [5, 2, 4, 3, 1, 6]

    for s in pref:
        if s not in occupied_slots:
            return s
    for s in range(1, 7):
        if s not in occupied_slots:
            return s
    return pref[0]


def get_date_slot_info(date_str: str, slot_num: int) -> dict:
    """Returns enriched timing & online follower data for a target YYYY-MM-DD and slot (1..6)."""
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        weekday_idx = dt.weekday()  # 0 = Monday .. 6 = Sunday
    except Exception:
        weekday_idx = 4  # Default Friday

    w_info = WEEKDAY_INSIGHTS[weekday_idx]
    slot_meta = next((s for s in DAILY_6_SLOTS if s["slot"] == slot_num), DAILY_6_SLOTS[4])
    online_count = w_info["slots"].get(slot_num, w_info["avg"])

    return {
        "date": date_str,
        "weekday_fa": w_info["name_fa"],
        "slot": slot_num,
        "time_irst": slot_meta["time_irst"],
        "window_label": slot_meta["window_label"],
        "online_followers": online_count,
        "day_peak_followers": w_info["peak"],
        "reason": slot_meta["reason"]
    }


class PublisherEngine:
    def __init__(self, db_path=DB_PATH, root_history_path=ROOT_HISTORY_PATH, skill_history_path=SKILL_HISTORY_PATH, stories_db_path=STORIES_DB_PATH):
        self.db_path = db_path
        self.root_history_path = root_history_path
        self.skill_history_path = skill_history_path
        self.stories_db_path = stories_db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        if not os.path.exists(self.db_path):
            self._init_default_db()

    def load_stories_db(self) -> dict:
        if not os.path.exists(self.stories_db_path):
            return {"meta": {"page_handle": "@rozetext.ir", "total_followers": 88491}, "stories": []}
        with open(self.stories_db_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_stories_db(self, data: dict):
        os.makedirs(os.path.dirname(self.stories_db_path), exist_ok=True)
        if "meta" not in data:
            data["meta"] = {}
        data["meta"]["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        tmp_path = self.stories_db_path + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, self.stories_db_path)

    def toggle_publish_story(self, story_id: str) -> dict:
        with DB_LOCK:
            db = self.load_stories_db()
            target = next((s for s in db["stories"] if s["id"] == story_id), None)
            if not target:
                raise ValueError(f"Story {story_id} not found")
            target["published"] = not target.get("published", False)
            target["published_at"] = datetime.now().strftime("%Y-%m-%d %H:%M") if target["published"] else None
            self.save_stories_db(db)
            return target

    def _init_default_db(self):
        default_data = {
            "meta": {
                "page_handle": "@rozetext.ir",
                "daily_goal": 6,
                "base_history_count": 233,
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            "scripts": []
        }
        self.save_db(default_data)

    def load_db(self) -> dict:
        with open(self.db_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if "scripts" in data and isinstance(data["scripts"], list):
            for sc in data["scripts"]:
                self.sanitize_script_origin(sc)
        return data

    def save_db(self, data: dict):
        if "meta" not in data or not isinstance(data["meta"], dict):
            data["meta"] = {
                "page_handle": "@rozetext.ir",
                "daily_goal": 6,
                "base_history_count": 233,
            }
        data["meta"]["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if "scripts" in data and isinstance(data["scripts"], list):
            for sc in data["scripts"]:
                self.sanitize_script_origin(sc)
        tmp_path = self.db_path + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, self.db_path)

    @staticmethod
    def sanitize_script_origin(script_obj: dict) -> dict:
        """
        تضمین ۱۰۰٪ صحت برچسب منبع (Hunted vs AI-Generated):
        یک ریلز فقط و فقط زمانی 'شکارشده' محسوب می‌شود که:
        ۱. فیلد is_viral_hunted به صورت صریح True باشد
        ۲. دارای منبع معتبر اینستاگرامی (source_url حاوی لینک یا source_page با شروع @) باشد.
        در غیر این صورت، این ریلز به صورت قطعی 'تولید اختصاصی هوش مصنوعی' است و تمامی فیلدهای پسماند
        شکار (لینک، پیج و ویو مرجع) به صورت خودکار پاکسازی می‌شوند تا هیچ برچسب اشتباهی ظاهر نشود.
        """
        source_url = (script_obj.get("source_url") or "").strip()
        source_page = (script_obj.get("source_page") or "").strip()
        has_valid_source = bool(
            (source_url and ("http" in source_url or "instagram.com" in source_url)) or
            (source_page and source_page.startswith("@") and len(source_page) > 2)
        )
        is_hunted = bool(script_obj.get("is_viral_hunted", False)) and has_valid_source

        if is_hunted:
            script_obj["is_viral_hunted"] = True
            script_obj["source_url"] = source_url
            script_obj["source_page"] = source_page
            script_obj["source_views"] = (script_obj.get("source_views") or "").strip()
            
            # Auto-resolve local frame image path if exists
            m = re.search(r"/(?:reel|p)/([A-Za-z0-9_-]+)", source_url)
            shortcode = m.group(1) if m else None
            frame_url = ""
            if shortcode:
                import glob
                all_found = (
                    glob.glob(f"downloads/frames/*{shortcode}*.png") +
                    glob.glob(f"downloads/frames/*{shortcode}*.jpg") +
                    glob.glob(f"assets/hunted_frames/*{shortcode}*.jpg") +
                    glob.glob(f"assets/hunted_frames/*{shortcode}*.png")
                )
                # Prioritize logged-in and 2s-verified frames over unauthenticated/age-gated frames
                matching_frames = sorted(
                    all_found,
                    key=lambda p: (0 if "logged" in p else (1 if "2s" in p else 2))
                )
                if matching_frames and os.path.exists(matching_frames[0]):
                    rel = os.path.relpath(matching_frames[0], BASE_DIR).replace("\\", "/")
                    frame_url = f"/{rel}"
            script_obj["local_frame_url"] = frame_url
            script_obj["has_local_frame"] = bool(frame_url)
        else:
            script_obj["is_viral_hunted"] = False
            script_obj["source_url"] = ""
            script_obj["source_page"] = ""
            script_obj["source_views"] = ""
            script_obj["extracted_raw_text"] = ""
            script_obj["local_frame_url"] = ""
            script_obj["has_local_frame"] = False

        return script_obj

    @staticmethod
    def _clean_raw_text_for_direct_use(raw_text: str) -> str:
        """
        Cleans extracted on-screen raw text for direct 1:1 publication on @rozetext.ir
        without rewriting/localizing the words (only strips source page watermarks/labels).
        """
        if not raw_text:
            return ""
        cleaned_lines = []
        for line in raw_text.splitlines():
            s = line.strip()
            if not s:
                continue
            # Skip metadata annotations or source watermarks
            if s.startswith("[") and s.endswith("]:"):
                continue
            if re.match(r"^[«\"']?حال\s*خوب[»\"']?$", s) or re.match(r"^@[A-Za-z0-9_.]+$", s):
                continue
            cleaned_lines.append(s)
        return "\n".join(cleaned_lines)

    @staticmethod
    def _normalize_persian_tokens(txt: str) -> set:
        if not txt:
            return set()
        norm = (
            txt.replace("ي", "ی")
            .replace("ك", "ک")
            .replace("\u200c", " ")
            .replace("ٔ", "")
        )
        # Normalize common conversational/formal verb prefixes (می‌کنم / میکنم -> کنم)
        norm = re.sub(r"\bن?می\s+", "", norm)
        stop = {"حال", "خوب", "متن", "تکست", "ریلز", "کپشن", "امروز", "برای", "اینکه", "وقتی", "همیشه", "خیلی", "دیگه", "دیگر", "چون", "اگر", "اگه"}
        return {w for w in re.findall(r"[\w\u0600-\u06FF]{3,}", norm) if w not in stop}

    @staticmethod
    def _extract_ngrams(txt: str, n: int = 4) -> set:
        if not txt:
            return set()
        norm = (
            txt.replace("ي", "ی")
            .replace("ك", "ک")
            .replace("\u200c", " ")
            .replace("ٔ", "")
        )
        words = [w for w in re.findall(r"[\w\u0600-\u06FF]{2,}", norm)]
        if len(words) < n:
            return set()
        return {" ".join(words[i : i + n]) for i in range(len(words) - n + 1)}

    def check_duplicate_against_history(self, content: str, extracted_raw_text: str = "", ignore_id: str = None) -> dict:
        """
        Programmatically checks candidate content AND extracted_raw_text against all 385+ historical reels
        (reports/06-10-2026-report.md + published-content-history.md + active scripts-db) using AntiDuplicationEngine.
        """
        try:
            from anti_duplication import AntiDuplicationEngine
            engine = AntiDuplicationEngine.get_instance()
            
            # Check content
            res_content = engine.check(content, ignore_id=ignore_id) if content else {"is_duplicate": False, "similarity_score": 0.0}
            # Check raw text if different
            res_raw = engine.check(extracted_raw_text, ignore_id=ignore_id) if (extracted_raw_text and extracted_raw_text != content) else {"is_duplicate": False, "similarity_score": 0.0}
            
            res = res_content if res_content.get("similarity_score", 0) >= res_raw.get("similarity_score", 0) else res_raw
            
            is_dup = res.get("is_duplicate", False)
            sim_pct = res.get("similarity_score", 0.0)
            doc = res.get("matched_document") or {}
            doc_id = doc.get("identifier") or (f"Reel #{doc.get('reel_number')}" if doc.get('reel_number') else "—")
            hook = doc.get("hook") or ""
            reason = res.get("match_reason") or ""
            
            if is_dup:
                badge = f"❌ تکراری! ({sim_pct}% مشابه با {doc_id}: «{hook[:40]}...» — {reason})"
            else:
                badge = f"✅ چک‌شده با دیتابیس جامع ۲۹۲ ریلز (غیرتکراری — بیشترین تشابه: {sim_pct}% با {doc_id})"
                
            return {
                "is_duplicate": is_dup,
                "similarity_score": sim_pct,
                "duplicate_of_reel": doc_id,
                "matched_hook": hook,
                "matched_ngram": reason,
                "history_check_badge": badge,
            }
        except Exception as e:
            return {
                "is_duplicate": False,
                "similarity_score": 0.0,
                "duplicate_of_reel": None,
                "matched_hook": "",
                "matched_ngram": None,
                "history_check_badge": f"⚠️ خطا در بررسی ضدتکرار: {e}",
            }

    def _get_next_history_number(self, db_data: dict, history_text: str) -> int:
        """Determines the next sequential Reel # (> 233) safely without collisions."""
        max_num = 233
        # Check existing published scripts in db
        for s in db_data.get("scripts", []):
            if s.get("published") and s.get("history_reel_number"):
                max_num = max(max_num, int(s["history_reel_number"]))
        # Also scan history markdown for any ### Reel #<num> or | **#<num>** |
        found_nums = [int(n) for n in re.findall(r"(?:### Reel #|\|\s*\*\*#)(\d+)", history_text)]
        for n in found_nums:
            # Ignore placeholder #234 if it has '*آماده ثبت*' on its line
            if n == 234 and "| **#234** | *آماده ثبت*" in history_text:
                continue
            max_num = max(max_num, n)
        return max_num + 1

    def _append_to_history_markdown(self, file_path: str, reel_num: int, script_obj: dict):
        """Idempotently appends a published script to Sections 1, 2, and 3 of published-content-history.md."""
        if not os.path.exists(file_path):
            return

        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

        marker_tag = f"<!-- SCRIPT_ID:{script_obj['id']} -->"
        if marker_tag in text or f"### Reel #{reel_num} (" in text:
            # Already present! Idempotent no-op.
            return

        content_lines = [l.strip() for l in script_obj["content"].splitlines() if l.strip()]
        first_line = content_lines[0] if content_lines else "—"
        last_line = content_lines[-1] if content_lines else "—"
        compact_content = " / ".join(content_lines)
        compact_caption = " ".join([l.strip() for l in script_obj["caption"].splitlines() if l.strip()])
        pub_date = script_obj.get("published_at") or datetime.now().strftime("%Y-%m-%d %H:%M")

        fl_clean = first_line.replace("|", "｜")
        ll_clean = last_line.replace("|", "｜")
        cc_clean = compact_content.replace("|", "｜")
        cap_clean = compact_caption.replace("|", "｜")

        # 1. Insert into Section 1 table (New Published Posts Log)
        sec1_row = f"| **#{reel_num}** | `{pub_date}` | «{fl_clean}» | {cc_clean} | {cap_clean} | {marker_tag}"
        placeholder_line = "| **#234** | *آماده ثبت* | *(پس از انتشار هر پست جدید، به ایجنت بگویید: «این پست را به تاریخچه اضافه کن»)* | — | — |"
        if placeholder_line in text:
            text = text.replace(placeholder_line, sec1_row + "\n" + placeholder_line, 1)
        else:
            sec1_header = "| شماره | تاریخ انتشار | هوک (خط اول ریلز) | متن کامل داخل ریلز (Manual Content) | کپشن منتشرشده |\n| :---: | :---: | :--- | :--- | :--- |"
            if sec1_header in text:
                text = text.replace(sec1_header, sec1_header + "\n" + sec1_row, 1)

        # 2. Insert into Section 2 table (Quick Hook Index) right at the top of the index table
        sec2_header = "| ردیف | وضعیت | بازدید | خط اول ریلز (Opening Hook) | خط آخر ریلز (Closing Punchline) |\n| :---: | :---: | :---: | :--- | :--- |"
        sec2_row = f"| **#{reel_num}** | ✅ [PUBLISHED] | جدید ({pub_date}) | {fl_clean} | {ll_clean} | {marker_tag}"
        if sec2_header in text:
            text = text.replace(sec2_header, sec2_header + "\n" + sec2_row, 1)

        # 3. Append full block at the end of Section 3
        sec3_block = (
            f"\n---\n### Reel #{reel_num} (✅ [PUBLISHED]) — ID: `{script_obj['id']}` | Date: `{pub_date}` {marker_tag}\n"
            f"* **آرکتایپ:** {script_obj.get('archetype', '—')} | **هدف:** {script_obj.get('goal', '—')} | **امتیاز اسکیل:** `{script_obj.get('score', 100)}/100`\n"
            f"* **هوک (خط اول):** «{first_line}»\n"
            f"* **متن کامل داخل ریلز (Manual Content):**\n"
            f"  > {compact_content}\n"
            f"* **کپشن:**\n"
            f"  > {compact_caption}\n"
        )
        text = text.rstrip() + "\n" + sec3_block

        tmp_path = file_path + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(text)
        os.replace(tmp_path, file_path)

    def _remove_from_history_markdown(self, file_path: str, script_id: str, reel_num: int):
        """Cleanly removes a script's lines/block from published-content-history.md if unchecked."""
        if not os.path.exists(file_path):
            return

        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

        marker_tag = f"<!-- SCRIPT_ID:{script_id} -->"
        if marker_tag not in text:
            return

        # Remove Section 3 block first
        block_pattern = re.compile(
            r"\n---\n### Reel #" + str(reel_num) + r"\s+\(✅ \[PUBLISHED\]\).*?" + re.escape(marker_tag) + r".*?(?=\n---\n### Reel #|\Z)",
            re.DOTALL
        )
        text = block_pattern.sub("", text)

        # Remove any single-line table rows in Section 1 and Section 2 containing marker_tag
        kept_lines = [line for line in text.splitlines() if marker_tag not in line]
        cleaned_text = "\n".join(kept_lines) + "\n"

        tmp_path = file_path + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(cleaned_text)
        os.replace(tmp_path, file_path)

    @staticmethod
    def compute_viral_probability_and_persona_audit(payload: dict, content: str, archetype: str) -> dict:
        """
        Computes the 5-pillar Viral Probability Score (0..100) and Persona Fit Reason
        for both AI-generated scripts and Instagram-hunted scripts.
        """
        lines = [l.strip() for l in content.splitlines() if l.strip()]
        words = content.split()
        w_count = len(words)
        l_count = len(lines)
        first_line_words = len(lines[0].split()) if lines else 0

        custom_bd = payload.get("score_breakdown") or {}
        persona_fit = int(custom_bd.get("persona_fit", 20 if ("آرکتایپ" in archetype) else 18))
        hook_power = int(custom_bd.get("hook_power", 20 if (2 <= first_line_words <= 8) else 17))
        pacing_watchtime = int(custom_bd.get("pacing_watchtime", 20 if (10 <= l_count <= 20 and 45 <= w_count <= 95) else 18))
        micdrop_saveability = int(custom_bd.get("micdrop_saveability", 19))
        share_trigger = int(custom_bd.get("share_trigger", 20 if any(k in archetype for k in ("آرکتایپ ۱", "آرکتایپ ۲", "آرکتایپ ۳", "آرکتایپ ۴")) else 19))

        breakdown = {
            "persona_fit": min(20, max(1, persona_fit)),
            "hook_power": min(20, max(1, hook_power)),
            "pacing_watchtime": min(20, max(1, pacing_watchtime)),
            "micdrop_saveability": min(20, max(1, micdrop_saveability)),
            "share_trigger": min(20, max(1, share_trigger)),
        }
        total_score = int(payload.get("score") or sum(breakdown.values()))

        default_reasons = {
            "آرکتایپ ۱": "تطابق ۱۰۰٪ با پرسونای «آدم همیشه قوی و بی‌صدا خوب» (راوی نجیب که بغضش را پشت لبخند پنهان می‌کند — هم‌خانواده ریلز #4 با ۱.۹۳M بازدید).",
            "آرکتایپ ۲": "تطابق ۱۰۰٪ با پرسونای «خداحافظی باوقار بعد از جنگیدن زیاد» بدون نفرین و پرخاش (هم‌خانواده ریلز #1 با ۲.۴۵M بازدید).",
            "آرکتایپ ۳": "تطابق ۱۰۰٪ با پرسونای «تقدیم‌نامه به آدم امن و ریشه‌دار» با بالاترین نرخ فوروارد در دایرکت (هم‌خانواده ریلز #7 با ۱.۶۶M بازدید).",
            "آرکتایپ ۴": "تطابق ۱۰۰٪ با پرسونای «گلایه بی‌دفاع و صادقانه در رابطه» از زاویه دید اول‌شخص (هم‌خانواده ریلز #8 با ۱.۶۴M بازدید).",
            "آرکتایپ ۵": "تطابق ۱۰۰٪ با پرسونای «مانیفست رفتاربینی، اصالت و عدالت خدا» با نرخ سیو بالا (هم‌خانواده ریلز #5 با ۱.۷۵M بازدید).",
            "آرکتایپ ۶": "تطابق ۱۰۰٪ با پرسونای «مینی‌روایت دیالوگی و برش واقعی زندگی ایرانی» با واچ‌تایم بالای ۱۰۰٪ (هم‌خانواده ریلز #2 با ۲.۰۵M بازدید).",
        }
        matched_reason = "تاییدشده توسط فیلتر دروازه‌بان پرسونای پیج رز تکست (@rozetext.ir)."
        for key, reason_txt in default_reasons.items():
            if key in archetype:
                matched_reason = reason_txt
                break

        persona_fit_reason = (payload.get("persona_fit_reason") or "").strip() or matched_reason
        return {
            "score": total_score,
            "score_breakdown": breakdown,
            "persona_fit_reason": persona_fit_reason,
        }

    @staticmethod
    def diagnose_post_mortem(script_obj: dict) -> str:
        """
        Analyzes WHY a high-score script might have underperformed (or why it succeeded)
        when actual_views / actual_result is recorded.
        """
        custom_note = (script_obj.get("post_mortem_analysis") or "").strip()
        actual_result = (script_obj.get("actual_result") or "").strip()
        actual_views = (script_obj.get("actual_views") or "").strip()
        score = int(script_obj.get("score") or 95)
        bd = script_obj.get("score_breakdown") or {}

        if not actual_views and not actual_result:
            return custom_note

        reasons = []
        if actual_result == "UNDERPERFORMED" and score >= 85:
            first_line_words = len((script_obj.get("hook") or "").split())
            if first_line_words > 7 or bd.get("hook_power", 20) < 18:
                reasons.append("۱. طولانی بودن سطر اول روی کاور (بیش از ۶ کلمه) باعث ریزش مخاطب در ۱.۵ ثانیه اول شده است.")
            if int(script_obj.get("scheduled_slot") or 5) not in (5, 6) and ("آرکتایپ ۱" in script_obj.get("archetype", "") or "آرکتایپ ۲" in script_obj.get("archetype", "")):
                reasons.append("۲. عدم تطابق ساعت انتشار با حسِ متن: آرکتایپ‌های بغض و خداحافظی در ساعات روز به اندازه اسلات ۲۱:۰۰ و ۲۳:۴۵ شب بازخورد نمی‌گیرند.")
            if script_obj.get("is_viral_hunted"):
                reasons.append("۳. تفاوت عوامل بصری/صوتی با ریلز مرجع: در ریلز شکارشده، بخشی از وایرال شدن پیج مادر مدیون موزیک ترند یا کنتراست فونت روی ویدیو بوده است.")
            if bd.get("share_trigger", 20) < 19:
                reasons.append("۴. ضعف محرک ارسال در دایرکت (Share Trigger): متن زیبا و قابل سیو بوده اما مخاطب مشخصی (مثل رفیق یا پارتنر) برای فوروارد فوری نداشته است.")
            if not reasons:
                reasons.append("متن و ساختار از نظر DNA نمره بالایی دارد؛ افت بازدید ناشی از اشباع همزمان چند پست مشابه در یک روز یا تغییر موزیک/کنتراست پس‌زمینه ویدیو است.")

            auto_diag = "🔍 کالبدشکافی اختلاف نمره بالا با بازخورد واقعی: " + " | ".join(reasons)
            return f"{custom_note}\n{auto_diag}".strip() if custom_note and "کالبدشکافی" not in custom_note else (custom_note or auto_diag)

        return custom_note

    def audit_and_fix_semantic_polarity(self, content_str: str) -> tuple[str, str]:
        """
        Programmatic Persian semantic polarity guard (complementing the persian_semantic_critic subagent):
        Detects and auto-fixes verb polarity inversions caused by line trimming (e.g., dropping 'تلاش برای'
        leaving 'از فهمیده شدن خسته' when context is 'کسی نفهمید / سکوت / بی‌صدا').
        """
        fixes_applied = []
        polarity_rules = [
            (r"از\s+فهمیده\s+شدن\s+خسته", "از فهمیده نشدن خسته", ("نفهمید", "سکوت", "بی‌صدا", "نگفت", "تنها")),
            (r"از\s+دیده\s+شدن\s+خسته", "از دیده نشدن خسته", ("ندید", "نادیده", "سکوت", "بی‌صدا")),
            (r"از\s+شنیده\s+شدن\s+خسته", "از شنیده نشدن خسته", ("نشنید", "سکوت", "بی‌صدا", "بغض")),
            (r"از\s+درک\s+شدن\s+خسته", "از درک نشدن خسته", ("درک نکرد", "نفهمید", "یک‌طرفه", "سکوت")),
        ]
        updated = content_str
        for pattern, replacement_prefix, context_triggers in polarity_rules:
            if re.search(pattern, updated):
                if any(trig in updated for trig in context_triggers):
                    updated = re.sub(pattern, replacement_prefix, updated)
                    fixes_applied.append(f"{pattern} -> {replacement_prefix}")

        if fixes_applied:
            badge = f"🛡️ اصلاح خودکار قطبیت معنایی ({', '.join(fixes_applied)})"
        else:
            badge = "✅ تایید منطق معنایی و قطبیت فعل (persian_semantic_critic)"
        return updated, badge

    def add_script(self, payload: dict) -> dict:
        with DB_LOCK:
            db = self.load_db()
            new_id = payload.get("id") or f"script-{int(datetime.now().timestamp() * 1000)}-{len(db['scripts']) + 1:03d}"
            # Check if id already exists
            for existing in db["scripts"]:
                if existing["id"] == new_id:
                    return existing

            target_date = payload.get("scheduled_date") or datetime.now().strftime("%Y-%m-%d")
            occupied = {
                s.get("scheduled_slot")
                for s in db["scripts"]
                if s.get("scheduled_date") == target_date and s.get("scheduled_slot")
            }
            archetype_str = payload.get("archetype") or "آرکتایپ ۱: آدم همیشه قوی و بی‌صدا خوب"
            raw_str = (payload.get("extracted_raw_text") or "").strip()
            is_hunted = bool(payload.get("is_viral_hunted", bool(payload.get("source_url"))))
            if is_hunted and raw_str:
                raw_str = self._clean_raw_text_for_direct_use(raw_str)
                # Direct Raw-Text Policy: always use the exact cleaned raw video text as main content
                content_str = raw_str
            else:
                content_str = payload.get("content", "").strip()
                content_str, semantic_badge = self.audit_and_fix_semantic_polarity(content_str)

            dup_info = self.check_duplicate_against_history(content_str, raw_str, ignore_id=new_id)
            if dup_info["is_duplicate"] and not payload.get("allow_duplicate"):
                raise ValueError(f"DUPLICATE_REEL_BLOCKED: {dup_info['history_check_badge']}")

            slot_num = int(payload.get("scheduled_slot") or recommend_slot_for_archetype(
                archetype_str,
                occupied,
                content_str,
                payload.get("title", "")
            ))
            slot_info = get_date_slot_info(target_date, slot_num)

            lines = [l.strip() for l in content_str.splitlines() if l.strip()]
            words_count = len(content_str.split())
            audit_info = self.compute_viral_probability_and_persona_audit(payload, content_str, archetype_str)

            script_obj = {
                "id": new_id,
                "title": payload.get("title") or (lines[0][:40] if lines else "اسکریپت جدید"),
                "archetype": archetype_str,
                "goal": payload.get("goal") or "جذب فالوور حداکثری (Follow Magnet)",
                "content": content_str,
                "caption": payload.get("caption", "").strip(),
                "hook": (payload.get("hook") or "").strip() or (lines[0] if lines else ""),
                "punchline": lines[-1] if lines else "",
                "words_count": words_count,
                "lines_count": len(lines),
                "score": audit_info["score"],
                "score_breakdown": audit_info["score_breakdown"],
                "persona_fit_reason": audit_info["persona_fit_reason"],
                "history_check_badge": dup_info["history_check_badge"],
                "history_similarity_score": dup_info["similarity_score"],
                # New Viral Source & Extra Description fields
                "is_viral_hunted": bool(payload.get("is_viral_hunted", bool(payload.get("source_url")))),
                "source_url": (payload.get("source_url") or "").strip(),
                "source_page": (payload.get("source_page") or "").strip(),
                "source_views": (payload.get("source_views") or "").strip(),
                "extracted_raw_text": raw_str,
                "extra_notes": (payload.get("extra_notes") or "").strip(),
                # Post-publish feedback & score calibration fields
                "actual_views": (payload.get("actual_views") or "").strip(),
                "actual_result": (payload.get("actual_result") or "").strip(),
                "post_mortem_analysis": (payload.get("post_mortem_analysis") or "").strip(),
                # Scheduling fields
                "scheduled_date": target_date,
                "scheduled_slot": slot_num,
                "recommended_time": slot_info["time_irst"],
                "window_label": slot_info["window_label"],
                "weekday_fa": slot_info["weekday_fa"],
                "online_followers": slot_info["online_followers"],
                "published": False,
                "published_at": None,
                "history_reel_number": None,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            script_obj["post_mortem_analysis"] = self.diagnose_post_mortem(script_obj)
            script_obj = self.sanitize_script_origin(script_obj)
            db["scripts"].insert(0, script_obj)
            self.save_db(db)
            return script_obj

    def update_script_metadata(self, script_id: str, payload: dict) -> dict:
        """Updates source metadata, persona_fit_reason, score_breakdown, actual_views, actual_result, and post_mortem_analysis."""
        with DB_LOCK:
            db = self.load_db()
            target = next((s for s in db["scripts"] if s["id"] == script_id), None)
            if not target:
                raise ValueError(f"Script {script_id} not found")

            for field in (
                "source_url", "source_page", "source_views", "extracted_raw_text", "extra_notes",
                "title", "hook", "archetype", "goal", "content", "caption",
                "persona_fit_reason", "actual_views", "actual_result", "post_mortem_analysis"
            ):
                if field in payload and payload[field] is not None:
                    target[field] = str(payload[field]).strip()

            if "score_breakdown" in payload and isinstance(payload["score_breakdown"], dict):
                bd = target.get("score_breakdown") or {}
                for k, v in payload["score_breakdown"].items():
                    bd[k] = min(20, max(1, int(v)))
                target["score_breakdown"] = bd
                target["score"] = sum(bd.values())
            elif "score" in payload and payload["score"] is not None:
                target["score"] = int(payload["score"])

            if "is_viral_hunted" in payload:
                target["is_viral_hunted"] = bool(payload["is_viral_hunted"])
            target = self.sanitize_script_origin(target)

            lines = [l.strip() for l in target.get("content", "").splitlines() if l.strip()]
            if "hook" in payload and payload["hook"] is not None:
                target["hook"] = str(payload["hook"]).strip()
            elif not target.get("hook"):
                target["hook"] = lines[0] if lines else ""
            target["punchline"] = lines[-1] if lines else ""
            target["words_count"] = len(target.get("content", "").split())
            target["lines_count"] = len(lines)
            target["post_mortem_analysis"] = self.diagnose_post_mortem(target)

            self.save_db(db)
            return target

    def batch_import_and_schedule(self, items: list, start_date: str = None) -> list:
        """
        Imports a list of scripts (e.g. 6, 12, 18, 24 reels for 1..N days) and automatically
        groups them into batches of 6 per day starting from start_date, assigning each reel
        within a 6-pack to its optimal circadian slot (1..6) based on its Archetype!
        """
        from datetime import timedelta
        base_dt = datetime.strptime(start_date, "%Y-%m-%d") if start_date else datetime.now()
        created_scripts = []

        # Process in chunks of 6 (1 day per 6 reels)
        for day_offset in range(0, len(items), 6):
            chunk = items[day_offset:day_offset + 6]
            day_str = (base_dt + timedelta(days=day_offset // 6)).strftime("%Y-%m-%d")

            with DB_LOCK:
                db = self.load_db()
                occupied = {
                    int(s.get("scheduled_slot"))
                    for s in db["scripts"]
                    if s.get("scheduled_date") == day_str and s.get("scheduled_slot") and not s.get("published")
                }
                while len(occupied) >= 6:
                    base_dt += timedelta(days=1)
                    day_str = (base_dt + timedelta(days=day_offset // 6)).strftime("%Y-%m-%d")
                    occupied = {
                        int(s.get("scheduled_slot"))
                        for s in db["scripts"]
                        if s.get("scheduled_date") == day_str and s.get("scheduled_slot") and not s.get("published")
                    }

            # Globally optimize the 6-pack slots before adding
            optimized_chunk = optimize_daily_basket_slots(chunk)

            for item in optimized_chunk:
                item_copy = dict(item)
                item_copy["scheduled_date"] = day_str
                # Use optimized slot directly
                slot_info = get_date_slot_info(day_str, item_copy.get("scheduled_slot", 1))
                item_copy["scheduled_time"] = slot_info["time_irst"]
                item_copy["recommended_time"] = slot_info["time_irst"]
                item_copy["window_label"] = slot_info["window_label"]
                item_copy["weekday_fa"] = slot_info["weekday_fa"]
                item_copy["online_followers"] = slot_info["online_followers"]
                item_copy["is_viral_hunted"] = True
                created = self.add_script(item_copy)
                created_scripts.append(created)

        return created_scripts

    def schedule_script(self, script_id: str, target_date: str, slot_num: int = None) -> dict:
        with DB_LOCK:
            db = self.load_db()
            target = next((s for s in db["scripts"] if s["id"] == script_id), None)
            if not target:
                raise ValueError(f"Script {script_id} not found")

            if not slot_num:
                occupied = {
                    s.get("scheduled_slot")
                    for s in db["scripts"]
                    if s["id"] != script_id and s.get("scheduled_date") == target_date and s.get("scheduled_slot")
                }
                slot_num = recommend_slot_for_archetype(
                    target.get("archetype", ""),
                    occupied,
                    target.get("content", ""),
                    target.get("title", "")
                )

            slot_num = max(1, min(6, int(slot_num)))
            slot_info = get_date_slot_info(target_date, slot_num)

            target["scheduled_date"] = target_date
            target["scheduled_slot"] = slot_num
            target["scheduled_time"] = slot_info["time_irst"]
            target["recommended_time"] = slot_info["time_irst"]
            target["window_label"] = slot_info["window_label"]
            target["weekday_fa"] = slot_info["weekday_fa"]
            target["online_followers"] = slot_info["online_followers"]

            self.save_db(db)
            return target

    def auto_schedule_date(self, target_date: str) -> list:
        """Automatically assigns and rebalances up to 6 scripts to their optimal circadian slots on target_date."""
        with DB_LOCK:
            db = self.load_db()
            day_scripts = [s for s in db["scripts"] if s.get("scheduled_date") == target_date]
            if len(day_scripts) < 6:
                for s in db["scripts"]:
                    if not s.get("published") and s not in day_scripts:
                        s["scheduled_date"] = target_date
                        day_scripts.append(s)
                        if len(day_scripts) == 6:
                            break

            # Run global basket optimization to match slots 1..6 with ideal archetypes
            optimized_basket = optimize_daily_basket_slots(day_scripts[:6])
            for opt_sc in optimized_basket:
                slot_num = opt_sc["scheduled_slot"]
                slot_info = get_date_slot_info(target_date, slot_num)
                opt_sc["scheduled_time"] = slot_info["time_irst"]
                opt_sc["recommended_time"] = slot_info["time_irst"]
                opt_sc["window_label"] = slot_info["window_label"]
                opt_sc["weekday_fa"] = slot_info["weekday_fa"]
                opt_sc["online_followers"] = slot_info["online_followers"]

                # Update in main db array
                for idx, existing in enumerate(db["scripts"]):
                    if existing["id"] == opt_sc["id"]:
                        db["scripts"][idx] = opt_sc
                        break

            self.save_db(db)
            return optimized_basket

    def rebalance_date_slots(self, target_date: str) -> list:
        """Alias for auto_schedule_date to globally rebalance circadian slot-archetype alignment."""
        return self.auto_schedule_date(target_date)

    def publish_script(self, script_id: str) -> dict:
        """Marks a script as published and atomically appends it to both published-content-history.md files."""
        with DB_LOCK:
            db = self.load_db()
            target = next((s for s in db["scripts"] if s["id"] == script_id), None)
            if not target:
                raise ValueError(f"Script {script_id} not found")

            # Read root history to determine next sequential number if not already assigned
            history_text = ""
            if os.path.exists(self.root_history_path):
                with open(self.root_history_path, "r", encoding="utf-8") as f:
                    history_text = f.read()

            if not target.get("published") or not target.get("history_reel_number"):
                next_num = self._get_next_history_number(db, history_text)
                target["published"] = True
                target["published_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                target["history_reel_number"] = next_num
            else:
                next_num = int(target["history_reel_number"])

            # Atomically ensure presence in both history files (idempotent)
            self._append_to_history_markdown(self.root_history_path, next_num, target)
            self._append_to_history_markdown(self.skill_history_path, next_num, target)

            self.save_db(db)
            return target

    def unpublish_script(self, script_id: str) -> dict:
        """Unchecks publish status and cleanly removes the entry from both published-content-history.md files."""
        with DB_LOCK:
            db = self.load_db()
            target = next((s for s in db["scripts"] if s["id"] == script_id), None)
            if not target:
                raise ValueError(f"Script {script_id} not found")

            reel_num = target.get("history_reel_number")
            if reel_num:
                self._remove_from_history_markdown(self.root_history_path, script_id, int(reel_num))
                self._remove_from_history_markdown(self.skill_history_path, script_id, int(reel_num))

            target["published"] = False
            target["published_at"] = None
            target["history_reel_number"] = None
            self.save_db(db)
            return target


ENGINE = PublisherEngine()


class RequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        super().end_headers()

    def _send_json(self, status_code: int, payload: dict):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/state":
            db = ENGINE.load_db()
            base_count = db.get("meta", {}).get("base_history_count", 233)
            if os.path.exists(ROOT_HISTORY_PATH):
                try:
                    with open(ROOT_HISTORY_PATH, "r", encoding="utf-8") as f:
                        h_matches = re.findall(r"### Reel #\d+", f.read())
                        if h_matches:
                            base_count = len(h_matches)
                except Exception:
                    pass
            self._send_json(200, {
                "ok": True,
                "meta": db["meta"],
                "total_history_count": base_count,
                "daily_6_slots": DAILY_6_SLOTS,
                "weekday_insights": WEEKDAY_INSIGHTS,
                "scripts": db["scripts"]
            })
            return
        if parsed.path == "/api/stories":
            s_db = ENGINE.load_stories_db()
            self._send_json(200, {
                "ok": True,
                "meta": s_db.get("meta", {}),
                "stories": s_db.get("stories", [])
            })
            return
        if parsed.path == "/api/telegram/config":
            try:
                import telegram_uploader
                cfg = telegram_uploader.load_config()
                self._send_json(200, {"ok": True, "config": cfg})
            except Exception as e:
                self._send_json(400, {"ok": False, "error": str(e)})
            return

        if parsed.path == "/api/telegram/banner-preview":
            try:
                from urllib.parse import parse_qs
                import telegram_uploader
                qs = parse_qs(parsed.query)
                target_date = qs.get("date", [datetime.now().strftime("%Y-%m-%d")])[0]
                text = telegram_uploader.build_daily_banner_message(target_date)
                self._send_json(200, {"ok": True, "date": target_date, "text": text})
            except Exception as e:
                self._send_json(400, {"ok": False, "error": str(e)})
            return

        if parsed.path == "/api/post-maker/render-preview":
            try:
                from urllib.parse import parse_qs
                qs = parse_qs(parsed.query)
                slot = int(qs.get("slot", [1])[0])
                date_str = qs.get("date", [datetime.now().strftime("%Y-%m-%d")])[0]
                item_type = qs.get("type", ["text"])[0]
                hook = qs.get("hook", [None])[0]
                content = qs.get("content", [None])[0]
                theme_override = qs.get("theme", [None])[0]
                
                custom_style = {}
                if "font_size" in qs:
                    custom_style["font_size"] = int(qs["font_size"][0])
                if "line_height" in qs:
                    custom_style["line_height"] = int(qs["line_height"][0])
                if "top_offset" in qs:
                    custom_style["top_offset"] = int(qs["top_offset"][0])
                if "is_bold" in qs:
                    custom_style["is_bold"] = qs["is_bold"][0].lower() in ["true", "1", "yes"]
                if "hl_color" in qs:
                    custom_style["hl_color"] = qs["hl_color"][0]
                if "cover_font_size" in qs:
                    custom_style["cover_font_size"] = int(qs["cover_font_size"][0])
                if "cover_line_height" in qs:
                    custom_style["cover_line_height"] = int(qs["cover_line_height"][0])
                if "cover_top_offset" in qs:
                    custom_style["cover_top_offset"] = int(qs["cover_top_offset"][0])
                if "cover_color" in qs:
                    custom_style["cover_color"] = qs["cover_color"][0]
                if "cover_is_bold" in qs:
                    custom_style["cover_is_bold"] = qs["cover_is_bold"][0].lower() in ["true", "1", "yes"]

                png_bytes = post_maker.render_preview_png_bytes(
                    slot=slot,
                    date_str=date_str,
                    item_type=item_type,
                    custom_hook=hook,
                    custom_content=content,
                    custom_style=custom_style,
                    theme_override=theme_override
                )
                self.send_response(200)
                self.send_header("Content-Type", "image/png")
                self.send_header("Content-Length", str(len(png_bytes)))
                self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
                self.end_headers()
                self.wfile.write(png_bytes)
            except Exception as e:
                self._send_json(400, {"ok": False, "error": str(e)})
            return

        if parsed.path == "/api/post-maker/preview":
            from urllib.parse import parse_qs
            qs = parse_qs(parsed.query)
            target_date = qs.get("date", [datetime.now().strftime("%Y-%m-%d")])[0]
            db = ENGINE.load_db()
            scripts = db.get("scripts", [])
            day_scripts = {int(s.get("scheduled_slot")): s for s in scripts if s.get("scheduled_date") == target_date and s.get("scheduled_slot")}
            
            import jdatetime
            try:
                parts = [int(p) for p in target_date.split("-")]
                j_date = jdatetime.date.fromgregorian(year=parts[0], month=parts[1], day=parts[2])
                shamsi_str = j_date.strftime("%Y-%m-%d")
            except Exception:
                shamsi_str = target_date
                
            catalog = post_maker.get_soundtracks_catalog() if post_maker else {"archetypes": {}}
            slot_to_default_arch = {1: 5, 2: 3, 3: 4, 4: 4, 5: 5, 6: 1}
            persian_to_eng = {'۱': 1, '۲': 2, '۳': 3, '۴': 4, '۵': 5, '۶': 6, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6}

            def get_hunted_reel_meta(script_dict, catalog_dict):
                if not script_dict:
                    return {"is_hunted": False}
                is_vh = bool(script_dict.get("is_viral_hunted"))
                s_url = (script_dict.get("source_url") or "").strip()
                s_page = (script_dict.get("source_page") or "").strip()
                s_views = (script_dict.get("source_views") or "").strip()
                raw_txt = (script_dict.get("extracted_raw_text") or "").strip()
                extra_nt = (script_dict.get("extra_notes") or "").strip()

                is_hunted = is_vh or bool(s_url) or bool(s_views) or bool(s_page)
                if not is_hunted:
                    return {"is_hunted": False}

                shortcode = ""
                if s_url:
                    m = re.search(r"/(?:reel|p)/([A-Za-z0-9_-]+)", s_url)
                    if m:
                        shortcode = m.group(1)

                matching_track = None
                if shortcode and catalog_dict:
                    for arch_k, tracks_list in catalog_dict.get("archetypes", {}).items():
                        for trk in tracks_list:
                            if trk.get("shortcode") == shortcode or (trk.get("url") and shortcode in trk.get("url")):
                                matching_track = dict(trk)
                                break
                        if matching_track:
                            break

                # Also scan local downloads/reels and assets for extracted audio if not in catalog
                if not matching_track and shortcode:
                    import glob
                    aud_candidates = (
                        glob.glob(f"downloads/reels/**/{shortcode}*.mp3", recursive=True) +
                        glob.glob(f"downloads/reels/**/*_{shortcode}_*.mp3", recursive=True) +
                        glob.glob(f"downloads/reels/**/*{shortcode}*.m4a", recursive=True) +
                        glob.glob(f"downloads/reels/**/*{shortcode}*.wav", recursive=True) +
                        glob.glob(f"assets/soundtracks/**/*{shortcode}*.mp3", recursive=True)
                    )
                    if aud_candidates and os.path.exists(aud_candidates[0]):
                        found_aud = os.path.abspath(aud_candidates[0])
                        rel_aud = os.path.relpath(found_aud, BASE_DIR).replace("\\", "/")
                        matching_track = {
                            "filename": os.path.basename(found_aud),
                            "relative_path": rel_aud,
                            "shortcode": shortcode,
                            "title": f"🎯 صدای استخراج‌شده ریلز مرجع ({shortcode})",
                            "duration_seconds": post_maker.get_audio_duration(found_aud) if post_maker else 7.0,
                            "url": s_url,
                            "filesize": os.path.getsize(found_aud),
                            "is_source_track": True
                        }

                local_video_path = None
                local_frame_path = None
                s_frame_custom = script_dict.get("confirmed_frame_path") or script_dict.get("local_frame_path")
                if s_frame_custom and os.path.exists(s_frame_custom):
                    local_frame_path = os.path.abspath(s_frame_custom)

                if shortcode:
                    import glob, subprocess
                    vids = (glob.glob(f"downloads/reels/**/{shortcode}*.mp4", recursive=True) +
                            glob.glob(f"downloads/reels/**/*_{shortcode}_*.mp4", recursive=True) +
                            glob.glob(f"downloads/reels/**/*{shortcode}*.mp4", recursive=True) +
                            glob.glob(f"assets/hunted_videos/*{shortcode}*.mp4"))
                    if vids and os.path.exists(vids[0]):
                        local_video_path = os.path.abspath(vids[0])

                    if not local_frame_path:
                        frames = (glob.glob(f"downloads/frames/*{shortcode}*.png") +
                                  glob.glob(f"downloads/frames/*{shortcode}*.jpg") +
                                  glob.glob(f"assets/hunted_frames/*{shortcode}*.jpg") +
                                  glob.glob(f"assets/hunted_frames/*{shortcode}*.png"))
                        if frames and os.path.exists(frames[0]):
                            local_frame_path = os.path.abspath(frames[0])

                    # Auto-extract keyframe if video exists but frame does not
                    if local_video_path and not local_frame_path:
                        try:
                            os.makedirs("downloads/frames", exist_ok=True)
                            gen_frame = os.path.abspath(f"downloads/frames/{shortcode}_frame.png")
                            cmd = ["ffmpeg", "-y", "-ss", "00:00:02", "-i", local_video_path, "-vframes", "1", "-q:v", "2", gen_frame]
                            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10)
                            if os.path.exists(gen_frame):
                                local_frame_path = gen_frame
                        except Exception:
                            pass

                import urllib.parse
                return {
                    "is_hunted": True,
                    "source_url": s_url,
                    "source_page": s_page,
                    "source_views": s_views,
                    "extracted_raw_text": raw_txt,
                    "extra_notes": extra_nt,
                    "shortcode": shortcode,
                    "matching_soundtrack": matching_track,
                    "local_video_path": local_video_path,
                    "local_frame_path": local_frame_path,
                    "local_video_url": f"/api/media/file-stream?path={urllib.parse.quote(local_video_path)}" if local_video_path else None,
                    "local_frame_url": f"/api/media/file-stream?path={urllib.parse.quote(local_frame_path)}" if local_frame_path else None,
                }

            items = []
            for slot in range(1, 7):
                s = day_scripts.get(slot)
                theme = "light" if slot in [1, 2, 6] else "dark"
                
                # Determine archetype number
                arch_num = slot_to_default_arch.get(slot, 1)
                arch_name = ""
                if s:
                    arch_raw = str(s.get("archetype_id") or s.get("archetype") or "")
                    arch_name = arch_raw
                    for p_ch, e_val in persian_to_eng.items():
                        if p_ch in arch_raw:
                            arch_num = e_val
                            break

                arch_tracks = catalog.get("archetypes", {}).get(str(arch_num), [])
                
                if s:
                    if post_maker:
                        hook = post_maker.clean_hook_text(s.get("hook"), s.get("title"), s.get("content"))
                    else:
                        hook = s.get("hook") or s.get("title") or ""
                        
                    hunted_meta = get_hunted_reel_meta(s, catalog)
                    slot_tracks = [dict(t) for t in arch_tracks]
                    source_soundtrack = hunted_meta.get("matching_soundtrack")
                    default_soundtrack = None

                    # If slot has a confirmed audio track extracted from reel or custom uploaded
                    custom_aud = s.get("confirmed_audio_path")
                    if custom_aud and os.path.exists(custom_aud):
                        found_aud = os.path.abspath(custom_aud)
                        rel_aud = os.path.relpath(found_aud, BASE_DIR).replace("\\", "/")
                        clean_fn = os.path.basename(found_aud)
                        source_soundtrack = {
                            "filename": clean_fn,
                            "relative_path": rel_aud,
                            "shortcode": hunted_meta.get("shortcode") or "custom",
                            "title": f"🎬 [صدای استخراج‌شده ریلز] {clean_fn}",
                            "duration_seconds": post_maker.get_audio_duration(found_aud) if post_maker else 7.0,
                            "filesize": os.path.getsize(found_aud),
                            "is_source_track": True,
                            "is_extracted_from_reel": True
                        }

                    if source_soundtrack:
                        existing_idx = next((i for i, t in enumerate(slot_tracks) if t.get("relative_path") == source_soundtrack.get("relative_path")), None)
                        if existing_idx is not None:
                            found_tr = slot_tracks.pop(existing_idx)
                            special_tr = dict(found_tr)
                            special_tr["is_source_track"] = True
                            special_tr["title"] = f"🎯 🌟 [موزیک ریلز مرجع] {special_tr.get('title', '')}"
                            slot_tracks.insert(0, special_tr)
                            default_soundtrack = special_tr["relative_path"]
                        else:
                            special_tr = dict(source_soundtrack)
                            special_tr["is_source_track"] = True
                            if not special_tr.get("title", "").startswith("🎯") and not special_tr.get("title", "").startswith("🎬"):
                                special_tr["title"] = f"🎯 🌟 [موزیک ریلز مرجع] {special_tr.get('title', '')}"
                            slot_tracks.insert(0, special_tr)
                            default_soundtrack = special_tr["relative_path"]
                    elif slot_tracks:
                        default_soundtrack = slot_tracks[0]["relative_path"]

                    items.append({
                        "slot": slot,
                        "theme": theme,
                        "title": s.get("title"),
                        "archetype": arch_num,
                        "archetype_name": arch_name,
                        "hook": hook,
                        "content": s.get("content", ""),
                        "script_id": s.get("id"),
                        "published": bool(s.get("published", False)),
                        "published_at": s.get("published_at"),
                        "history_reel_number": s.get("history_reel_number"),
                        "soundtracks": slot_tracks,
                        "default_soundtrack": default_soundtrack,
                        "is_hunted": hunted_meta.get("is_hunted", False),
                        "source_url": hunted_meta.get("source_url", ""),
                        "source_page": hunted_meta.get("source_page", ""),
                        "source_views": hunted_meta.get("source_views", ""),
                        "extracted_raw_text": hunted_meta.get("extracted_raw_text", ""),
                        "extra_notes": hunted_meta.get("extra_notes", ""),
                        "shortcode": hunted_meta.get("shortcode", ""),
                        "has_source_soundtrack": bool(source_soundtrack),
                        "source_soundtrack": source_soundtrack,
                        "local_video_url": hunted_meta.get("local_video_url"),
                        "local_frame_url": hunted_meta.get("local_frame_url"),
                        "frame_transcript_verified": bool(s.get("frame_transcript_verified", False)),
                        "caption": s.get("caption", ""),
                    })
                else:
                    items.append({
                        "slot": slot,
                        "theme": theme,
                        "title": None,
                        "archetype": arch_num,
                        "archetype_name": arch_name,
                        "hook": "",
                        "content": "",
                        "script_id": None,
                        "soundtracks": arch_tracks,
                        "default_soundtrack": arch_tracks[0]["relative_path"] if arch_tracks else None,
                        "is_hunted": False,
                        "source_url": "",
                        "source_page": "",
                        "source_views": "",
                        "extracted_raw_text": "",
                        "extra_notes": "",
                        "shortcode": "",
                        "has_source_soundtrack": False,
                        "source_soundtrack": None,
                        "local_video_url": None,
                        "local_frame_url": None,
                    })
            self._send_json(200, {
                "ok": True,
                "date": target_date,
                "shamsi_date": shamsi_str,
                "default_folder": get_posts_output_dir(shamsi_str),
                "catalog": catalog,
                "items": items
            })
            return
        if parsed.path == "/api/audio-stream":
            from urllib.parse import parse_qs
            qs = parse_qs(parsed.query)
            rel_file = qs.get("file", [""])[0]
            if not rel_file:
                self.send_error(400, "Missing file param")
                return
            safe_rel = os.path.normpath(rel_file.lstrip("/\\"))
            full_path = os.path.join(BASE_DIR, safe_rel)
            if not os.path.exists(full_path) or not os.path.isfile(full_path):
                self.send_error(404, "Audio file not found")
                return
            
            file_size = os.path.getsize(full_path)
            range_header = self.headers.get("Range")
            start = 0
            end = file_size - 1

            if range_header:
                # Handle bytes=start-end
                range_match = re.match(r"bytes=(\d+)-(\d*)", range_header)
                if range_match:
                    start = int(range_match.group(1))
                    if range_match.group(2):
                        end = int(range_match.group(2))
                    length = end - start + 1
                    self.send_response(206)
                    self.send_header("Content-Type", "audio/mpeg")
                    self.send_header("Content-Range", f"bytes {start}-{end}/{file_size}")
                    self.send_header("Content-Length", str(length))
                    self.send_header("Accept-Ranges", "bytes")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    with open(full_path, "rb") as f:
                        f.seek(start)
                        self.wfile.write(f.read(length))
                    return

            self.send_response(200)
            self.send_header("Content-Type", "audio/mpeg")
            self.send_header("Content-Length", str(file_size))
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            with open(full_path, "rb") as f:
                self.wfile.write(f.read())
        if parsed.path == "/api/post-maker/outputs":
            from urllib.parse import parse_qs
            qs = parse_qs(parsed.query)
            target_folder = qs.get("folder", [""])[0]
            if not target_folder:
                target_date = qs.get("date", [datetime.now().strftime("%Y-%m-%d")])[0]
                import jdatetime
                try:
                    parts = [int(p) for p in target_date.split("-")]
                    j_date = jdatetime.date.fromgregorian(year=parts[0], month=parts[1], day=parts[2])
                    shamsi_str = j_date.strftime("%Y-%m-%d")
                except Exception:
                    shamsi_str = target_date
                target_folder = get_posts_output_dir(shamsi_str)

            if not os.path.exists(target_folder):
                self._send_json(200, {"ok": True, "exists": False, "folder": target_folder, "slots": []})
                return

            slots = []
            for s in range(1, 7):
                c_name = f"post - {s} - cover.png"
                t_name = f"post - {s} - text.png"
                v_name_standard = f"post - {s}.mp4"
                v_name_legacy = f"post - {s} - reel.mp4"
                c_path = os.path.join(target_folder, c_name)
                t_path = os.path.join(target_folder, t_name)
                v_path_std = os.path.join(target_folder, v_name_standard)
                v_path_leg = os.path.join(target_folder, v_name_legacy)

                has_c = os.path.exists(c_path)
                has_t = os.path.exists(t_path)
                has_v = os.path.exists(v_path_std) or os.path.exists(v_path_leg)
                v_path = v_path_std if os.path.exists(v_path_std) else v_path_leg

                if has_c or has_t or has_v:
                    slots.append({
                        "slot": s,
                        "has_cover": has_c,
                        "cover_url": f"/api/media/file-stream?path={c_path}" if has_c else None,
                        "has_text": has_t,
                        "text_url": f"/api/media/file-stream?path={t_path}" if has_t else None,
                        "has_video": has_v,
                        "video_url": f"/api/media/file-stream?path={v_path}" if has_v else None,
                        "cover_size": os.path.getsize(c_path) if has_c else 0,
                        "text_size": os.path.getsize(t_path) if has_t else 0,
                        "video_size": os.path.getsize(v_path) if has_v else 0,
                    })

            self._send_json(200, {
                "ok": True,
                "exists": True,
                "folder": target_folder,
                "total_slots_ready": len(slots),
                "slots": slots
            })
            return

        if parsed.path == "/api/media/file-stream":
            from urllib.parse import parse_qs, unquote
            qs = parse_qs(parsed.query)
            file_path = qs.get("path", [""])[0]
            if not file_path:
                file_path = unquote(parsed.query.replace("path=", "", 1).split("&")[0])
            if not file_path or not os.path.exists(file_path):
                self.send_error(404, "File not found")
                return

            ext = os.path.splitext(file_path)[1].lower()
            mime = "application/octet-stream"
            if ext == ".png":
                mime = "image/png"
            elif ext == ".jpg" or ext == ".jpeg":
                mime = "image/jpeg"
            elif ext == ".mp4":
                mime = "video/mp4"
            elif ext == ".mp3":
                mime = "audio/mpeg"

            file_size = os.path.getsize(file_path)
            range_header = self.headers.get("Range")
            if range_header:
                range_match = re.match(r"bytes=(\d+)-(\d*)", range_header)
                if range_match:
                    start = int(range_match.group(1))
                    end = int(range_match.group(2)) if range_match.group(2) else file_size - 1
                    length = end - start + 1
                    self.send_response(206)
                    self.send_header("Content-Type", mime)
                    self.send_header("Content-Range", f"bytes {start}-{end}/{file_size}")
                    self.send_header("Content-Length", str(length))
                    self.send_header("Accept-Ranges", "bytes")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    with open(file_path, "rb") as f:
                        f.seek(start)
                        self.wfile.write(f.read(length))
                    return

            self.send_response(200)
            self.send_header("Content-Type", mime)
            self.send_header("Content-Length", str(file_size))
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            with open(file_path, "rb") as f:
                self.wfile.write(f.read())
            return

        if parsed.path == "/api/media/list-system-reels":
            from urllib.parse import parse_qs
            qs = parse_qs(parsed.query)
            target_date = qs.get("date", [""])[0]
            db = ENGINE.load_db()
            day_dirs = db.get("meta", {}).get("day_directories", {})
            custom_directory = day_dirs.get(target_date, "")
            reels = list_system_downloaded_reels(date_str=target_date, custom_directory=custom_directory)
            self._send_json(200, {"ok": True, "reels": reels})
            return

        return super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        length = int(self.headers.get("Content-Length", 0))
        raw_bytes = self.rfile.read(length) if length > 0 else b""
        try:
            raw_body = raw_bytes.decode("utf-8")
            payload = json.loads(raw_body) if raw_body else {}
        except Exception:
            payload = {}

        try:
            if parsed.path == "/api/stories/toggle-publish":
                sid = (payload.get("id") or "").strip()
                updated = ENGINE.toggle_publish_story(sid)
                self._send_json(200, {"ok": True, "story": updated})
                return

            if parsed.path == "/api/stories/save":
                with DB_LOCK:
                    s_db = ENGINE.load_stories_db()
                    sid = payload.get("id")
                    stories = s_db.get("stories", [])
                    idx = next((i for i, s in enumerate(stories) if s.get("id") == sid), -1)
                    if idx >= 0:
                        stories[idx] = payload
                    else:
                        stories.append(payload)
                    s_db["stories"] = stories
                    ENGINE.save_stories_db(s_db)
                self._send_json(200, {"ok": True, "story": payload})
                return

            if parsed.path == "/api/scripts":
                created = ENGINE.add_script(payload)
                self._send_json(200, {"ok": True, "script": created})
                return

            if parsed.path == "/api/scripts/auto-schedule-day":
                target_date = payload.get("date") or datetime.now().strftime("%Y-%m-%d")
                scheduled = ENGINE.auto_schedule_date(target_date)
                self._send_json(200, {"ok": True, "scheduled": scheduled})
                return

            if parsed.path == "/api/scripts/batch-import":
                items = payload.get("items") or []
                start_date = payload.get("start_date") or datetime.now().strftime("%Y-%m-%d")
                created_list = ENGINE.batch_import_and_schedule(items, start_date)
                self._send_json(200, {"ok": True, "created": created_list, "count": len(created_list)})
                return

            m_meta = re.match(r"^/api/scripts/([^/]+)/metadata$", parsed.path)
            if m_meta:
                sid = m_meta.group(1)
                updated = ENGINE.update_script_metadata(sid, payload)
                self._send_json(200, {"ok": True, "script": updated})
                return

            m_sched = re.match(r"^/api/scripts/([^/]+)/schedule$", parsed.path)
            if m_sched:
                sid = m_sched.group(1)
                target_date = payload.get("date") or datetime.now().strftime("%Y-%m-%d")
                slot_num = payload.get("slot")
                updated = ENGINE.schedule_script(sid, target_date, slot_num)
                self._send_json(200, {"ok": True, "script": updated})
                return

            m_pub = re.match(r"^/api/scripts/([^/]+)/publish$", parsed.path)
            if m_pub:
                sid = m_pub.group(1)
                updated = ENGINE.publish_script(sid)
                self._send_json(200, {"ok": True, "script": updated})
                return

            m_unpub = re.match(r"^/api/scripts/([^/]+)/unpublish$", parsed.path)
            if m_unpub:
                sid = m_unpub.group(1)
                updated = ENGINE.unpublish_script(sid)
                self._send_json(200, {"ok": True, "script": updated})
                return

            if parsed.path == "/api/media/download-and-extract":
                url = (payload.get("url") or "").strip()
                script_id = (payload.get("script_id") or "").strip()
                title = (payload.get("title") or "").strip()
                scheduled_date = (payload.get("scheduled_date") or "").strip()
                scheduled_slot = payload.get("scheduled_slot")
                custom_directory = (payload.get("custom_directory") or "").strip()

                db = ENGINE.load_db()
                if script_id:
                    target = next((s for s in db["scripts"] if s["id"] == script_id), None)
                    if target:
                        if not url:
                            url = (target.get("source_url") or "").strip()
                        if not title:
                            title = target.get("title") or ""
                        if not scheduled_date:
                            scheduled_date = target.get("scheduled_date") or ""
                        if scheduled_slot is None:
                            scheduled_slot = target.get("scheduled_slot")

                # If custom_directory was not passed, check configured day directory
                if not custom_directory and scheduled_date:
                    day_dirs = db.get("meta", {}).get("day_directories", {})
                    custom_directory = day_dirs.get(scheduled_date, "")

                if not url:
                    raise ValueError("آدرس اینترنتی ریلز (URL) وارد نشده است.")

                res = download_reel_and_extract_media(
                    url=url,
                    title=title,
                    scheduled_date=scheduled_date,
                    scheduled_slot=scheduled_slot,
                    custom_directory=custom_directory
                )
                if not res.get("ok"):
                    self._send_json(400, res)
                else:
                    self._send_json(200, res)
                return

            if parsed.path == "/api/settings/day-directory":
                date_str = (payload.get("date") or "").strip()
                dir_path = (payload.get("directory") or "").strip()
                if not date_str:
                    raise ValueError("تاریخ معتبر الزامی است.")
                with DB_LOCK:
                    db = ENGINE.load_db()
                    if "day_directories" not in db["meta"]:
                        db["meta"]["day_directories"] = {}
                    if dir_path:
                        db["meta"]["day_directories"][date_str] = dir_path
                    else:
                        db["meta"]["day_directories"].pop(date_str, None)
                    ENGINE.save_db(db)
                self._send_json(200, {
                    "ok": True,
                    "date": date_str,
                    "directory": dir_path,
                    "day_directories": db["meta"]["day_directories"]
                })
                return

            if parsed.path == "/api/media/open-explorer":
                target_path = (payload.get("path") or "").strip()
                if not target_path:
                    raise ValueError("مسیر فایل یا پوشه نامعتبر است.")
                ok = open_in_explorer(target_path)
                self._send_json(200, {"ok": ok, "path": target_path})
                return

            if parsed.path == "/api/post-maker/generate":
                target_date = payload.get("date") or datetime.now().strftime("%Y-%m-%d")
                custom_folder = (payload.get("folder") or "").strip()
                custom_hooks = payload.get("hooks") or {}
                generate_videos = bool(payload.get("generate_videos", False))
                custom_audios = payload.get("audios") or {}
                custom_styles = payload.get("styles") or {}
                import post_maker as pm
                result = pm.generate_daily_posts(
                    date_str=target_date,
                    target_folder=custom_folder if custom_folder else None,
                    custom_hooks=custom_hooks,
                    generate_videos=generate_videos,
                    custom_audios=custom_audios,
                    custom_styles=custom_styles
                )
                self._send_json(200, {"ok": True, "result": result})
                return

            if parsed.path in ["/api/post-maker/generate-single", "/api/post-maker/generate-slot"]:
                slot = int(payload.get("slot", 1))
                target_date = payload.get("date") or datetime.now().strftime("%Y-%m-%d")
                custom_folder = (payload.get("folder") or "").strip()
                custom_hook = (payload.get("hook") or "").strip()
                generate_video = bool(payload.get("generate_video", True))
                custom_audio = (payload.get("audio") or "").strip()
                custom_style = payload.get("style") or {}
                import post_maker as pm
                result = pm.generate_single_post(
                    slot=slot,
                    date_str=target_date,
                    target_folder=custom_folder if custom_folder else None,
                    custom_hook=custom_hook,
                    generate_video=generate_video,
                    custom_audio=custom_audio,
                    custom_style=custom_style
                )
                self._send_json(200, {"ok": True, "result": result})
                return

            if parsed.path == "/api/post-maker/open-folder":
                folder_path = (payload.get("folder") or "").strip()
                if not folder_path or not os.path.exists(folder_path):
                    self._send_json(400, {"ok": False, "error": "Folder not found"})
                    return
                open_in_explorer(folder_path)
                self._send_json(200, {"ok": True, "folder": folder_path})
                return

            if parsed.path == "/api/media/upload-frame":
                import base64
                img_data_b64 = payload.get("image_data", "")
                script_id = (payload.get("script_id") or "").strip()
                date_str = (payload.get("date") or "").strip()
                slot = payload.get("slot")
                shortcode = (payload.get("shortcode") or "").strip()

                if not img_data_b64:
                    self._send_json(400, {"ok": False, "error": "image_data is required"})
                    return

                if "base64," in img_data_b64:
                    img_data_b64 = img_data_b64.split("base64,")[1]

                raw_bytes = base64.b64decode(img_data_b64)
                os.makedirs("downloads/frames", exist_ok=True)
                file_prefix = shortcode or f"{date_str}_slot{slot}" if (date_str and slot) else f"manual_{int(datetime.now().timestamp())}"
                saved_frame_path = os.path.abspath(f"downloads/frames/{file_prefix}_custom_frame.png")

                with open(saved_frame_path, "wb") as f:
                    f.write(raw_bytes)

                # Persist in scripts-db.json if script_id or date+slot matches
                if script_id or (date_str and slot):
                    with DB_LOCK:
                        db = ENGINE.load_db()
                        for s in db.get("scripts", []):
                            match_id = script_id and (s.get("id") == script_id)
                            match_slot = date_str and slot and (s.get("scheduled_date") == date_str) and (str(s.get("scheduled_slot")) == str(slot))
                            if match_id or match_slot:
                                s["confirmed_frame_path"] = saved_frame_path
                                break
                        ENGINE.save_db(db)

                import urllib.parse
                frame_url = f"/api/media/file-stream?path={urllib.parse.quote(saved_frame_path)}"
                self._send_json(200, {
                    "ok": True,
                    "frame_path": saved_frame_path,
                    "frame_url": frame_url
                })
                return

            if parsed.path == "/api/media/upload-audio":
                import base64
                audio_data_b64 = payload.get("audio_data", "")
                script_id = (payload.get("script_id") or "").strip()
                date_str = (payload.get("date") or datetime.now().strftime("%Y-%m-%d")).strip()
                slot = payload.get("slot") or 1
                shortcode = (payload.get("shortcode") or "").strip()
                orig_filename = payload.get("filename") or "audio.mp3"
                clean_ext = os.path.splitext(orig_filename)[1] or ".mp3"
                if not clean_ext.lower() in [".mp3", ".m4a", ".wav", ".aac", ".ogg"]:
                    clean_ext = ".mp3"

                if not audio_data_b64:
                    self._send_json(400, {"ok": False, "error": "محتوای فایل صوتی (audio_data) ارسال نشده است."})
                    return

                if "base64," in audio_data_b64:
                    audio_data_b64 = audio_data_b64.split("base64,")[1]

                raw_bytes = base64.b64decode(audio_data_b64)
                out_dir = os.path.join(BASE_DIR, "downloads", "reels", date_str)
                os.makedirs(out_dir, exist_ok=True)
                slot_int = int(slot) if str(slot).isdigit() else 1
                clean_fn = f"{date_str}_Slot-{slot_int:02d}_{shortcode or 'custom'}_audio{clean_ext}"
                saved_audio_path = os.path.abspath(os.path.join(out_dir, clean_fn))

                with open(saved_audio_path, "wb") as f:
                    f.write(raw_bytes)

                rel_p = os.path.relpath(saved_audio_path, BASE_DIR).replace("\\", "/")
                dur = post_maker.get_audio_duration(saved_audio_path) if post_maker else 7.0

                track_obj = {
                    "filename": clean_fn,
                    "relative_path": rel_p,
                    "shortcode": shortcode,
                    "title": f"🎯 🌟 [موزیک آپلودشده ریلز مرجع] {orig_filename}",
                    "duration_seconds": dur,
                    "filesize": len(raw_bytes),
                    "is_source_track": True
                }

                self._send_json(200, {
                    "ok": True,
                    "audio_path": saved_audio_path,
                    "relative_path": rel_p,
                    "audio_filename": clean_fn,
                    "web_audio_url": f"/{rel_p}",
                    "track": track_obj
                })
                return

            if parsed.path == "/api/media/extract-audio-from-video":
                slot = payload.get("slot") or 1
                date_str = (payload.get("date") or datetime.now().strftime("%Y-%m-%d")).strip()
                title = (payload.get("title") or "").strip()
                script_id = (payload.get("script_id") or "").strip()
                video_path = (payload.get("video_path") or "").strip()
                video_data_b64 = payload.get("video_data", "")
                orig_filename = (payload.get("filename") or "reel.mp4").strip()

                db = ENGINE.load_db()
                day_dirs = db.get("meta", {}).get("day_directories", {})
                custom_directory = day_dirs.get(date_str, "")

                target_video_file = ""

                # Handle uploaded video (base64)
                if video_data_b64:
                    import base64
                    if "base64," in video_data_b64:
                        video_data_b64 = video_data_b64.split("base64,")[1]
                    raw_bytes = base64.b64decode(video_data_b64)

                    if custom_directory and os.path.isdir(custom_directory):
                        out_dir = os.path.normpath(custom_directory)
                    else:
                        out_dir = os.path.normpath(os.path.join(BASE_DIR, "downloads", "reels", date_str))
                    os.makedirs(out_dir, exist_ok=True)

                    slot_int = int(slot) if str(slot).isdigit() else 1
                    stem = os.path.splitext(orig_filename)[0]
                    clean_stem = re.sub(r"[^\w\u0600-\u06FF]+", "_", stem).strip("_")[:30] or "custom"
                    clean_ext = os.path.splitext(orig_filename)[1] or ".mp4"
                    clean_fn = f"{date_str}_Slot-{slot_int:02d}_{clean_stem}_video{clean_ext}"
                    target_video_file = os.path.join(out_dir, clean_fn)
                    with open(target_video_file, "wb") as f:
                        f.write(raw_bytes)
                elif video_path:
                    # Clean up Windows quotes if user pasted path with quotes
                    video_path = video_path.strip('\'"')
                    if not os.path.exists(video_path):
                        self._send_json(400, {"ok": False, "error": f"فایل ویدیویی در مسیر مشخص‌شده یافت نشد: {video_path}"})
                        return
                    target_video_file = os.path.normpath(video_path)
                else:
                    self._send_json(400, {"ok": False, "error": "هیچ فایل یا مسیری برای ویدیوی ریلز مشخص نشده است."})
                    return

                res = extract_audio_from_local_video(
                    video_path=target_video_file,
                    title=title,
                    scheduled_date=date_str,
                    scheduled_slot=slot,
                    custom_directory=custom_directory,
                    open_explorer=False
                )

                if not res.get("ok"):
                    self._send_json(400, res)
                    return

                # Persist in scripts-db.json for this slot and date
                with DB_LOCK:
                    db = ENGINE.load_db()
                    for s in db.get("scripts", []):
                        match_id = script_id and (s.get("id") == script_id)
                        match_slot = date_str and slot and (s.get("scheduled_date") == date_str) and (str(s.get("scheduled_slot")) == str(slot))
                        if match_id or match_slot:
                            s["confirmed_audio_path"] = res["audio_path"]
                            s["confirmed_video_path"] = target_video_file
                            if res.get("frame_path"):
                                s["confirmed_frame_path"] = res["frame_path"]
                            break
                    ENGINE.save_db(db)

                self._send_json(200, res)
                return

            if parsed.path == "/api/telegram/config":
                import telegram_uploader
                cfg = telegram_uploader.load_config()
                cfg["bot_token"] = (payload.get("bot_token") or "").strip()
                cfg["channel_id"] = (payload.get("channel_id") or "").strip()
                cfg["proxy_url"] = (payload.get("proxy_url") or "").strip()
                if "send_as_document" in payload:
                    cfg["send_as_document"] = bool(payload.get("send_as_document"))
                if "include_slot_time" in payload:
                    cfg["include_slot_time"] = bool(payload.get("include_slot_time"))
                ok = telegram_uploader.save_config(cfg)
                self._send_json(200, {"ok": ok, "config": cfg})
                return

            if parsed.path == "/api/telegram/test":
                import telegram_uploader
                token = (payload.get("bot_token") or "").strip()
                chat_id = (payload.get("channel_id") or "").strip()
                proxy = (payload.get("proxy_url") or "").strip()
                res = telegram_uploader.test_telegram_connection(token, chat_id, proxy)
                self._send_json(200, res)
                return

            if parsed.path == "/api/telegram/upload-slot":
                import telegram_uploader
                slot = int(payload.get("slot", 1))
                date_str = payload.get("date") or datetime.now().strftime("%Y-%m-%d")
                folder = (payload.get("folder") or "").strip()
                custom_caption = payload.get("caption")
                res = telegram_uploader.upload_single_slot(slot, date_str, target_folder=folder if folder else None, custom_caption=custom_caption)
                self._send_json(200, res)
                return

            if parsed.path == "/api/telegram/upload-all":
                import telegram_uploader
                date_str = payload.get("date") or datetime.now().strftime("%Y-%m-%d")
                folder = (payload.get("folder") or "").strip()
                captions_override = payload.get("captions") or {}
                res = telegram_uploader.upload_all_daily_slots(date_str, target_folder=folder if folder else None, captions_override=captions_override)
                self._send_json(200, res)
                return

            if parsed.path == "/api/telegram/send-banner":
                import telegram_uploader
                date_str = payload.get("date") or datetime.now().strftime("%Y-%m-%d")
                res = telegram_uploader.send_daily_banner(date_str)
                self._send_json(200, res)
                return

            if parsed.path == "/api/post-maker/render-preview":
                import base64
                slot = int(payload.get("slot", 1))
                date_str = payload.get("date") or datetime.now().strftime("%Y-%m-%d")
                item_type = payload.get("type", "text")
                hook = payload.get("hook")
                content = payload.get("content")
                custom_style = payload.get("custom_style") or {}
                theme_override = payload.get("theme")

                png_bytes = post_maker.render_preview_png_bytes(
                    slot=slot,
                    date_str=date_str,
                    item_type=item_type,
                    custom_hook=hook,
                    custom_content=content,
                    custom_style=custom_style,
                    theme_override=theme_override
                )
                b64_str = base64.b64encode(png_bytes).decode("ascii")
                data_url = f"data:image/png;base64,{b64_str}"
                self._send_json(200, {
                    "ok": True,
                    "slot": slot,
                    "type": item_type,
                    "data_url": data_url,
                    "size_bytes": len(png_bytes)
                })
                return

            self._send_json(404, {"ok": False, "error": "Endpoint not found"})
        except Exception as e:
            self._send_json(400, {"ok": False, "error": str(e)})


def run_server(port=None):
    if port is None:
        port = int(os.environ.get("PORT", 8765))
    host = os.environ.get("HOST", "0.0.0.0")
    server = ThreadingHTTPServer((host, port), RequestHandler)
    print(f"RozeText Publisher Server running on http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run_server()
