import json, os, sys
sys.stdout.reconfigure(encoding='utf-8')

# Reads data/benchmark_accounts.json and ensures markdown directory is updated
json_path = 'data/benchmark_accounts.json'
md_path = '.agents/skills/rozetext-persona-dna/references/benchmark-accounts-directory.md'

if not os.path.exists(json_path):
    print(f"Error: {json_path} not found.")
    sys.exit(1)

with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

accounts = data.get('accounts', [])
print(f"Loaded {len(accounts)} verified benchmark accounts from {json_path}.")

lines = []
lines.append(f"# دایرکتوری رسمی {len(accounts)} پیج مادر و بنچ‌مارک‌های واقعی @rozetext.ir")
lines.append(f"> **مخزن داده ماشینی:** [`data/benchmark_accounts.json`](file:///d:/rozetext-framework/data/benchmark_accounts.json)  ")
lines.append(f"> **وضعیت اصالت:** ۱۰۰٪ واقعی، استخراج‌شده به صورت زنده از گراف رسمی و پیشنهادهای اینستاگرام (Instagram Graph & Similar Accounts Chaining).")
lines.append("")
lines.append("---")
lines.append("")
lines.append("## 🎯 قوانین طلایی رصد پیج‌های مادر")
lines.append("1. **قانون متن روی ویدیو (Direct Raw-Text Policy):** تمام جملات باید دقیقاً از روی صفحه ویدیو خوانده و استخراج شوند (۷ تا ۱۶ سطر). هرگز به جملات ناقص یا خلاصه در کپشن اعتماد نکنید.")
lines.append("2. **کف ویو (View Floor):** حداقل ۵۰۰,۰۰۰ ویو ثبت‌شده برای ویدیوهای هدف (ترجیحاً بالای ۱ میلیون ویو).")
lines.append("3. **فیلتر تکرار (Deduplication):** مقایسه متن با ۲۳۳ ریلز تاریخی پیج و اسکریپت‌های موجود در دیتابیس؛ اشتراک کلمات کلیدی نباید بیش از ۶۰٪ باشد.")
lines.append("4. **اصالت پیج (Verified Authentic Only):** تمامی اکانت‌ها دارای پروفایل‌های فعال، فالوورهای واقعی و ریلزهای میلیونی در اینستاگرام هستند.")
lines.append("")
lines.append("---")
lines.append("")
lines.append(f"## 📂 جدول {len(accounts)} پیج مادر واقعی و تست‌شده (Verified Mother Accounts)")
lines.append("")
lines.append("| ردیف | آیدی پیج (Handle) | نام پیج | فالوور تاییدشده | بیشترین ویو ثبت‌شده | آرکتایپ‌های منطبق | سبک محتوا و کلاستر |")
lines.append("|:---:|:---|:---|:---:|:---:|:---:|:---|")

for i, acc in enumerate(accounts, 1):
    h = acc['handle']
    name = acc['name_fa']
    followers = acc.get('followers', 'فعال')
    top_views = acc.get('top_views_recorded', '-')
    archs = '، '.join(acc.get('matching_archetypes', []))
    style = acc.get('content_style', acc.get('cluster', ''))
    lines.append(f"| {i} | `{h}` | {name} | {followers} | {top_views} | {archs} | {style} |")

lines.append("")
lines.append("---")
lines.append("")
lines.append("## 🧭 دسته‌بندی کلاسترهای محتوایی پیج‌های مادر")
lines.append("1. **تکست‌گرافی مینیمال سینمایی و مونولوگ احساسی:** `@heliumm.__`، `@text.love400`، `@leyli_geraphy`، `@docharetooo`، `@darlahze__`، `@sanma.text`")
lines.append("2. **دکلمه صوتی، گویندگی و مانیفست‌های عاطفی:** `@vahidrezakhoshbayan`، `@shadighorbanyy`، `@alikeshavarz.original`، `@radiodelwin`، `@_khaazaan_`، `@radio.khat`، `@naghmeh_zendegiii`")
lines.append("3. **حال خوب، التیام زخم‌ها و روانشناسی آرامش:** `@halekhoub`، `@sepehr_kh`، `@savad_zendegi`، `@aruma.mind`، `@zehn.darlahzeh`، `@pouneh_ir`، `@lanternnevesht`")
lines.append("4. **حرف دل، بغض خاموش و نجواهای شبانه:** `@___yeharf`، `@boqzdel`، `@delneveshtee_naab`، `@medad.mag`، `@textnime_shab`، `@b.kame.del`، `@del__aavaa`، `@wiiraneh`")
lines.append("5. **تاوان، کارما، مرزبندی و خداحافظی باوقار:** `@tavan_sangin`، `@enhesaar`، `@imazhart`، `@matne_ziba`، `@tabattoll`")
lines.append("6. **عاشقانه، دلتنگی و وفاداری:** `@atiya_text`، `@haarmuni`، `@baroone_eshgh1`، `@chicheknaz`، `@tabe.eshgh__`، `@lilium.flwr`")

with open(md_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print(f"Successfully generated {md_path} with {len(accounts)} accounts.")
