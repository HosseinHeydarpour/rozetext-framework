# -*- coding: utf-8 -*-
"""
Script to generate a high-end, executive PDF proposal for Shahrchoob Design Story Campaign on RozeText.
"""

import os
import sys
import subprocess
import shutil

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>سناریوهای کمپین تبلیغاتی استوری — شهر چوب دیزاین در رُز تکست</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;600;700;800;900&display=swap');

        @page {
            size: A4 portrait;
            margin: 12mm 13mm 13mm 13mm;
            @bottom-center {
                content: counter(page);
                font-family: 'Vazirmatn', Tahoma, sans-serif;
                font-size: 8.5pt;
                color: #94a3b8;
            }
        }

        * {
            box-sizing: border-box;
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
        }

        body {
            font-family: 'Vazirmatn', 'Segoe UI', Tahoma, Arial, sans-serif;
            direction: rtl;
            text-align: right;
            color: #1e293b;
            background-color: #ffffff;
            margin: 0;
            padding: 0;
            font-size: 9.8pt;
            line-height: 1.6;
        }

        /* Header / Cover Hero */
        .header-card {
            background: linear-gradient(135deg, #1c1917 0%, #292524 50%, #44403c 100%);
            color: #ffffff;
            padding: 22px 24px;
            border-radius: 12px;
            margin-bottom: 16px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            border-right: 5px solid #d97706;
        }

        .badge-tag {
            display: inline-block;
            background: rgba(217, 119, 6, 0.22);
            color: #fbbf24;
            border: 1px solid rgba(251, 191, 36, 0.4);
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 8pt;
            font-weight: 600;
            margin-bottom: 8px;
            letter-spacing: 0.3px;
        }

        .header-title {
            font-size: 17pt;
            font-weight: 800;
            margin: 0 0 4px 0;
            line-height: 1.3;
            color: #ffffff;
        }

        .header-subtitle {
            font-size: 10pt;
            color: #d6d3d1;
            margin: 0 0 14px 0;
            font-weight: 400;
        }

        .meta-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            background: rgba(255, 255, 255, 0.08);
            padding: 10px 14px;
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.12);
        }

        .meta-item {
            font-size: 8.8pt;
        }

        .meta-label {
            color: #a8a29e;
            font-size: 7.8pt;
            display: block;
            margin-bottom: 2px;
        }

        .meta-value {
            font-weight: 700;
            color: #fef3c7;
        }

        /* Section Headings */
        .section-title {
            font-size: 11.5pt;
            font-weight: 800;
            color: #1e293b;
            margin: 16px 0 10px 0;
            display: flex;
            align-items: center;
            border-bottom: 2px solid #f1f5f9;
            padding-bottom: 5px;
        }

        .section-title span.num {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 24px;
            height: 24px;
            background: #d97706;
            color: #ffffff;
            border-radius: 6px;
            font-size: 9pt;
            margin-left: 8px;
            font-weight: 700;
        }

        /* Cards & Info Boxes */
        .info-box {
            background-color: #fafaf9;
            border: 1px solid #e7e5e4;
            border-right: 4px solid #78350f;
            border-radius: 8px;
            padding: 11px 14px;
            margin-bottom: 12px;
            font-size: 9pt;
            line-height: 1.6;
        }

        .info-box-title {
            font-weight: 700;
            color: #78350f;
            margin-bottom: 4px;
            font-size: 9.5pt;
        }

        /* Scenario Container */
        .scenario-card {
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            margin-bottom: 14px;
            overflow: hidden;
            box-shadow: 0 1px 5px rgba(0, 0, 0, 0.02);
            page-break-inside: avoid;
        }

        .scenario-header {
            background: #f8fafc;
            padding: 10px 14px;
            border-bottom: 1px solid #e2e8f0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .scenario-title {
            font-size: 10.5pt;
            font-weight: 800;
            color: #0f172a;
            margin: 0;
        }

        .scenario-tag {
            font-size: 7.8pt;
            padding: 2px 8px;
            border-radius: 5px;
            font-weight: 600;
        }

        .tag-recommended {
            background: #dcfce7;
            color: #15803d;
            border: 1px solid #bbf7d0;
        }

        .tag-secondary {
            background: #fef3c7;
            color: #b45309;
            border: 1px solid #fde68a;
        }

        .scenario-body {
            padding: 12px 14px;
            background: #ffffff;
        }

        .scenario-intro {
            font-size: 8.8pt;
            color: #475569;
            margin-bottom: 10px;
            background: #fffbeb;
            padding: 7px 11px;
            border-radius: 6px;
            border: 1px dashed #fcd34d;
        }

        /* Slide Steps */
        .slides-grid {
            display: flex;
            flex-direction: column;
            gap: 9px;
        }

        .slide-item {
            border: 1px solid #e5e7eb;
            border-radius: 7px;
            padding: 9px 12px;
            background: #ffffff;
        }

        .slide-item.s1 {
            border-right: 4px solid #3b82f6;
            background: #f8faff;
        }
        .slide-item.s2 {
            border-right: 4px solid #d97706;
            background: #fffdfa;
        }
        .slide-item.s3 {
            border-right: 4px solid #10b981;
            background: #f6fdf9;
        }

        .slide-title-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 5px;
        }

        .slide-name {
            font-weight: 800;
            font-size: 9.2pt;
            color: #1e293b;
        }

        .slide-timing {
            font-size: 7.8pt;
            color: #64748b;
            font-weight: 600;
            background: #f1f5f9;
            padding: 2px 7px;
            border-radius: 4px;
        }

        .slide-visual {
            font-size: 8.2pt;
            color: #475569;
            margin-bottom: 6px;
        }

        .content-box {
            background: #18181b;
            color: #f4f4f5;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 9pt;
            line-height: 1.55;
            margin-bottom: 6px;
            white-space: pre-line;
            border: 1px solid #27272a;
        }

        .sticker-box {
            background: #ffffff;
            border: 1px dashed #cbd5e1;
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 8.2pt;
            display: flex;
            align-items: center;
            flex-wrap: wrap;
            gap: 6px;
        }

        .sticker-badge {
            background: #eff6ff;
            color: #1d4ed8;
            font-weight: 700;
            padding: 1px 6px;
            border-radius: 4px;
            font-size: 7.8pt;
        }

        .sticker-option {
            background: #f1f5f9;
            padding: 1px 6px;
            border-radius: 4px;
            color: #334155;
            font-size: 8pt;
        }

        /* Tables */
        table.custom-table {
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0 14px 0;
            font-size: 8.8pt;
            page-break-inside: avoid;
        }

        table.custom-table th, table.custom-table td {
            border: 1px solid #e2e8f0;
            padding: 8px 11px;
            text-align: right;
        }

        table.custom-table th {
            background-color: #f8fafc;
            color: #1e293b;
            font-weight: 700;
        }

        table.custom-table tr:nth-child(even) {
            background-color: #fbfcfe;
        }

        /* Checklist */
        .checklist-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-bottom: 14px;
            page-break-inside: avoid;
        }

        .check-card {
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 10px 12px;
            background: #ffffff;
        }

        .check-card-title {
            font-size: 9pt;
            font-weight: 700;
            color: #0f172a;
            margin-bottom: 4px;
            display: flex;
            align-items: center;
        }

        .check-card-title span {
            margin-left: 5px;
        }

        .check-card p {
            margin: 0;
            font-size: 8.2pt;
            color: #64748b;
            line-height: 1.55;
        }

        .page-break {
            page-break-after: always;
        }

        .footer-note {
            font-size: 8pt;
            color: #94a3b8;
            text-align: center;
            margin-top: 18px;
            border-top: 1px solid #e2e8f0;
            padding-top: 10px;
        }
    </style>
</head>
<body>

    <!-- Cover / Header Section -->
    <div class="header-card">
        <span class="badge-tag">سند استراتژی و پلن اجرایی کمپین اینستاگرام</span>
        <h1 class="header-title">سناریوهای خلاقانه کمپین تبلیغاتی استوری</h1>
        <p class="header-subtitle">طراحی سناریوهای نیتیو و احساسی بر اساس هم‌پوشانی مخاطبان پیج «شهر چوب دیزاین» و «رُز تکست»</p>
        
        <div class="meta-grid">
            <div class="meta-item">
                <span class="meta-label">کسب‌وکار هدف (اسپانسر):</span>
                <span class="meta-value">@shahrchoob.design (شهر چوب)</span>
            </div>
            <div class="meta-item">
                <span class="meta-label">رسانه میزبان (ناشر):</span>
                <span class="meta-value">@rozetext.ir (~۶۰K مخاطب)</span>
            </div>
            <div class="meta-item">
                <span class="meta-label">فرمت و رویکرد کمپین:</span>
                <span class="meta-value">استوری تعاملی چندپرده‌ای (Native Story)</span>
            </div>
        </div>
    </div>

    <!-- Section 1: Strategic Alignment -->
    <div class="section-title">
        <span class="num">۱</span>
        <span>منطق استراتژیک کمپین و نقطه پیوند دو برند (Brand Alignment)</span>
    </div>

    <div class="info-box">
        <div class="info-box-title">چرا مخاطبان پیج «رُز تکست» بالاترین پتانسیل تبدیل به خریدار و فالوور شهر چوب را دارند؟</div>
        بیش از <strong>۷۲٪ از مخاطبان رُز تکست را خانم‌های ۱۸ تا ۳۴ سال</strong> تشکیل می‌دهند که در فاز تشکیل زندگی، طراحی دکوراسیون منزل، کافه‌نشینی و خرید اکسسوری‌های خاص هستند. پرسونای رُز تکست تداعی‌گر <em>«آرامش، خلوت، اصالت و دوری از هیاهو و ظاهرسازی مدرن»</em> است. عنصر <strong>چوب طبیعی و دست‌سازه‌های روستیک شهر چوب</strong> دقیقاً پاسخ فیزیکی و ملموس به همین نیاز عاطفی است.
    </div>

    <table class="custom-table">
        <thead>
            <tr>
                <th style="width: 25%;">شاخص</th>
                <th style="width: 37%;">رویکرد سنتی و شکست‌خورده (بلاگری)</th>
                <th style="width: 38%;">رویکرد اختصاصی این کمپین (نیتیو و داستانی)</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>لحن معرفی</strong></td>
                <td>«سلام بچه‌ها! امروز اومدم یه پیج خفن معرفی کنم...» (Skip Rate بالای ۸۵٪)</td>
                <td>روایت آرامش، بوی چوب و کشف یک هنر دست‌ساز اصیل با لحن آرام و صمیمی</td>
            </tr>
            <tr>
                <td><strong>مکانیزم تعامل</strong></td>
                <td>صرفاً یک بنر خشک یا ری‌استوری ساده ریلز</td>
                <td>استفاده از نظرسنجی ۲ گزینه‌ای چالش‌برانگیز در اسلاید ۱ برای جهش سین استوری</td>
            </tr>
            <tr>
                <td><strong>تصمیم مخاطب</strong></td>
                <td>حس تبلیغات زرد و تمایل به رد کردن سریع</td>
                <td>احساس هم‌سلیقگی، لذت بصری و فالو کردن پیج به عنوان یک منبع الهام و هنر</td>
            </tr>
        </tbody>
    </table>

    <!-- Page Break for clean scenario presentation -->
    <div class="page-break"></div>

    <!-- Section 2: Detailed Scenarios -->
    <div class="section-title">
        <span class="num">۲</span>
        <span>سناریوهای ۳ مرحله‌ای استوری (آماده اجرا و بازتولید)</span>
    </div>

    <!-- Scenario 1 -->
    <div class="scenario-card">
        <div class="scenario-header">
            <h3 class="scenario-title">سناریو ۱ (پیشنهادی و اولویت اصلی): «گوشه دنج و پناهگاه آرامش» (The Cozy Sanctuary)</h3>
            <span class="scenario-tag tag-recommended">🔥 بالاترین نرخ تبدیل و جذب فالوور</span>
        </div>
        <div class="scenario-body">
            <div class="scenario-intro">
                <strong>منطق روانشناسی:</strong> لمس نیاز عاطفی به داشتن یک گوشه دنج، آرام و دلنشین در خانه با فنجان چای و اکسسوری چوبی که مخاطب خسته از روزمرگی را عمیقاً همراه می‌کند.
            </div>

            <div class="slides-grid">
                <!-- Slide 1 -->
                <div class="slide-item s1">
                    <div class="slide-title-bar">
                        <span class="slide-name">اسلاید ۱: استوری شوک تعاملی و پرتاب سین (Igniter)</span>
                        <span class="slide-timing">ساعت ۲۱:۱۵ شب (اوج آنلاین‌ها)</span>
                    </div>
                    <div class="slide-visual"><strong>بصری:</strong> عکس بسیار باکیفیت و دارک از ماگ گرم چای روی بافت چوب طبیعی با نور ملایم شمع.</div>
                    <div class="content-box">آدم گاهی از کل دنیا و شلوغیاش خسته میشه،
دلش فقط یه گوشه‌ی دنج تو خونه می‌خواد؛
با بوی چوب، نور شمع و یه لیوان چایی... ☕🪵
قبول داری چوب طبیعی به خونه "روح و گرما" میده؟ 👇</div>
                    <div class="sticker-box">
                        <span class="sticker-badge">استیکر Poll دوگزینه‌ای:</span>
                        <span class="sticker-option">گزینه ۱: دقیقاً، حس زندگی میده 🤎</span>
                        <span class="sticker-option">گزینه ۲: وسایل مدرن و سرد 🥀</span>
                    </div>
                </div>

                <!-- Slide 2 -->
                <div class="slide-item s2">
                    <div class="slide-title-bar">
                        <span class="slide-name">اسلاید ۲: روایت عاطفی و اتصال به کارگاه شهر چوب</span>
                        <span class="slide-timing">ساعت ۲۱:۴۵ شب</span>
                    </div>
                    <div class="slide-visual"><strong>بصری:</strong> کلیپ کوتاه (۴ ثانیه) از تراشیدن چوب، لمس رگه‌های طبیعی یا ویدیوی زیبای کارگاه شهر چوب.</div>
                    <div class="content-box">امروز داشتم این پیج رو نگاه می‌کردم؛
چقدر حس و حال کارگاهشون و عشقشون به چوب قشنگ بود...
از اون آدمایی که از صفر شروع کردن
و با دستاشون به یه تیکه چوب خشکِ طبیعت، روح و قشنگی می‌بخشند 🥹🪵</div>
                    <div class="sticker-box">
                        <span class="sticker-badge">هدف الگوریتمی:</span>
                        <span class="sticker-option">مکث کامل مخاطب (Hold) و ایجاد کشش احساسی بدون آگهی مستقیم</span>
                    </div>
                </div>

                <!-- Slide 3 -->
                <div class="slide-item s3">
                    <div class="slide-title-bar">
                        <span class="slide-name">اسلاید ۳: دعوت به اقدام نرم و هدایت به فالو (Call To Action)</span>
                        <span class="slide-timing">بلافاصله بعد از اسلاید ۲</span>
                    </div>
                    <div class="slide-visual"><strong>بصری:</strong> تصویر تمیز از چند محصول دست‌ساز (اردوخوری شیک، تخته سرو یا میز روستیک).</div>
                    <div class="content-box">اگه شما هم مثل من عاشق بوی چوب، دکورهای روستیک
و گوشه‌های دنجِ آرامش‌بخشید،
دیدن کارای دست‌سازشون واقعاً حالِ دل رو خوب می‌کنه.
پیجشون رو داشته باشید، هم کاراشون چشم‌نوازه
هم دیدن مسیر رشدشون قشنگه 🤎👇</div>
                    <div class="sticker-box">
                        <span class="sticker-badge">استیکر Mention & Tag:</span>
                        <span class="sticker-option">@shahrchoob.design (با کنتراست بالا و سایز خوانا)</span>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Scenario 2 -->
    <div class="scenario-card">
        <div class="scenario-header">
            <h3 class="scenario-title">سناریو ۲: «داستان اصالت و شروع از صفر» (The Authentic Craftsmanship)</h3>
            <span class="scenario-tag tag-secondary">حمایت از کارآفرینی و هنر دست</span>
        </div>
        <div class="scenario-body">
            <div class="scenario-intro">
                <strong>منطق روانشناسی:</strong> تکیه بر پیام ریلز اول شهرچوب («ما از صفر شروع کردیم...»). مخاطبان فرهیخته عاشق دیدن پشت‌صحنه، تلاش صادقانه و حمایت از هنر دست در مقابل تولیدات انبوه ماشینی هستند.
            </div>

            <div class="slides-grid">
                <!-- Slide 1 -->
                <div class="slide-item s1">
                    <div class="slide-title-bar">
                        <span class="slide-name">اسلاید ۱: نظرسنجی ارزشی و تامل‌برانگیز</span>
                        <span class="slide-timing">ساعت ۲۱:۱۵ شب</span>
                    </div>
                    <div class="content-box">هنوزم معتقدم قشنگ‌ترین چیزایی که ساخته میشن،
حاصل دست‌های زحمت‌کشی هستن
که از صفر و فقط با "عشق" شروع کردن... 🤎
توی دکور خونه، کدومش برات باارزش‌تره؟ 👇</div>
                    <div class="sticker-box">
                        <span class="sticker-badge">استیکر Poll دوگزینه‌ای:</span>
                        <span class="sticker-option">گزینه ۱: دست‌ساز با اصالت و روح‌دار 🪵</span>
                        <span class="sticker-option">گزینه ۲: کارهای آماده و صنعتی بازار ⚙️</span>
                    </div>
                </div>

                <!-- Slide 2 & 3 Combined Presentation -->
                <div class="slide-item s2">
                    <div class="slide-title-bar">
                        <span class="slide-name">اسلاید ۲: معرفی کارگاه بهشهر و تعهد به کیفیت</span>
                        <span class="slide-timing">ساعت ۲۱:۴۵ شب</span>
                    </div>
                    <div class="content-box">بچه‌های «شهر چوب» یه تیم جوون و مستقل تو مازندران هستن
که با هنر نجاری، از اکسسوری و ظروف چوبی تا کابینت و کلبه می‌سازن.
ریلز اول پیجشون رو دیدم که از صفر شروع کردن؛
چقدر این صداقت و انگیزه برای ساختن تحسین‌برانگیزه 🤍🌱</div>
                </div>

                <div class="slide-item s3">
                    <div class="slide-title-bar">
                        <span class="slide-name">اسلاید ۳: دعوت به همراهی و فالو</span>
                        <span class="slide-timing">ساعت ۲۱:۵۰ شب</span>
                    </div>
                    <div class="content-box">حیفم اومد این هنر تمیز و دست‌ساز رو بهتون معرفی نکنم.
برید کاراشون رو ببینید و یه گوشه از این مسیر کنارشون باشید 🪵👇
پیجشون رو حتماً فالو داشته باشید:</div>
                    <div class="sticker-box">
                        <span class="sticker-badge">استیکر تگ:</span>
                        <span class="sticker-option">@shahrchoob.design</span>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Scenario 3 -->
    <div class="scenario-card">
        <div class="scenario-header">
            <h3 class="scenario-title">سناریو ۳: «تست استایل دکوراسیون و پیشنهاد هدیه» (Aesthetic & Gift Inspiration)</h3>
            <span class="scenario-tag tag-secondary">تمرکز بر خرید اکسسوری، هدیه و ظروف پذیرایی</span>
        </div>
        <div class="scenario-body">
            <div class="scenario-intro">
                <strong>منطق روانشناسی:</strong> تحریک سلیقه بصری خانم‌ها برای پذیرایی مهمانی و خرید هدیه‌های لوکس، خاص و اقتصادی (مانند اردوخوری و تخته سرو چوبی).
            </div>

            <div class="slides-grid">
                <!-- Slide 1 -->
                <div class="slide-item s1">
                    <div class="slide-title-bar">
                        <span class="slide-name">اسلاید ۱: تست سبک پذیرایی و میزبانی</span>
                        <span class="slide-timing">ساعت ۲۱:۱۵ شب</span>
                    </div>
                    <div class="slide-visual"><strong>بصری:</strong> عکس چشم‌نواز از چیدمان میز عصرانه با ظروف سرو چوبی و میوه/آجیل.</div>
                    <div class="content-box">به نظرتون میزبانی و پذیرایی با ظروف چوب طبیعی قشنگ‌تره
یا بلور و کریستال‌های قدیمی؟ ✨👇</div>
                    <div class="sticker-box">
                        <span class="sticker-badge">استیکر تعاملی:</span>
                        <span class="sticker-option">Poll: چوب طبیعی و روستیک 🤎 | بلور و شیشه 🥂</span>
                    </div>
                </div>

                <!-- Slide 2 & 3 -->
                <div class="slide-item s3">
                    <div class="slide-title-bar">
                        <span class="slide-name">اسلاید ۲ و ۳: پاسخ به نیاز و معرفی محصولات پرفروش</span>
                        <span class="slide-timing">ساعت ۲۱:۴۵ شب</span>
                    </div>
                    <div class="content-box">خیلی‌ها می‌پرسید این اکسسوری‌ها و تخته سروهای چوبی خاص رو از کجا میشه تهیه کرد که کیفیت چوبش عالی باشه و پوسته‌پوسته نشه...
این کارگاه مستقیماً همه چیز رو با چوب طبیعی کار می‌کنه و ارسال به کل کشور هم دارن.
اگه دنبال یه هدیه موندگار یا ظروف خاص برای پذیرایی هستید، مدل‌هاشون رو اینجا ببینید 🪵👇</div>
                    <div class="sticker-box">
                        <span class="sticker-badge">استیکر منشن:</span>
                        <span class="sticker-option">@shahrchoob.design | با تگ روی تصویر محصولات</span>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Page Break before Checklist & Launch Timing -->
    <div class="page-break"></div>

    <!-- Section 3: Client Pre-Campaign Checklist -->
    <div class="section-title">
        <span class="num">۳</span>
        <span>چک‌لیست الزامی پیج «شهر چوب» قبل از انتشار کمپین (Conversion Checklist)</span>
    </div>

    <div class="checklist-grid">
        <div class="check-card">
            <div class="check-card-title">
                <span>📁</span>
                <span>۱. طراحی ۳ هایلایت حیاتی در پروفایل</span>
            </div>
            <p>قبل از انتشار استوری، حتماً هایلایت‌های <strong>«محصولات و قیمت»</strong> (عکس چند مدل اردوخوری و تخته سرو با قیمت حدودی)، <strong>«کارگاه و اصالت»</strong> (پشت‌صحنه کارگاه بهشهر) و <strong>«رضایت و ارسال»</strong> چیده شود تا کاربر ورودی بلافاصله اعتماد کند.</p>
        </div>

        <div class="check-card">
            <div class="check-card-title">
                <span>🔥</span>
                <span>۲. فعال بودن استوری‌های روز کمپین</span>
            </div>
            <p>در روزی که استوری تبلیغاتی منتشر می‌شود، پیج شهر چوب نباید سوت‌وکور باشد. انتشار ۲ تا ۳ استوری جذاب از ساخت یک محصول، بسته‌بندی یا محیط کارگاه باعث می‌شود کاربر ورودی دایره استوری را باز کند و بلافاصله فالو نماید.</p>
        </div>

        <div class="check-card">
            <div class="check-card-title">
                <span>🔗</span>
                <span>۳. ساماندهی بیوگرافی و راه ارتباطی</span>
            </div>
            <p>به جای یک شماره تماس ساده در بیو، از زیلینک یا لینک واتساپ با متن آماده <em>(«سلام، برای مشاهده کاتالوگ و ثبت سفارش پیام دادم»)</em> استفاده شود تا فاصله تصمیم تا خرید مشتری به حداقل برسد.</p>
        </div>

        <div class="check-card">
            <div class="check-card-title">
                <span>💬</span>
                <span>۴. آمادگی دایرکت برای پاسخگویی سریع</span>
            </div>
            <p>سرعت پاسخگویی به پیام‌های دایرکت در ۴ ساعت اول کمپین تعیین‌کننده است. داشتن پاسخ‌های آماده و صمیمانه برای قیمت، زمان ارسال و ابعاد محصولات ضروری است.</p>
        </div>
    </div>

    <!-- Section 4: Launch Timing & Technical Rules -->
    <div class="section-title">
        <span class="num">۴</span>
        <span>زمان‌بندی و پروتکل فنی انتشار در پیج رُز تکست</span>
    </div>

    <table class="custom-table">
        <tbody>
            <tr>
                <td style="width: 25%;"><strong>روزهای طلایی اجرا</strong></td>
                <td>چهارشنبه، پنج‌شنبه یا جمعه (روزهای پیک آنلاین و بالاترین نرخ بازدید هفتگی پیج)</td>
            </tr>
            <tr>
                <td><strong>ساعت انتشار استوری ۱</strong></td>
                <td>ساعت <strong>۲۱:۱۵ شب</strong> (لحظه حضور همزمان بیش از ۱۵,۰۰۰ فالوور آنلاین در پیج)</td>
            </tr>
            <tr>
                <td><strong>تکنیک افزایش سین (Reach Hack)</strong></td>
                <td>خالی نگه داشتن استوری‌ها به مدت حداقل ۴ ساعت قبل از شروع کمپین (Reset Story Tray) برای فعال‌سازی اعلان و اولویت‌بندی در نوار استوری مخاطبان</td>
            </tr>
            <tr>
                <td><strong>پروتکل منشن</strong></td>
                <td>تگ خوانا و واضح آیدی <code>@shahrchoob.design</code> در اسلاید نهایی با ابعاد استاندارد لمس انگشت (Tap Friendly)</td>
            </tr>
        </tbody>
    </table>

    <div class="footer-note">
        این سند بر اساس تحلیل دقیق پرسونای هر دو پیج توسط اتاق فکر محتوایی رُز تکست تدوین شده و تضمین‌کننده حفظ هویت برند و جذب مخاطب وفادار است.
    </div>

</body>
</html>
"""

def generate_pdf():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    html_file = os.path.join(base_dir, "shahrchoob_campaign_proposal.html")
    pdf_file = os.path.join(base_dir, "سناریوهای_تبلیغاتی_شهرچوب_در_رزتکست.pdf")
    pdf_file_en = os.path.join(base_dir, "Shahrchoob_Story_Campaign_Proposal.pdf")

    # 1. Write HTML
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(HTML_TEMPLATE)
    print(f"HTML written to: {html_file}")

    # 2. Locate Browser
    chrome_candidates = [
        shutil.which("chrome"),
        shutil.which("msedge"),
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
    ]
    browser = None
    for p in chrome_candidates:
        if p and os.path.exists(p):
            browser = p
            break

    if not browser:
        raise RuntimeError("Neither Chrome nor Edge was found on system.")

    print(f"Using browser: {browser}")

    # 3. Print to PDF using Headless Chrome
    cmd = [
        browser,
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_file}",
        html_file
    ]

    print(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(f"Subprocess return code: {result.returncode}")

    if os.path.exists(pdf_file) and os.path.getsize(pdf_file) > 0:
        file_size_kb = os.path.getsize(pdf_file) / 1024
        print(f"SUCCESS: Generated PDF at {pdf_file} ({file_size_kb:.1f} KB)")
        # Also copy to English filename for easy cross-platform compatibility
        import shutil
        shutil.copyfile(pdf_file, pdf_file_en)
        print(f"SUCCESS: Copied also to {pdf_file_en}")
        return pdf_file, pdf_file_en
    else:
        print(f"STDERR: {result.stderr}")
        print(f"STDOUT: {result.stdout}")
        raise RuntimeError("PDF generation failed or output file is 0 bytes.")

if __name__ == "__main__":
    generate_pdf()
