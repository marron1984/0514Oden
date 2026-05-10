#!/usr/bin/env python3
"""Generate transparent text overlay PNGs for the Reel."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

W, H = 1080, 1920
OUT = "/tmp/oden_work/overlays"
os.makedirs(OUT, exist_ok=True)

JP_BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
JP_REG  = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"

PINK   = (255, 92, 130, 255)
WHITE  = (255, 255, 255, 255)
BLACK  = (24, 24, 24, 255)
CREAM  = (255, 246, 224, 255)
DEEP   = (60, 30, 20, 255)
GOLD   = (255, 196, 60, 255)


def font(path, size):
    return ImageFont.truetype(path, size)


def text_size(draw, text, fnt):
    bb = draw.textbbox((0, 0), text, font=fnt)
    return bb[2] - bb[0], bb[3] - bb[1]


def draw_text_with_outline(draw, xy, text, fnt, fill, outline, ow=6):
    x, y = xy
    for dx in range(-ow, ow + 1):
        for dy in range(-ow, ow + 1):
            if dx * dx + dy * dy <= ow * ow:
                draw.text((x + dx, y + dy), text, font=fnt, fill=outline)
    draw.text((x, y), text, font=fnt, fill=fill)


def draw_pill(draw, xy, wh, fill, radius=None):
    x, y = xy
    w, h = wh
    if radius is None:
        radius = h // 2
    draw.rounded_rectangle([x, y, x + w, y + h], radius=radius, fill=fill)


def with_shadow(im):
    shadow = Image.new("RGBA", im.size, (0, 0, 0, 0))
    a = im.split()[-1]
    shadow.putalpha(a.point(lambda v: int(v * 0.55)))
    shadow = shadow.filter(ImageFilter.GaussianBlur(8))
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    out = Image.alpha_composite(out, Image.merge("RGBA", (Image.new("L", im.size, 0), Image.new("L", im.size, 0), Image.new("L", im.size, 0), shadow.split()[-1])))
    out = Image.alpha_composite(out, im)
    return out


def scene_hook():
    """新メニュー登場 ✨"""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    # Top dimming for legibility
    band = Image.new("RGBA", (W, 520), (0, 0, 0, 0))
    bd = ImageDraw.Draw(band)
    for i in range(520):
        a = int(170 * (1 - i / 520) ** 1.4)
        bd.rectangle([0, i, W, i + 1], fill=(0, 0, 0, a))
    im.alpha_composite(band, (0, 0))

    # NEW MENU pill
    f1 = font(JP_BOLD, 56)
    label = "NEW MENU"
    tw, th = text_size(d, label, f1)
    pad_x, pad_y = 50, 22
    pw, ph = tw + pad_x * 2, th + pad_y * 2 + 12
    px = (W - pw) // 2
    py = 200
    draw_pill(d, (px, py), (pw, ph), PINK)
    d.text((px + pad_x, py + pad_y - 6), label, font=f1, fill=WHITE)

    # Big JP headline
    f2 = font(JP_BOLD, 110)
    line = "新メニュー登場"
    lw, lh = text_size(d, line, f2)
    draw_text_with_outline(d, ((W - lw) // 2, py + ph + 40), line, f2, WHITE, BLACK, ow=7)

    f3 = font(JP_BOLD, 70)
    sub = "チビ〇おでん 3種串"
    sw, sh = text_size(d, sub, f3)
    draw_text_with_outline(d, ((W - sw) // 2, py + ph + 40 + lh + 30), sub, f3, GOLD, BLACK, ow=6)

    im.save(f"{OUT}/01_hook.png")


def scene_tease():
    """迷ったら、コレ！"""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    # bottom band
    band = Image.new("RGBA", (W, 600), (0, 0, 0, 0))
    bd = ImageDraw.Draw(band)
    for i in range(600):
        a = int(170 * (i / 600) ** 1.4)
        bd.rectangle([0, i, W, i + 1], fill=(0, 0, 0, a))
    im.alpha_composite(band, (0, H - 600))

    f = font(JP_BOLD, 130)
    line1 = "迷ったら、"
    line2 = "コレ。"
    w1, h1 = text_size(d, line1, f)
    w2, h2 = text_size(d, line2, f)
    base_y = H - 480
    draw_text_with_outline(d, ((W - w1) // 2, base_y), line1, f, WHITE, BLACK, ow=8)
    draw_text_with_outline(d, ((W - w2) // 2, base_y + h1 + 30), line2, f, PINK, WHITE, ow=8)

    f2 = font(JP_BOLD, 50)
    sub = "本日の主役は、コレ。"
    sw, _ = text_size(d, sub, f2)
    draw_text_with_outline(d, ((W - sw) // 2, base_y + h1 + 30 + h2 + 60), sub, f2, WHITE, BLACK, ow=4)

    im.save(f"{OUT}/02_tease.png")


def scene_logo():
    """チビ〇おでん 3種串 / KAWAii DAKE ja ARIMASEN"""
    im = Image.new("RGBA", (W, H), CREAM)
    d = ImageDraw.Draw(im)

    # decorative dots
    import random
    random.seed(7)
    for _ in range(80):
        x = random.randint(0, W)
        y = random.randint(0, H)
        r = random.randint(4, 14)
        c = random.choice([(255, 200, 210, 180), (255, 230, 170, 180), (255, 170, 190, 160)])
        d.ellipse([x - r, y - r, x + r, y + r], fill=c)

    # ribbon top
    draw_pill(d, (110, 360), (W - 220, 130), PINK)
    f1 = font(JP_BOLD, 70)
    head = "迷ったらコレ！"
    hw, hh = text_size(d, head, f1)
    d.text(((W - hw) // 2, 360 + (130 - hh) // 2 - 10), head, font=f1, fill=WHITE)

    # main title
    f2 = font(JP_BOLD, 130)
    line = "チビ〇おでん"
    lw, lh = text_size(d, line, f2)
    draw_text_with_outline(d, ((W - lw) // 2, 600), line, f2, DEEP, WHITE, ow=10)

    f3 = font(JP_BOLD, 200)
    line2 = "3種串"
    l2w, l2h = text_size(d, line2, f3)
    draw_text_with_outline(d, ((W - l2w) // 2, 800), line2, f3, PINK, WHITE, ow=12)

    # tagline pill
    f4 = font(JP_BOLD, 50)
    tag = "KAWAii DAKE ja ARIMASEN!!"
    tw, th = text_size(d, tag, f4)
    pad_x, pad_y = 40, 24
    pw, ph = tw + pad_x * 2, th + pad_y * 2 + 8
    px = (W - pw) // 2
    py = 1100
    draw_pill(d, (px, py), (pw, ph), DEEP)
    d.text((px + pad_x, py + pad_y - 4), tag, font=f4, fill=GOLD)

    f5 = font(JP_BOLD, 56)
    jp = "可愛いだけじゃ、ありません！！"
    jw, jh = text_size(d, jp, f5)
    draw_text_with_outline(d, ((W - jw) // 2, py + ph + 50), jp, f5, DEEP, WHITE, ow=4)

    im.save(f"{OUT}/03_logo.png")


def scene_skewer(letter, ingredients, idx, accent=PINK):
    """A/B/C skewer detail card."""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    # bottom info card
    card_h = 720
    card = Image.new("RGBA", (W - 100, card_h), (255, 255, 255, 240))
    cd = ImageDraw.Draw(card)
    # rounded corners by drawing rounded rect on transparent canvas
    mask = Image.new("L", card.size, 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle([0, 0, card.size[0], card.size[1]], radius=48, fill=255)
    card.putalpha(mask)
    im.alpha_composite(card, (50, H - card_h - 80))

    # giant letter circle
    cx, cy, cr = 230, H - card_h - 80 - 20, 130
    d.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=accent)
    fL = font(JP_BOLD, 180)
    lw, lh = text_size(d, letter, fL)
    d.text((cx - lw // 2, cy - lh // 2 - 18), letter, font=fL, fill=WHITE)

    # Header
    f1 = font(JP_BOLD, 64)
    head = f"{letter} の3種"
    d.text((400, H - card_h - 30), head, font=f1, fill=DEEP)

    # divider
    d.rectangle([100, H - card_h + 60, W - 100, H - card_h + 66], fill=accent)

    # ingredients
    f2 = font(JP_BOLD, 88)
    y = H - card_h + 110
    for i, ing in enumerate(ingredients):
        # bullet circle
        d.ellipse([130, y + 24, 180, y + 74], fill=accent)
        d.text((210, y), f"{ing}", font=f2, fill=DEEP)
        y += 130

    # price
    f3 = font(JP_BOLD, 64)
    price = "1本 ¥300"
    pw, ph = text_size(d, price, f3)
    py2 = H - 200
    draw_pill(d, ((W - pw) // 2 - 40, py2 - 18), (pw + 80, ph + 36), accent)
    d.text(((W - pw) // 2, py2 - 8), price, font=f3, fill=WHITE)

    im.save(f"{OUT}/{idx:02d}_skewer_{letter}.png")


def scene_tagline():
    """可愛いだけじゃない、ちゃんと旨い。"""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    # darken
    band = Image.new("RGBA", (W, 760), (0, 0, 0, 0))
    bd = ImageDraw.Draw(band)
    for i in range(760):
        a = int(180 * (i / 760) ** 1.4)
        bd.rectangle([0, i, W, i + 1], fill=(0, 0, 0, a))
    im.alpha_composite(band, (0, H - 760))

    f = font(JP_BOLD, 96)
    l1 = "可愛いだけじゃない、"
    l2 = "ちゃんと、旨い。"
    w1, h1 = text_size(d, l1, f)
    w2, h2 = text_size(d, l2, f)
    y0 = H - 560
    draw_text_with_outline(d, ((W - w1) // 2, y0), l1, f, WHITE, BLACK, ow=7)
    draw_text_with_outline(d, ((W - w2) // 2, y0 + h1 + 30), l2, f, GOLD, BLACK, ow=7)

    f2 = font(JP_BOLD, 46)
    s = "出汁の染みた、ひと口サイズ。"
    sw, sh = text_size(d, s, f2)
    draw_text_with_outline(d, ((W - sw) // 2, y0 + h1 + 30 + h2 + 60), s, f2, WHITE, BLACK, ow=4)

    im.save(f"{OUT}/07_tagline.png")


def scene_price():
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    # top dim
    band = Image.new("RGBA", (W, 520), (0, 0, 0, 0))
    bd = ImageDraw.Draw(band)
    for i in range(520):
        a = int(160 * (1 - i / 520) ** 1.4)
        bd.rectangle([0, i, W, i + 1], fill=(0, 0, 0, a))
    im.alpha_composite(band, (0, 0))

    f1 = font(JP_BOLD, 76)
    head = "選べる3種から、お好きに♪"
    hw, hh = text_size(d, head, f1)
    draw_text_with_outline(d, ((W - hw) // 2, 130), head, f1, WHITE, BLACK, ow=6)

    # bottom card
    card_h = 820
    card = Image.new("RGBA", (W - 80, card_h), (255, 255, 255, 240))
    mask = Image.new("L", card.size, 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle([0, 0, card.size[0], card.size[1]], radius=56, fill=255)
    card.putalpha(mask)
    im.alpha_composite(card, (40, H - card_h - 80))

    fP = font(JP_BOLD, 96)
    fY = font(JP_BOLD, 128)

    items = [
        ("1本",   "¥300", "お試し"),
        ("2本",   "¥500", "お得！"),
        ("3本",   "¥680", "さらにお得！！"),
    ]
    y = H - card_h - 20
    for i, (qty, yen, badge) in enumerate(items):
        row_y = y + i * 235
        # badge pill
        fb = font(JP_BOLD, 44)
        bw, bh = text_size(d, badge, fb)
        bcol = [GOLD, PINK, (220, 40, 80, 255)][i]
        draw_pill(d, (110, row_y), (bw + 60, bh + 24), bcol)
        d.text((140, row_y + 8), badge, font=fb, fill=WHITE)

        # qty
        d.text((110, row_y + bh + 50), qty, font=fP, fill=DEEP)

        # yen
        yw, yh = text_size(d, yen, fY)
        d.text((W - 80 - yw - 60, row_y + bh + 30), yen, font=fY, fill=PINK)

    im.save(f"{OUT}/08_price.png")


def scene_cta():
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    # top dim band for headline
    band = Image.new("RGBA", (W, 400), (0, 0, 0, 0))
    bd = ImageDraw.Draw(band)
    for i in range(400):
        a = int(190 * (1 - i / 400) ** 1.4)
        bd.rectangle([0, i, W, i + 1], fill=(0, 0, 0, a))
    im.alpha_composite(band, (0, 0))

    # bottom dim band for CTA
    band2 = Image.new("RGBA", (W, 460), (0, 0, 0, 0))
    bd2 = ImageDraw.Draw(band2)
    for i in range(460):
        a = int(190 * (i / 460) ** 1.4)
        bd2.rectangle([0, i, W, i + 1], fill=(0, 0, 0, a))
    im.alpha_composite(band2, (0, H - 460))

    # top headline (two lines, fits within frame)
    f1 = font(JP_BOLD, 90)
    l1 = "今夜、"
    l2 = "おでんスタンドで。"
    w1, h1 = text_size(d, l1, f1)
    w2, h2 = text_size(d, l2, f1)
    draw_text_with_outline(d, ((W - w1) // 2, 90), l1, f1, WHITE, BLACK, ow=6)
    draw_text_with_outline(d, ((W - w2) // 2, 90 + h1 + 14), l2, f1, GOLD, BLACK, ow=6)

    # bottom CTA pill
    f2 = font(JP_BOLD, 56)
    s = "ご予約はプロフィールから →"
    sw, sh = text_size(d, s, f2)
    py = H - 220
    draw_pill(d, ((W - sw) // 2 - 40, py), (sw + 80, sh + 50), PINK)
    d.text(((W - sw) // 2, py + 12), s, font=f2, fill=WHITE)

    f3 = font(JP_BOLD, 44)
    s2 = "▼ QRコードからもどうぞ"
    s2w, _ = text_size(d, s2, f3)
    draw_text_with_outline(d, ((W - s2w) // 2, py - 70), s2, f3, WHITE, BLACK, ow=4)

    im.save(f"{OUT}/09_cta.png")


if __name__ == "__main__":
    scene_hook()
    scene_tease()
    scene_logo()
    scene_skewer("A", ["こんにゃく", "子にゃんぺん", "ちくわ"], 4, accent=(255, 110, 130, 255))
    scene_skewer("B", ["こんにゃく", "鶏つくね", "しゅうまい"], 5, accent=(255, 160, 60, 255))
    scene_skewer("C", ["こんにゃく", "たこ焼き", "厚揚げ"], 6, accent=(140, 195, 80, 255))
    scene_tagline()
    scene_price()
    scene_cta()
    print("done")
