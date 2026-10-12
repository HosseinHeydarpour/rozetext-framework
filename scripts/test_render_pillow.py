import os
import sys
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display

font_titr_path = r"C:\Windows\Fonts\IRTitr.ttf"
font_lotus_path = r"C:\Windows\Fonts\IRLotusBold.ttf"

def reshape_text(text):
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)

def test_cover():
    bg_path = "assets/clean_templates/clean_dark_cover.png"
    im = Image.open(bg_path).convert("RGBA")
    # center crop 1080x1920
    if im.width != 1080:
        left = (im.width - 1080) // 2
        im = im.crop((left, 0, left + 1080, 1920))
    
    draw = ImageDraw.Draw(im)
    font = ImageFont.truetype(font_titr_path, 95)
    
    hook = "شاید بزرگ‌ترین ویژگیم\nهمین باشه..."
    lines = hook.split('\n')
    
    y = 650
    for line in lines:
        bidi_line = reshape_text(line)
        bbox = draw.textbbox((0, 0), bidi_line, font=font)
        w = bbox[2] - bbox[0]
        x = (1080 - w) // 2
        draw.text((x, y), bidi_line, font=font, fill=(255, 247, 237, 255))
        y += 160
        
    os.makedirs("tests/output", exist_ok=True)
    out = "tests/output/test_pillow_cover.png"
    im.save(out)
    print("Cover test saved to:", out)

test_cover()
