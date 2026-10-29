"""Mic-mode icons for the chat window (original simple shapes): T_Mic_Open (green, waves), T_Mic_PTT (amber, V key),
T_Mic_Live (red, PTT held), T_Mic_Off (grey, slashed). Output: TheKeepr_Demo/SourceArt/Icons/*.png (256 px)."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parents[1] / "TheKeepr_Demo" / "SourceArt" / "Icons"
OUT.mkdir(parents=True, exist_ok=True)
S = 256
WHITE = (255, 255, 255, 255)


def mic(d, cx, cy, col):
    d.rounded_rectangle((cx - 26, cy - 70, cx + 26, cy + 18), radius=26, fill=col)       # capsule
    d.arc((cx - 46, cy - 40, cx + 46, cy + 40), start=0, end=180, fill=col, width=10)    # cradle
    d.line((cx, cy + 40, cx, cy + 66), fill=col, width=10)                                # stem
    d.line((cx - 26, cy + 66, cx + 26, cy + 66), fill=col, width=10)                      # base


def icon(name, bg, extra=None):
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((6, 6, S - 6, S - 6), fill=bg, outline=(255, 255, 255, 230), width=6)
    mic(d, S // 2, S // 2 + 4, WHITE)
    if extra:
        extra(d)
    im.save(OUT / f"{name}.png")


def waves(d):
    for r in (70, 98):
        d.arc((128 - r, 124 - r, 128 + r, 124 + r), start=-40, end=40, fill=WHITE, width=9)
        d.arc((128 - r, 124 - r, 128 + r, 124 + r), start=140, end=220, fill=WHITE, width=9)


def vkey(d):
    d.rounded_rectangle((168, 156, 238, 226), radius=14, fill=(255, 255, 255, 255))
    try:
        f = ImageFont.truetype("arialbd.ttf", 52)
    except OSError:
        f = ImageFont.load_default()
    d.text((203, 191), "V", fill=(150, 90, 0, 255), font=f, anchor="mm")


def slash(d):
    d.line((60, 60, 196, 196), fill=(255, 255, 255, 255), width=14)


icon("T_Mic_Open", (20, 150, 80, 235), waves)
icon("T_Mic_PTT", (200, 125, 10, 235), vkey)
icon("T_Mic_Live", (210, 40, 60, 240), waves)
icon("T_Mic_Off", (90, 95, 110, 220), slash)
print("wrote", sorted(p.name for p in OUT.glob("*.png")))
