"""Turns the home page mockup (one flat picture) into the pieces the page is built from:

  img/home-hero.webp      the photo part (top 700 px) with every word, the logo and the menu taken out;
                          the five round icons and their dividers stay, the page puts the words back
  img/home-hero-m.webp    phones: a closer crop of the five friends
  img/home-icon-1…5.png   the five round icons on their own (phones show them in a row)
  img/how-1…3.webp        the three "How it works" drawings
  img/skyline-strip.webp  the green Kolkata skyline along the bottom, drawings taken out

    pip install opencv-contrib-python-headless
    python3 _src/tools/make_home_hero.py Mon_Mela__Find_Your_Community.png
"""
import pathlib
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw

SITE = pathlib.Path(__file__).resolve().parents[2]
IMG = SITE / "img"
src = cv2.imread(sys.argv[1])
H, W = src.shape[:2]


def fill(image, mask, box):
    """Fill masked pixels inside box (x0, y0, x1, y1) from the pixels around them."""
    x0, y0, x1, y1 = box
    crop = image[y0:y1, x0:x1].copy()
    known = np.where(mask[y0:y1, x0:x1], 0, 255).astype(np.uint8)
    out = crop.copy()
    cv2.xphoto.inpaint(crop, known, out, cv2.xphoto.INPAINT_FSR_FAST)
    image[y0:y1, x0:x1] = out


def dark_text(box, v=150, grow=3):
    """Mask of dark lettering inside box (on the light sky)."""
    x0, y0, x1, y1 = box
    hsv = cv2.cvtColor(src[y0:y1, x0:x1], cv2.COLOR_BGR2HSV)
    m = (hsv[:, :, 2] < v).astype(np.uint8) * 255
    m = cv2.dilate(m, np.ones((grow, grow), np.uint8), iterations=2)
    out = np.zeros((H, W), bool)
    out[y0:y1, x0:x1] = m > 0
    return out


def rect(*boxes):
    out = np.zeros((H, W), bool)
    for x0, y0, x1, y1 in boxes:
        out[y0:y1, x0:x1] = True
    return out


# ---------------------------------------------------------------- the round icons, before anything changes
ICONS = [(652, 135), (814, 135), (966, 135), (1116, 135), (1281, 135)]
rgb = Image.open(sys.argv[1]).convert("RGBA")
for n, (cx, cy) in enumerate(ICONS, 1):
    r = 37
    icon = rgb.crop((cx - r, cy - r, cx + r, cy + r)).resize((148, 148), Image.LANCZOS)
    mask = Image.new("L", (148, 148), 0)
    ImageDraw.Draw(mask).ellipse((2, 2, 145, 145), fill=255)
    icon.putalpha(mask)
    icon.save(IMG / f"home-icon-{n}.png", optimize=True)

# ---------------------------------------------------------------- the three drawings and the skyline
for n, box in enumerate([(392, 728, 548, 878), (846, 742, 1104, 884), (1462, 738, 1614, 850)], 1):
    Image.open(sys.argv[1]).convert("RGB").crop(box).save(IMG / f"how-{n}.webp", "WEBP", quality=88)
# The strip starts below the step texts (y 838); the bottoms of the phone, the friends and the red
# bubble reach into it and are filled from the hazy skyline around them.
strip = src.copy()
cut = rect((388, 838, 512, 878), (838, 838, 1094, 880), (1520, 838, 1604, 850))
fill(strip, cut, (300, 838, 1200, 941))
fill(strip, cut, (1400, 838, 1672, 941))
Image.fromarray(cv2.cvtColor(strip[838:941], cv2.COLOR_BGR2RGB)).save(IMG / "skyline-strip.webp", "WEBP", quality=86)

# ---------------------------------------------------------------- the photo, words out
# Cut just above the mockup's white wave; the page draws its own wave over the bottom edge.
H = 660
src = src[:H]
hero = src.copy()
words = (
    rect((60, 18, 400, 118),            # logo and name
         (60, 255, 552, 352),           # Mon Mela
         (60, 358, 532, 482),           # the line under it
         (268, 448, 478, 498),          # yellow underline
         (1336, 30, 1540, 90))          # English / বাংলা
    | dark_text((500, 38, 1060, 84))    # menu
    | dark_text((598, 170, 1330, 224))  # icon labels (the grey dividers stay)
)
# Small words on the sky (menu, icon labels): fill from the pixels round them.
for box in [(480, 20, 1080, 100), (580, 150, 1350, 240)]:
    fill(hero, words, box)
# Big words on the out-of-focus left side (logo, heading, its line, language switch): those spots are
# soft haze anyway, so fill them with a wide blur of the picture made without the lettering
# ("normalised" blur: only the pixels that aren't lettering count), and blend that in softly.
big = rect((60, 18, 400, 118), (60, 250, 556, 500), (1336, 30, 1540, 90))
big |= dark_text((40, 240, 580, 510), v=110) & rect((40, 240, 580, 510))
known = (~(big | words)).astype(np.float32)
haze = None
for sigma in (140, 60, 26):   # wide first, then finer wherever enough real pixels are near
    num = cv2.GaussianBlur(hero.astype(np.float32) * known[..., None], (0, 0), sigma)
    den = cv2.GaussianBlur(known, (0, 0), sigma)[..., None]
    layer = num / np.maximum(den, 1e-4)
    trust = np.clip((den - 0.15) / 0.35, 0, 1)
    haze = layer if haze is None else layer * trust + haze * (1 - trust)
w = cv2.GaussianBlur((big | (words & rect((0, 0, 640, 520)))).astype(np.float32), (0, 0), 22)
w = np.clip(w * 2.2, 0, 1)[..., None]
hero = np.clip(haze * w + hero.astype(np.float32) * (1 - w), 0, 255).astype(np.uint8)
photo = Image.fromarray(cv2.cvtColor(hero, cv2.COLOR_BGR2RGB))
# The hero pictures now come from the raw photo: see make_home_photo.py.
photo.save("/tmp/home-hero-check.png")
print("done")
