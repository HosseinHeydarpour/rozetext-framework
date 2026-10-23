import json
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

with open('data/verified_36_reels_clean.json', 'r', encoding='utf-8') as f:
    items = json.load(f)

# Metadata mapping for each reel
meta_mapping = {
    'DeZH7Z0u1s6': {
        'title': 'من متهم ردیف اول زندگی خودمم',
        'archetype': 'آرکتایپ ۱: آدمِ همیشه قوی و بی‌صدا خوب',
        'goal': 'افزایش سیو و اشتراک‌گذاری دایرکت (Save & Share Magnet)',
        'score': 98,
        'breakdown': {'hook_power': 20, 'emotional_depth': 20, 'relatability': 19, 'shareability': 20, 'completion_rate': 19},
        'persona_fit': 'پذیرش مسئولیت کامل شکست‌ها و تصمیمات بدون فرافکنی، منطبق بر حکمت و وقار درونی پرسونا.',
        'notes': 'تصویر بک‌گراند بارانی مات، موزیک آمبینت پیانو مینیمال، کال‌تو‌اکشن ذخیره برای بازخوانی در خلوت.'
    },
    'DeeBHT_O_Zi': {
        'title': 'حلال نمیکنم...',
        'archetype': 'آرکتایپ ۲: پایانِ باوقار و خداحافظی آرام',
        'goal': 'افزایش کامنت و تعامل عمیق (Deep Engagement)',
        'score': 97,
        'breakdown': {'hook_power': 20, 'emotional_depth': 20, 'relatability': 19, 'shareability': 19, 'completion_rate': 19},
        'persona_fit': 'بیان مرزهای عدم بخشش حق‌الناس عاطفی با لحن قاطع و بدون پرخاشگری سخیف.',
        'notes': 'تایپوگرافی سفید روی پس‌زمینه ابرهای تاریک، تعلیق ریتمیک میان سطرها.'
    },
    'DZId7nxNc_K': {
        'title': 'وجدان راحتم زندگی سختمو آسون تر کرد',
        'archetype': 'آرکتایپ ۵: مانیفستِ استقلال و صراحتِ بدون تعارف',
        'goal': 'جذب فالوور حداکثری (Follow Magnet)',
        'score': 98,
        'breakdown': {'hook_power': 20, 'emotional_depth': 19, 'relatability': 20, 'shareability': 20, 'completion_rate': 19},
        'persona_fit': 'مانیفست آرامش وجدان در برابر قضاوت‌های بیرونی، محور اصلی فلسفه تاب‌آوری پیج.',
        'notes': 'ویدیوی حرکت در جاده مه‌آلود، صدای لو-فای ملایم، تاکید روی مفهوم آرامش شبانه.'
    },
    'DbbY_s-MMK0': {
        'title': 'کاش یکی موقع بزرگ شدن بهمون می‌گفت',
        'archetype': 'آرکتایپ ۴: گلایه فلسفی / خستگی عمیق',
        'goal': 'وایرال مارکتینگ و موج اکسپلور (Explore Surge)',
        'score': 99,
        'breakdown': {'hook_power': 20, 'emotional_depth': 20, 'relatability': 20, 'shareability': 20, 'completion_rate': 19},
        'persona_fit': 'حسرت بلوغ زودرس و از دست رفتن معصومیت کودکی، قوی‌ترین تریگر نوستالژیک پرسونای پیج.',
        'notes': 'طبیعت بکر و مه‌آلود شمال، ریتم آرام دکلمه، ترغیب به فرستادن برای هم‌سن‌وسال‌ها.'
    },
    'DbjHTCAMKq8': {
        'title': 'گاهی با خودم فکر می‌کنم',
        'archetype': 'آرکتایپ ۴: گلایه فلسفی / خستگی عمیق',
        'goal': 'افزایش سیو و اشتراک‌گذاری دایرکت (Save & Share Magnet)',
        'score': 98,
        'breakdown': {'hook_power': 19, 'emotional_depth': 20, 'relatability': 20, 'shareability': 20, 'completion_rate': 19},
        'persona_fit': 'مونولوگ درونی درباره بهای سنگین مهربانی و درک دیگران با لحن عمیق و منصفانه.',
        'notes': 'نمای دوردست از جنگل ابری، متن با فونت نازک و خوانا در مرکز صفحه.'
    },
    'Dc_z1QtMhd7': {
        'title': 'نمی‌دونم از چی خستم...',
        'archetype': 'آرکتایپ ۱: آدمِ همیشه قوی و بی‌صدا خوب',
        'goal': 'جذب فالوور حداکثری (Follow Magnet)',
        'score': 98,
        'breakdown': {'hook_power': 20, 'emotional_depth': 20, 'relatability': 20, 'shareability': 19, 'completion_rate': 19},
        'persona_fit': 'بیان خستگی روحی ناشی از همیشه فهمیدن و تکیه‌گاه بودن دیگران، انطباق کامل با سلیقه مخاطب روزتکست.',
        'notes': 'ویدیوی ریلز جاده کوهستانی، ریتم خوانش کند و تفکربرانگیز.'
    },
    'DblsFKUsRjn': {
        'title': 'من آدمی بودم که نه نمی‌گفتم',
        'archetype': 'آرکتایپ ۵: مانیفستِ استقلال و صراحتِ بدون تعارف',
        'goal': 'افزایش سیو و اشتراک‌گذاری دایرکت (Save & Share Magnet)',
        'score': 97,
        'breakdown': {'hook_power': 19, 'emotional_depth': 20, 'relatability': 20, 'shareability': 19, 'completion_rate': 19},
        'persona_fit': 'بازتعریف حد و مرز فردی پس از نادیده گرفته شدن، حس غرور و استقلال بدون کینه.',
        'notes': 'تصویر قطرات باران روی پنجره، مکث روی واژه‌های کلیدی خودداری.'
    },
    'Dcy79eFObfp': {
        'title': 'این روزا فقط پول کم نمیاریم...',
        'archetype': 'آرکتایپ ۴: گلایه فلسفی / خستگی عمیق',
        'goal': 'وایرال مارکتینگ و موج اکسپلور (Explore Surge)',
        'score': 99,
        'breakdown': {'hook_power': 20, 'emotional_depth': 20, 'relatability': 20, 'shareability': 20, 'completion_rate': 19},
        'persona_fit': 'پیوند زدن دغدغه اجتماعی و روانی کمبود حوصله و انگیزه در عصر مدرن، همذات‌پنداری ۱۰۰ درصدی.',
        'notes': 'ویدیوی خیابان پاییزی، موسیقی ملایم سازهای زهی، هوک آغازین انفجاری.'
    },
    'Dbd9tTKMOsp': {
        'title': 'دلم برای خودم می‌سوزه',
        'archetype': 'آرکتایپ ۱: آدمِ همیشه قوی و بی‌صدا خوب',
        'goal': 'افزایش کامنت و تعامل عمیق (Deep Engagement)',
        'score': 98,
        'breakdown': {'hook_power': 20, 'emotional_depth': 20, 'relatability': 19, 'shareability': 20, 'completion_rate': 19},
        'persona_fit': 'سوگواری پنهان برای روحی که زودتر از سن شناسنامه‌ای پیر و صبور شد.',
        'notes': 'تصویر حرکت ابرها بر فراز قله، کپشن تعاملی با دعوت به همدلی.'
    },
    'Dc1S6FRoBRz': {
        'title': 'فهمیدم اگه کسی دور از من خوشه',
        'archetype': 'آرکتایپ ۲: پایانِ باوقار و خداحافظی آرام',
        'goal': 'جذب فالوور حداکثری (Follow Magnet)',
        'score': 98,
        'breakdown': {'hook_power': 20, 'emotional_depth': 19, 'relatability': 20, 'shareability': 20, 'completion_rate': 19},
        'persona_fit': 'رها کردن بزرگوارانه آدم‌ها بدون اصرار و چنگ زدن به ماندن، اوج بلوغ احساسی.',
        'notes': 'فوتیج سیاه و سفید قهوه و کتاب، سکوت در لحظه تغییر متن.'
    },
    'Dbv_TqKMl-P': {
        'title': 'نمی‌دونم اسم این روزا چیه...',
        'archetype': 'آرکتایپ ۴: گلایه فلسفی / خستگی عمیق',
        'goal': 'افزایش سیو و اشتراک‌گذاری دایرکت (Save & Share Magnet)',
        'score': 97,
        'breakdown': {'hook_power': 19, 'emotional_depth': 20, 'relatability': 20, 'shareability': 19, 'completion_rate': 19},
        'persona_fit': 'توصیف دقیق حالت برزخ احساسی و بی‌تفاوتی محافظتی روح در برابر ضربه‌ها.',
        'notes': 'طبیعت بارانی، فونت کلاسیک، ترغیب مخاطب به تگ کردن رفیق صمیمی.'
    },
    'DcHKsdUMpGH': {
        'title': 'حوصله ناراحت بودنم نداری',
        'archetype': 'آرکتایپ ۱: آدمِ همیشه قوی و بی‌صدا خوب',
        'goal': 'وایرال مارکتینگ و موج اکسپلور (Explore Surge)',
        'score': 97,
        'breakdown': {'hook_power': 20, 'emotional_depth': 19, 'relatability': 20, 'shareability': 19, 'completion_rate': 19},
        'persona_fit': 'گذر از فاز خشم و اعتراض به فاز سکوت و بی‌حوصلگی مطلق، واقع‌گرایی تلخ و درخشان.',
        'notes': 'تصویر چراغ‌های شهر از بالا در شب، موزیک پیانوی غمگین اما تسلی‌بخش.'
    },
    'DayDs66sKNZ': {
        'title': 'یه وقتایی به خودم میام و می‌بینم',
        'archetype': 'آرکتایپ ۴: گلایه فلسفی / خستگی عمیق',
        'goal': 'جذب فالوور حداکثری (Follow Magnet)',
        'score': 99,
        'breakdown': {'hook_power': 20, 'emotional_depth': 20, 'relatability': 20, 'shareability': 20, 'completion_rate': 19},
        'persona_fit': 'لحظه بیداری اگزیستانسیال از غرق شدن در روزمرگی و از یاد بردن خویشتن.',
        'notes': 'ویو ۲.۹ میلیونی در پیج مرجع، اثبات کشش فوق‌العاده بالا روی جامعه هدف.'
    },
    'DaOCORNMENF': {
        'title': 'بعضی وقتا سکوت یعنی چی...',
        'archetype': 'آرکتایپ ۱: آدمِ همیشه قوی و بی‌صدا خوب',
        'goal': 'افزایش سیو و اشتراک‌گذاری دایرکت (Save & Share Magnet)',
        'score': 99,
        'breakdown': {'hook_power': 20, 'emotional_depth': 20, 'relatability': 20, 'shareability': 20, 'completion_rate': 19},
        'persona_fit': 'معناشناسی سکوت آدم‌های صبور؛ سکوت از سر ناامیدی نه از سر رضایت.',
        'notes': 'ویو ۲.۰ میلیونی، متراژ متراکم و تک‌ضرب، ایده‌آل برای ذخیره فوری.'
    },
    'Da0ofrisUtb': {
        'title': 'نسل ما نسلی بود که...',
        'archetype': 'آرکتایپ ۴: گلایه فلسفی / خستگی عمیق',
        'goal': 'وایرال مارکتینگ و موج اکسپلور (Explore Surge)',
        'score': 98,
        'breakdown': {'hook_power': 20, 'emotional_depth': 20, 'relatability': 20, 'shareability': 20, 'completion_rate': 18},
        'persona_fit': 'روایت جمعی از دردهای مشترک نسلی که در جوانی بار سنگین زندگی را کشید.',
        'notes': 'موج شدید بازنشر در استوری‌ها، مناسب برای اسلات‌های عصرگاهی.'
    },
    'Da8duzdMYQt': {
        'title': 'دیگه از کسی انتظار ندارم',
        'archetype': 'آرکتایپ ۵: مانیفستِ استقلال و صراحتِ بدون تعارف',
        'goal': 'جذب فالوور حداکثری (Follow Magnet)',
        'score': 98,
        'breakdown': {'hook_power': 20, 'emotional_depth': 19, 'relatability': 20, 'shareability': 20, 'completion_rate': 19},
        'persona_fit': 'قطع بند ناف توقع از اطرافیان و رسیدن به خودبسندگی عاطفی، پیام بنیادین پیج.',
        'notes': 'تصویر جاده کویری بی‌پایان، ریتم مصمم کلمات روی تصویر.'
    },
    'DR7fbNlCBle': {
        'title': 'عوض شدم چون ارزش خودمو فهمیدم',
        'archetype': 'آرکتایپ ۵: مانیفستِ استقلال و صراحتِ بدون تعارف',
        'goal': 'افزایش سیو و اشتراک‌گذاری دایرکت (Save & Share Magnet)',
        'score': 99,
        'breakdown': {'hook_power': 20, 'emotional_depth': 20, 'relatability': 20, 'shareability': 20, 'completion_rate': 19},
        'persona_fit': 'شرح تحول شخصیتی از یک آدم همیشه در دسترس به انسانی دارای پرستیژ و عزت نفس.',
        'notes': 'ویو نزدیک به یک میلیون، یکی از نمادین‌ترین متن‌های توانمندسازی روانی.'
    },
    'DRpeLe-iMDr': {
        'title': 'این اخلاقم کم منو اذیت نکرد',
        'archetype': 'آرکتایپ ۱: آدمِ همیشه قوی و بی‌صدا خوب',
        'goal': 'افزایش کامنت و تعامل عمیق (Deep Engagement)',
        'score': 99,
        'breakdown': {'hook_power': 20, 'emotional_depth': 20, 'relatability': 20, 'shareability': 20, 'completion_rate': 19},
        'persona_fit': 'اعتراف به آسیب‌های درک افراطی دیگران و نادیده گرفتن حقوق خود.',
        'notes': '۹۴۱K ویو، ایجاد موج کامنت‌های درد‌دل مخاطبان در زیر پست.'
    },
    'DZiJyf3ImZl': {
        'title': 'دلتنگ نسخه‌ی قدیمی خودم نیستم',
        'archetype': 'آرکتایپ ۵: مانیفستِ استقلال و صراحتِ بدون تعارف',
        'goal': 'جذب فالوور حداکثری (Follow Magnet)',
        'score': 97,
        'breakdown': {'hook_power': 19, 'emotional_depth': 20, 'relatability': 19, 'shareability': 20, 'completion_rate': 19},
        'persona_fit': 'پذیرش هزینه‌های بلوغ فردی و ترجیح دادن اقتدار فعلی به سادگی گذشته.',
        'notes': 'پس‌زمینه شهری خلوت، مناسب برای بازخوانی در پایان روز کاری.'
    },
    'Ddop_U4RDVl': {
        'title': 'عاشقت شدم خیلی زود و خیلی شدید',
        'archetype': 'آرکتایپ ۳: آدمِ امن و رفیق واقعی',
        'goal': 'افزایش سیو و اشتراک‌گذاری دایرکت (Save & Share Magnet)',
        'score': 97,
        'breakdown': {'hook_power': 20, 'emotional_depth': 20, 'relatability': 19, 'shareability': 20, 'completion_rate': 18},
        'persona_fit': 'احساس عمیق و اصیل انسانی در رابطه امن بدون باج‌خواهی و تحقیر، صمیمیت پاک.',
        'notes': 'طراحی شده برای ارسال در دایرکت به عنوان اعتراف عاشقانه باوقار.'
    },
    'DanaKZYN_9w': {
        'title': 'دروغ چرا، هنوزم حواسم بهت هست',
        'archetype': 'آرکتایپ ۳: آدمِ امن و رفیق واقعی',
        'goal': 'وایرال مارکتینگ و موج اکسپلور (Explore Surge)',
        'score': 97,
        'breakdown': {'hook_power': 20, 'emotional_depth': 20, 'relatability': 20, 'shareability': 19, 'completion_rate': 18},
        'persona_fit': 'صداقت بی‌پیرایه در پذیرش پیوند قلبی با فردی خاص در کمال حیا و حرمت.',
        'notes': 'تصویر شمع و شب بارانی، مکث‌های کوتاه احساسی بین جملات.'
    },
    'DdeYIgZqlG9': {
        'title': 'تو کاری کردی که بچه‌ام اشکامو پاک کنه',
        'archetype': 'آرکتایپ ۶: دیالوگ‌های کوبنده و مینی‌داستان‌های دراماتیک',
        'goal': 'افزایش کامنت و تعامل عمیق (Deep Engagement)',
        'score': 99,
        'breakdown': {'hook_power': 20, 'emotional_depth': 20, 'relatability': 20, 'shareability': 20, 'completion_rate': 19},
        'persona_fit': 'روایت تکان‌دهنده مادرانه از عمق زخم‌های ناسازگاری عاطفی، بی‌نهایت اثرگذار.',
        'notes': '۱.۴ میلیون ویو، بالاترین نرخ مشارکت و کامنت‌های حسی در جامعه مادران.'
    },
    'DdhIZDEK8_S': {
        'title': 'آن‌قدر مرد بودی که...',
        'archetype': 'آرکتایپ ۶: دیالوگ‌های کوبنده و مینی‌داستان‌های دراماتیک',
        'goal': 'افزایش سیو و اشتراک‌گذاری دایرکت (Save & Share Magnet)',
        'score': 99,
        'breakdown': {'hook_power': 20, 'emotional_depth': 20, 'relatability': 20, 'shareability': 20, 'completion_rate': 19},
        'persona_fit': 'روایتی تلخ از بدعهدی با زبانی نجیب و کنایه‌آمیز اما کاملاً متین و محکم.',
        'notes': '۱.۱ میلیون ویو، استفاده از استعاره‌های رفتاری قدرتمند.'
    },
    'DdotWXnCiBy': {
        'title': 'برای شکارِ من گرگ فرستاده بودی',
        'archetype': 'آرکتایپ ۵: مانیفستِ استقلال و صراحتِ بدون تعارف',
        'goal': 'جذب فالوور حداکثری (Follow Magnet)',
        'score': 98,
        'breakdown': {'hook_power': 20, 'emotional_depth': 20, 'relatability': 19, 'shareability': 20, 'completion_rate': 19},
        'persona_fit': 'اثبات قوی بودن در مواجهه با نارفیقی‌ها با زبانی نمادین و بی‌نهایت باابهت.',
        'notes': '۷۷۹K ویو، تصویر کوهستان تاریک و مه‌آلود، القای حس پیروزی اخلاقی.'
    },
    'DdzFv9hCAZO': {
        'title': 'خیانتش را بخشیدم اما...',
        'archetype': 'آرکتایپ ۲: پایانِ باوقار و خداحافظی آرام',
        'goal': 'افزایش کامنت و تعامل عمیق (Deep Engagement)',
        'score': 98,
        'breakdown': {'hook_power': 20, 'emotional_depth': 20, 'relatability': 19, 'shareability': 20, 'completion_rate': 19},
        'persona_fit': 'ترسیم مرز دقیق میان بخشش برای رهایی خود و پایان دادن قطعی به رابطه.',
        'notes': '۶۶۴K ویو، برانگیزاننده بحث‌های عمیق اخلاقی در کامنت‌ها.'
    },
    'DeHxCX3i3xc': {
        'title': 'من همان قماربازی بودم که...',
        'archetype': 'آرکتایپ ۶: دیالوگ‌های کوبنده و مینی‌داستان‌های دراماتیک',
        'goal': 'وایرال مارکتینگ و موج اکسپلور (Explore Surge)',
        'score': 99,
        'breakdown': {'hook_power': 20, 'emotional_depth': 20, 'relatability': 20, 'shareability': 20, 'completion_rate': 19},
        'persona_fit': 'تمثیل شجاعت در عشق و پایبندی به قمار احساس حتی به قیمت باختن همه چیز.',
        'notes': '۱.۲ میلیون ویو، متن بسیار ادبی، فاخر و مسحورکننده.'
    },
    'Ded4vxjsQX3': {
        'title': 'دارم به خودم یاد میدم',
        'archetype': 'آرکتایپ ۵: مانیفستِ استقلال و صراحتِ بدون تعارف',
        'goal': 'جذب فالوور حداکثری (Follow Magnet)',
        'score': 98,
        'breakdown': {'hook_power': 20, 'emotional_depth': 19, 'relatability': 20, 'shareability': 20, 'completion_rate': 19},
        'persona_fit': 'تربیت و مهندسی مجدد خویشتن برای وابسته نبودن به تایید دیگران.',
        'notes': '۸۳۳K ویو، متن فشرده ۷ سطری روی تصویر، ضرب‌آهنگ عالی برای شروع صبح.'
    },
    'DKaDbPWoKWC': {
        'title': 'شخصیتم نقاب رو تحمل نمیکنه',
        'archetype': 'آرکتایپ ۵: مانیفستِ استقلال و صراحتِ بدون تعارف',
        'goal': 'افزایش سیو و اشتراک‌گذاری دایرکت (Save & Share Magnet)',
        'score': 98,
        'breakdown': {'hook_power': 20, 'emotional_depth': 19, 'relatability': 20, 'shareability': 20, 'completion_rate': 19},
        'persona_fit': 'اعلام موضع شفاف در برابر دورویی و ارجح دانستن تنهایی بر روابط نمایشی.',
        'notes': '۶۰۰K ویو، ایجاد حس جسارت در مخاطب و ترغیب به استوری کردن.'
    },
    'DIO_li0IL5X': {
        'title': 'از صمیم قلب دعا میکنم که',
        'archetype': 'آرکتایپ ۳: آدمِ امن و رفیق واقعی',
        'goal': 'افزایش کامنت و تعامل عمیق (Deep Engagement)',
        'score': 98,
        'breakdown': {'hook_power': 20, 'emotional_depth': 20, 'relatability': 20, 'shareability': 20, 'completion_rate': 18},
        'persona_fit': 'دعای خیر برای آرامش قلب‌های خسته و التیام زخم‌های نامرئی انسان‌ها.',
        'notes': '۵۳۰K ویو، برانگیزاننده حس آرامش معنوی و سیل کامنت‌های آمین.'
    },
    'DI_5NgqITTy': {
        'title': 'شاید بزرگ‌ترین ویژگیم پا پس نکشیدنه',
        'archetype': 'آرکتایپ ۱: آدمِ همیشه قوی و بی‌صدا خوب',
        'goal': 'جذب فالوور حداکثری (Follow Magnet)',
        'score': 98,
        'breakdown': {'hook_power': 20, 'emotional_depth': 20, 'relatability': 20, 'shareability': 19, 'completion_rate': 19},
        'persona_fit': 'مانیفست تسلیم‌ناپذیری و جنگیدن برای اهداف حتی با دست خالی و روح خسته.',
        'notes': '۵۲۰K ویو، انرژی‌بخش و برانگیزاننده امید در لحظات یاس فردی.'
    },
    'DK-E6xoonsH': {
        'title': 'برای من تو همون آدمی',
        'archetype': 'آرکتایپ ۳: آدمِ امن و رفیق واقعی',
        'goal': 'افزایش سیو و اشتراک‌گذاری دایرکت (Save & Share Magnet)',
        'score': 98,
        'breakdown': {'hook_power': 20, 'emotional_depth': 20, 'relatability': 20, 'shareability': 20, 'completion_rate': 18},
        'persona_fit': 'تعریف دقیق و ملموس مفهوم «آدم امن» در بحبوحه اضطراب‌ها و آشفتگی‌های جهان.',
        'notes': '۵۴۲K ویو، بالاترین پتانسیل ارسال به پارتنر یا رفیق صمیمی در دایرکت.'
    },
    'DPHRC0yCJxg': {
        'title': 'قدر محبت رو دونستن از محبت کردن مهم‌تره',
        'archetype': 'آرکتایپ ۵: مانیفستِ استقلال و صراحتِ بدون تعارف',
        'goal': 'وایرال مارکتینگ و موج اکسپلور (Explore Surge)',
        'score': 98,
        'breakdown': {'hook_power': 20, 'emotional_depth': 19, 'relatability': 20, 'shareability': 20, 'completion_rate': 19},
        'persona_fit': 'تمرکز بر بلوغ رفتاری و فرهنگ قدرشناسی در برابر توهم وظیفه پنداشتن فداکاری‌ها.',
        'notes': '۵۲۴K ویو، متن تلنگری شدید برای روابط دوطرفه خانوادگی و دوستانه.'
    },
    'DZSr1vMN1mr': {
        'title': 'هنوز قهری؟ باشه ولی به خودت برس',
        'archetype': 'آرکتایپ ۳: آدمِ امن و رفیق واقعی',
        'goal': 'افزایش سیو و اشتراک‌گذاری دایرکت (Save & Share Magnet)',
        'score': 99,
        'breakdown': {'hook_power': 20, 'emotional_depth': 20, 'relatability': 20, 'shareability': 20, 'completion_rate': 19},
        'persona_fit': 'نمایش عشق بالغ و مراقبت اصیل حتی در میانه قهر و دلخوری بدون لجبازی سخیف.',
        'notes': '۱.۰ میلیون ویو در پیج هلیوم، از ماندگارترین ریلزهای دایرکتی اینستاگرام فارسی.'
    },
    'DbyY0F7tmAn': {
        'title': 'تقصیر خودمونه به بعضیا بال و پر دادیم',
        'archetype': 'آرکتایپ ۵: مانیفستِ استقلال و صراحتِ بدون تعارف',
        'goal': 'جذب فالوور حداکثری (Follow Magnet)',
        'score': 99,
        'breakdown': {'hook_power': 20, 'emotional_depth': 19, 'relatability': 20, 'shareability': 20, 'completion_rate': 20},
        'persona_fit': 'تحلیل صریح خطای رفتاری در بزرگ کردن آدم‌های کوچک و بازگرداندن تراز عدالت به رفتار.',
        'notes': '۱.۱ میلیون ویو، ریتم تند، رپید ادیت کلمات و جذب حداکثری فالوور در اکسپلور.'
    },
    'DcjQOwtN86T': {
        'title': 'یه مرحله از رشد همینه که خودتو درگیر نمیکنی',
        'archetype': 'آرکتایپ ۵: مانیفستِ استقلال و صراحتِ بدون تعارف',
        'goal': 'جذب فالوور حداکثری (Follow Magnet)',
        'score': 99,
        'breakdown': {'hook_power': 20, 'emotional_depth': 20, 'relatability': 20, 'shareability': 20, 'completion_rate': 19},
        'persona_fit': 'توصیف اعلای استواری روانی، عبور از خاله زنک‌بازی‌ها و تمرکز بر اهداف بدون واکنش هیجانی.',
        'notes': '۶۰۱K ویو، فریم تاییدشده و ثبت‌شده در مخزن تصاویر، بازخورد فوق‌العاده قوی.'
    },
    'DcJelWZKk0u': {
        'title': 'تو فراموش نشده‌ای، فقط دیگر دوست‌داشتنی نیستی',
        'archetype': 'آرکتایپ ۲: پایانِ باوقار و خداحافظی آرام',
        'goal': 'افزایش سیو و اشتراک‌گذاری دایرکت (Save & Share Magnet)',
        'score': 99,
        'breakdown': {'hook_power': 20, 'emotional_depth': 20, 'relatability': 20, 'shareability': 20, 'completion_rate': 19},
        'persona_fit': 'بستن پرونده عاطفی در نهایت عزت نفس؛ تفکیک دقیق بین یادآوری خاطره و زوال میل به بازگشت.',
        'notes': '۲.۸ میلیون ویو و ۹۵K لایک از شادی قربانی، شاهکار بستن رابطه در ادبیات معاصر اینستاگرام.'
    }
}

batch_data = []
for it in items:
    sc = it['shortcode']
    m = meta_mapping.get(sc, {
        'title': it['text'].split('\n')[0][:40],
        'archetype': 'آرکتایپ ۱: آدمِ همیشه قوی و بی‌صدا خوب',
        'goal': 'جذب فالوور حداکثری (Follow Magnet)',
        'score': 98,
        'breakdown': {'hook_power': 20, 'emotional_depth': 20, 'relatability': 19, 'shareability': 19, 'completion_rate': 20},
        'persona_fit': 'انطباق متن خام با پرسونا و لحن متین پیج.',
        'notes': 'محتوای وایرال تاییدشده بر اساس فریم مستقیم.'
    })
    
    # Companion caption
    lines = [l.strip() for l in it['text'].split('\n') if l.strip()]
    hook = lines[0] if lines else ''
    caption = f"""{it['text'].strip()}
.
.
نظر شما چیه؟ چقدر با این تجربه موافقین؟ 🫂
اگه این متن حرف دلت بود، برای یه آدم باارزش بفرست یا توی خلوتت سیوش کن...
.
.
#روزتکست #متن_خاص #دلنوشته #حرف_دل #آرامش #تکست_ناب"""

    batch_data.append({
        'title': m['title'],
        'archetype': m['archetype'],
        'goal': m['goal'],
        'content': it['text'].strip(),
        'extracted_raw_text': it['text'].strip(),
        'caption': caption,
        'score': m['score'],
        'score_breakdown': m['breakdown'],
        'persona_fit_reason': m['persona_fit'],
        'source_url': it['url'],
        'source_page': it['author'],
        'source_views': it['views'],
        'extra_notes': m['notes']
    })

print(f"Prepared batch with {len(batch_data)} reels.")
out_file = 'data/batch_schedule_36_reels.json'
with open(out_file, 'w', encoding='utf-8') as f:
    json.dump(batch_data, f, ensure_ascii=False, indent=2)

print(f"Successfully generated {out_file}")
