#!/usr/bin/env python3
"""Generate transparent text overlay PNGs for the Reel.

Design principles:
- Modern rounded font (M PLUS Rounded 1c) for kawaii-but-tasteful headlines.
- Handwritten accent (Yusei Magic) for warmth.
- Generous safe zones, padded info-cards instead of heavy edge-to-edge gradients.
- QR scene leaves the QR completely unobstructed.
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

W, H = 1080, 1920
SAFE_X = 90  # safe horizontal margin
OUT = "/tmp/oden_work/overlays"
os.makedirs(OUT, exist_ok=True)

FONT_DIR = "/tmp/oden_work/fonts"
F_BLACK  = f"{FONT_DIR}/MPLUSRounded1c-Black.ttf"     # heaviest, headlines
F_BOLD   = f"{FONT_DIR}/MPLUSRounded1c-Bold.ttf"      # body bold
F_MED    = f"{FONT_DIR}/MPLUSRounded1c-Medium.ttf"    # body
F_HAND   = f"{FONT_DIR}/YuseiMagic-Regular.ttf"       # handwritten accent

# Color palette (warm food tones)
PINK   = (240, 90, 110, 255)
PINK_S = (255, 130, 150, 255)
DEEP   = (45, 28, 22, 255)        # near-black brown
CREAM  = (255, 244, 224, 255)
CREAM2 = (252, 232, 200, 255)
WHITE  = (255, 255, 255, 255)
GOLD   = (235, 165, 60, 255)
GREEN  = (110, 168, 90, 255)
INK    = (38, 30, 28, 255)


def font(path, size):
    return ImageFont.truetype(path, size)


def text_size(draw, text, fnt):
    bb = draw.textbbox((0, 0), text, font=fnt)
    return bb[2] - bb[0], bb[3] - bb[1]


def draw_text_centered(draw, y, text, fnt, fill, x_center=W // 2):
    w, _ = text_size(draw, text, fnt)
    draw.text((x_center - w // 2, y), text, font=fnt, fill=fill)


def draw_text_outline(draw, xy, text, fnt, fill, outline, ow=4):
    x, y = xy
    for dx in range(-ow, ow + 1):
        for dy in range(-ow, ow + 1):
            if dx * dx + dy * dy <= ow * ow:
                draw.text((x + dx, y + dy), text, font=fnt, fill=outline)
    draw.text((x, y), text, font=fnt, fill=fill)


def draw_text_outline_centered(draw, y, text, fnt, fill, outline, ow=4):
    w, _ = text_size(draw, text, fnt)
    draw_text_outline(draw, ((W - w) // 2, y), text, fnt, fill, outline, ow)


def soft_card(im, xy, wh, fill=(255, 255, 255, 235), radius=44, shadow=True):
    x, y = xy
    w, h = wh
    if shadow:
        sh = Image.new("RGBA", (w + 60, h + 60), (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle([30, 30, 30 + w, 30 + h], radius=radius, fill=(0, 0, 0, 110))
        sh = sh.filter(ImageFilter.GaussianBlur(14))
        im.alpha_composite(sh, (x - 30, y - 30 + 8))
    card = Image.new("RGBA", (w, h), fill)
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w, h], radius=radius, fill=255)
    card.putalpha(mask)
    im.alpha_composite(card, (x, y))


def draw_pill(draw, xy, wh, fill, radius=None):
    x, y = xy
    w, h = wh
    if radius is None:
        radius = h // 2
    draw.rounded_rectangle([x, y, x + w, y + h], radius=radius, fill=fill)


def gradient_band(im, y, h, top_alpha=0, bot_alpha=180):
    """Vertical alpha gradient band (transparent → black)."""
    band = Image.new("RGBA", (W, h), (0, 0, 0, 0))
    bd = ImageDraw.Draw(band)
    for i in range(h):
        a = int(top_alpha + (bot_alpha - top_alpha) * (i / h) ** 1.4)
        bd.rectangle([0, i, W, i + 1], fill=(0, 0, 0, a))
    im.alpha_composite(band, (0, y))


# ==================================================================== SCENES

def scene_hook():
    """01 - 新メニュー登場  (over steaming pot)"""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    gradient_band(im, 0, 720, top_alpha=210, bot_alpha=0)

    # NEW pill
    f_pill = font(F_BLACK, 52)
    label = "NEW MENU"
    tw, th = text_size(d, label, f_pill)
    pad_x, pad_y = 46, 20
    pw, ph = tw + pad_x * 2, th + pad_y * 2 + 10
    px = (W - pw) // 2
    py = 200
    draw_pill(d, (px, py), (pw, ph), PINK)
    d.text((px + pad_x, py + pad_y - 4), label, font=f_pill, fill=WHITE)

    # Big headline (single line, sized to safe zone)
    f_head = font(F_BLACK, 116)
    head = "新メニュー、登場。"
    draw_text_outline_centered(d, py + ph + 50, head, f_head, WHITE, INK, ow=7)

    # Sub
    f_sub = font(F_HAND, 60)
    sub = "あの“チビ〇おでん”に、新作。"
    draw_text_outline_centered(d, py + ph + 50 + 140, sub, f_sub, GOLD, INK, ow=4)

    im.save(f"{OUT}/01_hook.png")


def scene_tease():
    """02 - 迷ったら、コレ。  (over serving shot)"""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    gradient_band(im, H - 760, 760, top_alpha=0, bot_alpha=200)

    f1 = font(F_BLACK, 140)
    l1 = "迷ったら、"
    l2 = "コレ。"
    w1, h1 = text_size(d, l1, f1)
    w2, h2 = text_size(d, l2, f1)
    base_y = H - 580
    draw_text_outline_centered(d, base_y, l1, f1, WHITE, INK, ow=8)
    draw_text_outline_centered(d, base_y + h1 + 20, l2, f1, GOLD, INK, ow=8)

    f_sub = font(F_HAND, 56)
    draw_text_outline_centered(d, base_y + h1 + 20 + h2 + 60, "今夜、保存ボタン押して。",
                                f_sub, WHITE, INK, ow=4)

    im.save(f"{OUT}/02_tease.png")


def scene_logo():
    """03 - logo card  (own background)"""
    im = Image.new("RGBA", (W, H), CREAM)
    d = ImageDraw.Draw(im)

    # subtle warm pattern
    import random
    random.seed(42)
    for _ in range(60):
        x = random.randint(0, W); y = random.randint(0, H)
        r = random.randint(4, 18)
        col = random.choice([(255, 200, 215, 110), (255, 224, 170, 130), (160, 220, 170, 100)])
        d.ellipse([x - r, y - r, x + r, y + r], fill=col)

    # ribbon
    rib_w, rib_h = 720, 110
    rib_x = (W - rib_w) // 2; rib_y = 320
    draw_pill(d, (rib_x, rib_y), (rib_w, rib_h), PINK)
    f_rib = font(F_BLACK, 60)
    head = "迷ったらコレ！"
    hw, hh = text_size(d, head, f_rib)
    d.text((rib_x + (rib_w - hw) // 2, rib_y + (rib_h - hh) // 2 - 8), head, font=f_rib, fill=WHITE)

    # main title
    f_t1 = font(F_BLACK, 130)
    title = "チビ〇おでん"
    draw_text_outline_centered(d, 530, title, f_t1, DEEP, WHITE, ow=8)

    # huge "3種串"
    f_t2 = font(F_BLACK, 230)
    t2 = "3種串"
    draw_text_outline_centered(d, 720, t2, f_t2, PINK, WHITE, ow=12)

    # tagline pill
    f_tag = font(F_BLACK, 50)
    tag = "KAWAii DAKE ja ARIMASEN!!"
    tw, th = text_size(d, tag, f_tag)
    pad_x, pad_y = 38, 22
    pw, ph = tw + pad_x * 2, th + pad_y * 2 + 6
    px = (W - pw) // 2; py = 1080
    draw_pill(d, (px, py), (pw, ph), DEEP)
    d.text((px + pad_x, py + pad_y - 4), tag, font=f_tag, fill=GOLD)

    # JP translation in handwritten font
    f_jp = font(F_HAND, 64)
    jp = "可愛いだけじゃ、ありません。"
    draw_text_centered(d, py + ph + 50, jp, f_jp, DEEP)

    im.save(f"{OUT}/03_logo.png")


def scene_skewer(letter, ingredients, idx, accent):
    """04-06 - per-skewer detail with bottom info card.

    Top: small "おすすめ" pill only (food image breathes through).
    Middle: empty so the photo shows.
    Bottom: card with circle-letter + ingredients + price.
    """
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    # Top "おすすめ" + letter pill (compact, doesn't dominate)
    f_top = font(F_BLACK, 48)
    top_label = f"おすすめ  {letter}"
    tw, th = text_size(d, top_label, f_top)
    pad = 40
    pw = tw + pad * 2; ph = th + 30
    draw_pill(d, ((W - pw) // 2, 100), (pw, ph), accent)
    d.text(((W - pw) // 2 + pad, 100 + 10), top_label, font=f_top, fill=WHITE)

    # Bottom info card
    card_h = 760
    card_y = H - card_h - 70
    soft_card(im, (60, card_y), (W - 120, card_h), fill=(255, 250, 244, 242), radius=56)

    # accent bar header inside card
    d.rounded_rectangle([100, card_y + 78, W - 100, card_y + 90], radius=6, fill=accent)

    # giant accent circle (overlaps top edge of card)
    cx, cy, cr = 230, card_y - 30, 130
    sh = Image.new("RGBA", (cr * 2 + 80, cr * 2 + 80), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse([40, 50, 40 + cr * 2, 50 + cr * 2], fill=(0, 0, 0, 120))
    sh = sh.filter(ImageFilter.GaussianBlur(12))
    im.alpha_composite(sh, (cx - cr - 40, cy - cr - 50))
    d.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=accent)
    # thin white inner border
    d.ellipse([cx - cr + 8, cy - cr + 8, cx + cr - 8, cy + cr - 8],
              outline=(255, 255, 255, 200), width=4)
    f_letter = font(F_BLACK, 180)
    lw, lh = text_size(d, letter, f_letter)
    d.text((cx - lw // 2, cy - lh // 2 - 18), letter, font=f_letter, fill=WHITE)

    # "の3種" handwritten label - put in a small white pill so it reads on any bg
    f_label = font(F_HAND, 52)
    lbl = "の3種"
    lw, lh = text_size(d, lbl, f_label)
    lpx = cx + cr + 24
    lpy = cy - lh // 2 - 6
    d.rounded_rectangle([lpx - 18, lpy - 8, lpx + lw + 18, lpy + lh + 14],
                        radius=22, fill=(255, 250, 244, 240))
    d.text((lpx, lpy), lbl, font=f_label, fill=DEEP)

    # ingredient list (3 items)
    f_ing = font(F_BLACK, 88)
    y = card_y + 150
    for ing in ingredients:
        d.ellipse([130, y + 30, 184, y + 84], fill=accent)
        d.text((216, y), ing, font=f_ing, fill=DEEP)
        y += 130

    # price strip
    f_p1 = font(F_BLACK, 56)
    f_p2 = font(F_BLACK, 88)
    qty, yen = "1本", "¥300"
    yw, _ = text_size(d, yen, f_p2)
    qw, _ = text_size(d, qty, f_p1)
    total = qw + 24 + yw
    px0 = (W - total) // 2
    py0 = card_y + card_h - 140
    draw_pill(d, (px0 - 56, py0 - 14), (total + 112, 118), accent)
    d.text((px0, py0 + 28), qty, font=f_p1, fill=WHITE)
    d.text((px0 + qw + 24, py0 + 6), yen, font=f_p2, fill=WHITE)

    im.save(f"{OUT}/{idx:02d}_skewer_{letter}.png")


def scene_tagline():
    """07 - 可愛いだけじゃない、ちゃんと、旨い。  (over group shot)"""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    gradient_band(im, H - 820, 820, top_alpha=0, bot_alpha=210)

    f = font(F_BLACK, 88)
    l1 = "可愛いだけじゃない、"
    l2 = "ちゃんと、旨い。"
    w1, h1 = text_size(d, l1, f)
    w2, h2 = text_size(d, l2, f)
    y0 = H - 540
    draw_text_outline_centered(d, y0, l1, f, WHITE, INK, ow=6)
    draw_text_outline_centered(d, y0 + h1 + 24, l2, f, GOLD, INK, ow=6)

    f_sub = font(F_HAND, 50)
    draw_text_outline_centered(d, y0 + h1 + 24 + h2 + 50,
                                "出汁の染みた、ひと口サイズ。",
                                f_sub, WHITE, INK, ow=4)

    im.save(f"{OUT}/07_tagline.png")


def scene_price():
    """08 - price table  (over assorted plate, lower card)"""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    # top dim
    gradient_band(im, 0, 380, top_alpha=200, bot_alpha=0)

    f_h = font(F_BLACK, 76)
    head = "選べる3種から、お好きに。"
    draw_text_outline_centered(d, 110, head, f_h, WHITE, INK, ow=6)

    # bottom card
    card_h = 920
    card_y = H - card_h - 60
    soft_card(im, (50, card_y), (W - 100, card_h), fill=(255, 250, 244, 245), radius=60)

    # title strip in card
    f_ct = font(F_BLACK, 60)
    draw_text_centered(d, card_y + 50, "OPTION", f_ct, PINK)
    draw_text_centered(d, card_y + 130, "本数で、もっとお得に。", font(F_HAND, 48), DEEP)

    # rows
    items = [
        ("1本", "¥300", "お試し", GOLD),
        ("2本", "¥500", "お得！", PINK_S),
        ("3本", "¥680", "さらにお得！！", PINK),
    ]
    f_qty = font(F_BLACK, 110)
    f_yen = font(F_BLACK, 130)
    f_bdg = font(F_BLACK, 40)
    row_y = card_y + 240
    row_gap = 200
    row_x_left = 130
    row_x_right_pad = 130
    for i, (qty, yen, badge, color) in enumerate(items):
        ry = row_y + i * row_gap

        # badge above qty
        bw, bh = text_size(d, badge, f_bdg)
        bp_w, bp_h = bw + 44, bh + 22
        draw_pill(d, (row_x_left, ry - 8), (bp_w, bp_h), color)
        d.text((row_x_left + 22, ry - 8 + 6), badge, font=f_bdg, fill=WHITE)

        # qty (left)
        d.text((row_x_left, ry + bp_h + 6), qty, font=f_qty, fill=DEEP)

        # yen (right, baseline aligned)
        yw, yh = text_size(d, yen, f_yen)
        d.text((W - row_x_right_pad - yw, ry + bp_h - 4), yen, font=f_yen, fill=color)

        # divider (except last)
        if i < len(items) - 1:
            d.rounded_rectangle([row_x_left, ry + row_gap - 28,
                                 W - row_x_right_pad, ry + row_gap - 22],
                                radius=3, fill=(220, 200, 180, 220))

    im.save(f"{OUT}/08_price.png")


def scene_cta():
    """09 - QR + reservation CTA. KEEP CENTRAL QR REGION CLEAR."""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    # top dim band for headline
    gradient_band(im, 0, 460, top_alpha=210, bot_alpha=0)
    # bottom dim band for CTA
    gradient_band(im, H - 360, 360, top_alpha=0, bot_alpha=210)

    # ---- top headline (two lines)
    f1 = font(F_BLACK, 92)
    l1 = "今夜、おでんスタンドで。"
    # if too wide, split
    w1, h1 = text_size(d, l1, f1)
    if w1 > W - SAFE_X * 2:
        l1a = "今夜、"
        l1b = "おでんスタンドで。"
        h_a = text_size(d, l1a, f1)[1]
        draw_text_outline_centered(d, 100, l1a, f1, WHITE, INK, ow=7)
        draw_text_outline_centered(d, 100 + h_a + 14, l1b, f1, GOLD, INK, ow=7)
        head_bot = 100 + h_a + 14 + text_size(d, l1b, f1)[1]
    else:
        draw_text_outline_centered(d, 130, l1, f1, GOLD, INK, ow=7)
        head_bot = 130 + h1

    f_sub = font(F_HAND, 50)
    draw_text_outline_centered(d, head_bot + 20, "▼QRから、すぐご予約。", f_sub, WHITE, INK, ow=4)

    # ---- bottom CTA pill (no QR overlap; QR sits in middle of frame at ~y=900-1500)
    f2 = font(F_BLACK, 56)
    s = "ご予約はプロフィールから →"
    sw, sh = text_size(d, s, f2)
    py = H - 200
    draw_pill(d, ((W - sw) // 2 - 44, py), (sw + 88, sh + 50), PINK)
    d.text(((W - sw) // 2, py + 12), s, font=f2, fill=WHITE)

    im.save(f"{OUT}/09_cta.png")


if __name__ == "__main__":
    scene_hook()
    scene_tease()
    scene_logo()
    scene_skewer("A", ["こんにゃく", "子にゃんぺん", "ちくわ"],   4, accent=(238, 100, 130, 255))
    scene_skewer("B", ["こんにゃく", "鶏つくね",   "しゅうまい"], 5, accent=(232, 150, 50, 255))
    scene_skewer("C", ["こんにゃく", "たこ焼き",   "厚揚げ"],     6, accent=(120, 178, 80, 255))
    scene_tagline()
    scene_price()
    scene_cta()
    print("done")
