import sys

sys.stdout.reconfigure(encoding='utf-8')

# The 7 days from the screenshots:
# Buckets: 12a, 3a, 6a, 9a, 12p, 3p, 6p, 9p
data = {
    "M":  {"name_fa": "دوشنبه", "12a": 16217, "3a": 17859, "6a": 16836, "9a": 19159, "12p": 18702, "3p": 7445, "6p": 6142, "9p": 12448},
    "Tu": {"name_fa": "سه‌شنبه", "12a": 16684, "3a": 18379, "6a": 17327, "9a": 19590, "12p": 19029, "3p": 7582, "6p": 6422, "9p": 12934},
    "W":  {"name_fa": "چهارشنبه", "12a": 17145, "3a": 18872, "6a": 17886, "9a": 20121, "12p": 19860, "3p": 8388, "6p": 5931, "9p": 12861},
    "Th": {"name_fa": "پنج‌شنبه", "12a": 17853, "3a": 19453, "6a": 18108, "9a": 20184, "12p": 20355, "3p": 9843, "6p": 5590, "9p": 12078},
    "F":  {"name_fa": "جمعه", "12a": 19116, "3a": 20471, "6a": 19691, "9a": 21970, "12p": 20951, "3p": 8443, "6p": 6859, "9p": 14008},
    "Sa": {"name_fa": "شنبه", "12a": 18696, "3a": 20771, "6a": 19857, "9a": 22565, "12p": 21669, "3p": 8354, "6p": 7121, "9p": 14462},
    "Su": {"name_fa": "یکشنبه", "12a": 19250, "3a": 21312, "6a": 20188, "9a": 23060, "12p": 22113, "3p": 8470, "6p": 7322, "9p": 14853},
}

# In server.py:
# Weekday index: 0 = Monday, 1 = Tuesday, 2 = Wednesday, 3 = Thursday, 4 = Friday, 5 = Saturday, 6 = Sunday
# Slots:
# Slot 1: 09:30 IRST -> mapped to 9p bucket (08:30-11:29 IRST)
# Slot 2: 12:15 IRST -> mapped to 12a bucket (11:30-14:29 IRST)
# Slot 3: 15:00 IRST -> mapped to 3a bucket (14:30-17:29 IRST)
# Slot 4: 18:15 IRST -> mapped to 6a bucket (17:30-20:29 IRST)
# Slot 5: 21:00 IRST -> mapped to 9a bucket (20:30-23:29 IRST)
# Slot 6: 23:45 IRST -> mapped to 12p bucket (23:30-02:29 IRST)

print("=== 7-DAY INSIGHTS SUMMARY ===")
day_order = ["M", "Tu", "W", "Th", "F", "Sa", "Su"]
weekday_insights = {}

for idx, k in enumerate(day_order):
    v = data[k]
    values = [v["12a"], v["3a"], v["6a"], v["9a"], v["12p"], v["3p"], v["6p"], v["9p"]]
    peak = max(values)
    avg = sum(values) // len(values)
    slots = {
        1: v["9p"],
        2: v["12a"],
        3: v["3a"],
        4: v["6a"],
        5: v["9a"],
        6: v["12p"]
    }
    weekday_insights[idx] = {
        "name_fa": v["name_fa"],
        "peak": peak,
        "avg": avg,
        "slots": slots
    }
    print(f"{v['name_fa']} ({k}): Peak={peak:,} | Avg={avg:,} | S5(21:00)={slots[5]:,} | S6(23:45)={slots[6]:,}")

print("\n--- Python code for WEEKDAY_INSIGHTS in server.py ---")
import pprint
pprint.pprint(weekday_insights, sort_dicts=False)
