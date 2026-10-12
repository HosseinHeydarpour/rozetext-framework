import os
import sys
import json
import time
import re
import requests
from datetime import datetime

try:
    import jdatetime
except ImportError:
    jdatetime = None

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
CONFIG_PATH = os.path.join(DATA_DIR, "telegram_config.json")
DB_PATH = os.path.join(DATA_DIR, "scripts-db.json")

SLOT_TIMES = {
    1: {"time": "09:30", "label": "۰۹:۳۰ صبح (موج اول: شروع روز و مسیر کار)"},
    2: {"time": "12:15", "label": "۱۲:۱۵ ظهر (موج دوم: تایم استراحت ظهرگاهی)"},
    3: {"time": "15:00", "label": "۱۵:۰۰ بعدازظهر (موج سوم: اوج استراحت عصر)"},
    4: {"time": "18:15", "label": "۱۸:۱۵ عصر (موج چهارم: پیش‌راه‌اندازی شبانه)"},
    5: {"time": "21:00", "label": "۲۱:۰۰ شب (موج پنجم: بمب اول پیک مطلق شبانه)"},
    6: {"time": "23:45", "label": "۲۳:۴۵ آخر شب (موج ششم: بمب دوم نیمه‌شب و دلتنگی)"},
}

def load_config() -> dict:
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "bot_token": "",
        "channel_id": "",
        "proxy_url": "",
        "send_as_document": True,
        "include_slot_time": True,
        "send_daily_banner": True,
        "custom_template": ""
    }

def save_config(cfg: dict) -> bool:
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error saving telegram config: {e}")
        return False

def get_request_proxies(proxy_url: str = ""):
    if not proxy_url:
        cfg = load_config()
        proxy_url = cfg.get("proxy_url", "").strip()
    if proxy_url:
        return {"http": proxy_url, "https": proxy_url}
    return None

def test_telegram_connection(bot_token: str = None, channel_id: str = None, proxy_url: str = None) -> dict:
    cfg = load_config()
    token = (bot_token or cfg.get("bot_token", "")).strip()
    chat_id = (channel_id or cfg.get("channel_id", "")).strip()
    proxy = proxy_url if proxy_url is not None else cfg.get("proxy_url", "").strip()

    if not token:
        return {"ok": False, "error": "توکن ربات تلگرام (Bot Token) وارد نشده است."}

    proxies = get_request_proxies(proxy)
    api_url = f"https://api.telegram.org/bot{token}"

    try:
        # 1. Test Bot Token via getMe
        r = requests.get(f"{api_url}/getMe", proxies=proxies, timeout=12)
        res = r.json()
        if not res.get("ok"):
            return {"ok": False, "error": f"توکن ربات نامعتبر است: {res.get('description', '')}"}

        bot_info = res.get("result", {})
        bot_username = bot_info.get("username", "")
        bot_first_name = bot_info.get("first_name", "")

        # 2. Test Channel if provided
        channel_info = None
        if chat_id:
            r_chat = requests.get(f"{api_url}/getChat", params={"chat_id": chat_id}, proxies=proxies, timeout=12)
            res_chat = r_chat.json()
            if not res_chat.get("ok"):
                desc = res_chat.get("description", "")
                return {
                    "ok": False,
                    "bot_ok": True,
                    "bot_username": bot_username,
                    "bot_name": bot_first_name,
                    "error": f"ربات تایید شد اما دسترسی به کانال {chat_id} ندارد ({desc}). لطفاً ربات @{bot_username} را ادمین کانال کنید."
                }
            channel_info = res_chat.get("result", {})

        return {
            "ok": True,
            "bot_username": bot_username,
            "bot_name": bot_first_name,
            "channel_title": channel_info.get("title") if channel_info else None,
            "channel_id": channel_info.get("id") if channel_info else chat_id
        }
    except requests.exceptions.ProxyError:
        return {"ok": False, "error": "خطا در اتصال به پروکسی! لطفاً آدرس و پورت پروکسی را بررسی کنید."}
    except requests.exceptions.ConnectionError:
        return {"ok": False, "error": "خطای عدم دسترسی به سرور تلگرام! لطفاً فیلترشکن سیستم را روشن کنید یا آدرس پروکسی را تنظیم نمایید."}
    except Exception as e:
        return {"ok": False, "error": f"خطا در ارتباط با تلگرام: {str(e)}"}

def format_telegram_caption(slot: int, raw_caption: str, hook: str = None, include_time: bool = True, slot_time_override: str = None) -> str:
    time_str = slot_time_override
    if not time_str:
        time_info = SLOT_TIMES.get(int(slot), {"time": "12:15", "label": "ظهر"})
        time_str = time_info.get("time", "12:15")
    
    parts = []
    if include_time:
        parts.append(f"⏰ ساعت انتشار: {time_str} (اسلات {slot})")
        parts.append("")

    clean_cap = (raw_caption or "").strip()
    if clean_cap:
        parts.append(clean_cap)
    elif hook:
        parts.append(hook.strip())

    return "\n".join(parts).strip()

PERSIAN_WEEKDAYS = ["شنبه", "یکشنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنجشنبه", "جمعه"]
PERSIAN_MONTHS = ["فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور", "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"]

def to_persian_digits(text) -> str:
    en_digits = "0123456789"
    fa_digits = "۰۱۲۳۴۵۶۷۸۹"
    res = []
    for ch in str(text):
        if ch in en_digits:
            res.append(fa_digits[en_digits.index(ch)])
        else:
            res.append(ch)
    return "".join(res)

def build_daily_banner_message(date_str: str, cfg: dict = None) -> str:
    """
    Builds an aesthetic visual Telegram box card for the daily publishing schedule,
    including Persian weekday, Shamsi date, Gregorian date, and the 6 golden slot times.
    """
    try:
        parts = [int(p) for p in date_str.split("-")]
        dt = datetime(parts[0], parts[1], parts[2]).date()
    except Exception:
        dt = datetime.now().date()

    weekday_name = "امروز"
    shamsi_str = date_str
    if jdatetime:
        try:
            jd = jdatetime.date.fromgregorian(date=dt)
            weekday_name = PERSIAN_WEEKDAYS[jd.weekday()]
            month_name = PERSIAN_MONTHS[jd.month - 1]
            shamsi_day = to_persian_digits(jd.day)
            shamsi_year = to_persian_digits(jd.year)
            shamsi_str = f"{shamsi_day} {month_name} {shamsi_year}"
        except Exception:
            pass
    else:
        weekday_map = {0: "دوشنبه", 1: "سه‌شنبه", 2: "چهارشنبه", 3: "پنجشنبه", 4: "جمعه", 5: "شنبه", 6: "یکشنبه"}
        weekday_name = weekday_map.get(dt.weekday(), "امروز")

    gregorian_str = dt.strftime("%Y/%m/%d")

    banner = (
        "<blockquote>\n"
        "🌹 <b>بسته انتشار ۶ ریلز روزانه رز تکست (@rozetext.ir)</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🗓 <b>روز:</b> {weekday_name}\n"
        f"📅 <b>تاریخ شمسی:</b> {shamsi_str}\n"
        f"🌐 <b>تاریخ میلادی:</b> {gregorian_str}\n"
        "</blockquote>\n\n"
        "⏰ <b>جدول زمان‌بندی ۶ تایم طلایی انتشار:</b>\n"
        "  ➊ <b>۰۹:۳۰</b> ── اسلات اول (صبحگاه: شروع روز)\n"
        "  ➋ <b>۱۲:۱۵</b> ── اسلات دوم (ظهرگاه: استراحت ظهر)\n"
        "  ➌ <b>۱۵:۰۰</b> ── اسلات سوم (عصرگاه: اوج استراحت عصر)\n"
        "  ➍ <b>۱۸:۱۵</b> ── اسلات چهارم (غروب: پیش‌راه‌اندازی شب)\n"
        "  ➎ <b>۲۱:۰۰</b> ── اسلات پنجم (بمب اول پیک شبانه 🔥)\n"
        "  ➏ <b>۲۳:۴۵</b> ── اسلات ششم (بمب دوم نیمه‌شب 🔥)\n\n"
        "<blockquote>\n"
        "📦 <b>محتویات این بسته:</b>\n"
        "• ۶ کاور کریستالی (IRTitr ۱۰۸۰×۱۹۲۰)\n"
        "• ۶ ویدیوی ریلز کامل همراه با موزیک آرکتایپ (کیفیت اصلی)\n"
        "• کپشن کامل هر پست و ساعت دقیق انتشار\n"
        "</blockquote>\n\n"
        "✨ <i>فایل‌های امروز به ترتیب در ادامه ارسال می‌شوند 👇</i>"
    )
    return banner

def send_daily_banner(date_str: str, cfg: dict = None) -> dict:
    cfg = cfg or load_config()
    token = cfg.get("bot_token", "").strip()
    chat_id = cfg.get("channel_id", "").strip()
    proxy = cfg.get("proxy_url", "").strip()

    if not token or not chat_id:
        return {"ok": False, "error": "توکن ربات تلگرام یا آیدی کانال تنظیم نشده است."}

    text = build_daily_banner_message(date_str, cfg=cfg)
    proxies = get_request_proxies(proxy)
    api_url = f"https://api.telegram.org/bot{token}"

    try:
        data = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML"
        }
        r = requests.post(f"{api_url}/sendMessage", data=data, proxies=proxies, timeout=25)
        res = r.json()
        if not res.get("ok"):
            # Fallback without HTML tags if parse fails
            data["parse_mode"] = ""
            data["text"] = re.sub(r"<[^>]+>", "", text)
            r2 = requests.post(f"{api_url}/sendMessage", data=data, proxies=proxies, timeout=25)
            res2 = r2.json()
            if not res2.get("ok"):
                return {"ok": False, "error": f"خطا در ارسال بنر روز: {res.get('description', '')}"}
            res = res2

        msg_id = res.get("result", {}).get("message_id")
        return {"ok": True, "message_id": msg_id, "text": text}
    except Exception as e:
        return {"ok": False, "error": f"خطای ارسال پیام بنر روزانه: {str(e)}"}

def upload_single_slot(slot: int, date_str: str, target_folder: str = None, custom_caption: str = None, cfg: dict = None) -> dict:
    cfg = cfg or load_config()
    token = cfg.get("bot_token", "").strip()
    chat_id = cfg.get("channel_id", "").strip()
    proxy = cfg.get("proxy_url", "").strip()
    send_as_doc = cfg.get("send_as_document", True)
    include_time = cfg.get("include_slot_time", True)

    if not token or not chat_id:
        return {"ok": False, "error": "تنظیمات تلگرام (توکن ربات یا آیدی کانال) کامل نیست."}

    # Determine folder path
    if not target_folder:
        import jdatetime
        parts = [int(p) for p in date_str.split("-")]
        j_date = jdatetime.date.fromgregorian(year=parts[0], month=parts[1], day=parts[2])
        shamsi_str = j_date.strftime("%Y-%m-%d")
        target_folder = os.path.join(r"D:\زر تکست", shamsi_str)

    if not os.path.exists(target_folder):
        return {"ok": False, "error": f"پوشه فایل‌ها یافت نشد: {target_folder}"}

    cover_file = f"post - {slot} - cover.png"
    cover_path = os.path.join(target_folder, cover_file)
    
    video_file = f"post - {slot}.mp4"
    video_path = os.path.join(target_folder, video_file)

    if not os.path.exists(cover_path):
        return {"ok": False, "error": f"فایل کاور یافت نشد: {cover_file}"}

    has_video = os.path.exists(video_path)

    # Get caption and recommended_time from DB if not customized
    rec_time = None
    if custom_caption is None:
        try:
            with open(DB_PATH, "r", encoding="utf-8") as f:
                db = json.load(f)
            script = next((s for s in db.get("scripts", []) if s.get("scheduled_date") == date_str and int(s.get("scheduled_slot", 0)) == int(slot)), None)
            raw_caption = script.get("caption", "") if script else ""
            hook = script.get("hook", "") if script else ""
            if script and script.get("recommended_time"):
                rec_time = script.get("recommended_time")
        except Exception:
            raw_caption = ""
            hook = ""
    else:
        raw_caption = custom_caption
        hook = ""

    formatted_caption = format_telegram_caption(slot, raw_caption, hook, include_time=include_time, slot_time_override=rec_time)
    # Telegram caption length limit is 1024 chars
    if len(formatted_caption) > 1020:
        formatted_caption = formatted_caption[:1017] + "..."

    proxies = get_request_proxies(proxy)
    api_url = f"https://api.telegram.org/bot{token}"

    try:
        # Build Media Group if video exists
        if has_video:
            media_type = "document" if send_as_doc else "document"
            media_group = [
                {
                    "type": media_type,
                    "media": "attach://cover_file",
                },
                {
                    "type": media_type,
                    "media": "attach://video_file",
                    "caption": formatted_caption
                }
            ]
            
            with open(cover_path, "rb") as fc, open(video_path, "rb") as fv:
                files = {
                    "cover_file": (cover_file, fc, "image/png"),
                    "video_file": (video_file, fv, "video/mp4")
                }
                data = {
                    "chat_id": chat_id,
                    "media": json.dumps(media_group)
                }
                r = requests.post(f"{api_url}/sendMediaGroup", data=data, files=files, proxies=proxies, timeout=90)
                res = r.json()
                if not res.get("ok"):
                    # Fallback: send cover then send video
                    desc = res.get("description", "")
                    return {"ok": False, "error": f"خطا در ارسال آلبوم تلگرام: {desc}"}
                
                return {
                    "ok": True,
                    "slot": slot,
                    "caption": formatted_caption,
                    "message_ids": [m.get("message_id") for m in res.get("result", [])]
                }
        else:
            # Only cover file exists
            with open(cover_path, "rb") as fc:
                files = {"document": (cover_file, fc, "image/png")}
                data = {
                    "chat_id": chat_id,
                    "caption": formatted_caption
                }
                r = requests.post(f"{api_url}/sendDocument", data=data, files=files, proxies=proxies, timeout=60)
                res = r.json()
                if not res.get("ok"):
                    return {"ok": False, "error": f"خطا در ارسال کاور: {res.get('description', '')}"}
                return {
                    "ok": True,
                    "slot": slot,
                    "caption": formatted_caption,
                    "message_ids": [res.get("result", {}).get("message_id")]
                }

    except Exception as e:
        return {"ok": False, "slot": slot, "error": f"خطای ارسال تلگرام: {str(e)}"}

def upload_all_daily_slots(date_str: str, target_folder: str = None, captions_override: dict = None) -> dict:
    cfg = load_config()
    token = cfg.get("bot_token", "").strip()
    chat_id = cfg.get("channel_id", "").strip()
    if not token or not chat_id:
        return {"ok": False, "error": "لطفاً ابتدا در بخش تنظیمات تلگرام، توکن ربات و آیدی کانال را وارد نمایید."}

    # Send daily banner box before slots if enabled
    send_banner = cfg.get("send_daily_banner", True)
    banner_result = None
    if send_banner:
        banner_result = send_daily_banner(date_str, cfg=cfg)
        time.sleep(2.0)

    captions_override = captions_override or {}
    results = []
    success_count = 0

    for slot in range(1, 7):
        custom_cap = captions_override.get(str(slot)) or captions_override.get(slot)
        res = upload_single_slot(slot, date_str, target_folder=target_folder, custom_caption=custom_cap, cfg=cfg)
        results.append(res)
        if res.get("ok"):
            success_count += 1
        # 1.8s delay between slots to stay completely safe with Telegram rate limits
        if slot < 6:
            time.sleep(1.8)

    return {
        "ok": success_count > 0,
        "total": 6,
        "banner_sent": (banner_result.get("ok") if banner_result else False),
        "banner_result": banner_result,
        "success_count": success_count,
        "results": results
    }
