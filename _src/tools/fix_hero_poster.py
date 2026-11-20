"""Cleans the home page poster photo (img/hero-poster.webp): removes the old logo and words that
were drawn into the artwork at the bottom right, rebuilds the red shirt and the river behind them,
and writes the phone crop too (img/hero-poster-m.webp).

    pip install opencv-contrib-python-headless
    python3 _src/tools/fix_hero_poster.py Mon_Mela_Riverside_Connections.png

Steps: (1) mask the old logo, words and underline; (2) fill the river from river pixels and the shirt
from shirt pixels, separately, split by the outline of the man's back; (3) the artwork had darkened the
shirt behind its words, so that part is brought back to the shirt's own colour; (4) the faint lines
where the words were are filled again; (5) shirt over river with a soft outline."""
import pathlib
import sys

import cv2
import numpy as np

SITE = pathlib.Path(__file__).resolve().parents[2]
src = cv2.imread(sys.argv[1])
H, W = src.shape[:2]
yy, xx = np.mgrid[0:H, 0:W]

# 1. What to remove: white words, the yellow underline, the green logo disc (bottom-right box only).
x0, y0, x1, y1 = 1240, 555, 1672, 800
roi = src[y0:y1, x0:x1]
hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
b, g, r = [roi[:, :, i].astype(int) for i in range(3)]
words = (hsv[:, :, 2] > 150) & (hsv[:, :, 1] < 80)
underline = (hsv[:, :, 0] > 10) & (hsv[:, :, 0] < 38) & (hsv[:, :, 1] > 110) & (hsv[:, :, 2] > 140)
logo = (g > b - 10) & (g > r + 25) & (hsv[:, :, 1] > 70)
m = (words | underline | logo).astype(np.uint8) * 255
cv2.circle(m, (1367 - x0, 608 - y0), 45, 255, -1)
m = cv2.dilate(m, np.ones((5, 5), np.uint8))
remove = np.zeros((H, W), bool)
remove[y0:y1, x0:x1] = m > 0

# The man's back, from his neck down to the bottom edge (a smooth shoulder line).
back = [(1290, 572), (1312, 582), (1330, 600), (1345, 628), (1360, 665), (1377, 710), (1396, 758),
        (1418, 808), (1438, 852), (1458, 900), (1473, 941)]
poly = np.array(back + [(1473, 941), (1000, 941), (1000, 560), (1290, 560)], np.int32)
inside = np.zeros((H, W), np.uint8)
cv2.fillPoly(inside, [poly], 255)
inside = inside > 0


def fill(image, unknown, box, mode=cv2.xphoto.INPAINT_FSR_FAST):
    """Fills `unknown` pixels from the rest of `box` (x0, y0, x1, y1)."""
    X0, Y0, X1, Y1 = box
    crop = image[Y0:Y1, X0:X1].copy()
    known = np.where(unknown[Y0:Y1, X0:X1], 0, 255).astype(np.uint8)
    out = crop.copy()
    cv2.xphoto.inpaint(crop, known, out, mode)
    result = image.copy()
    result[Y0:Y1, X0:X1] = out
    return result


BOX = (1100, 460, 1672, 941)
# 2. River from river pixels; shirt from shirt pixels.
river = fill(src, remove | inside, BOX)
shirt = fill(src, remove | ~inside, BOX)

# 3. The darkened shirt behind the old words, back to the shirt's own colour (ramping in from x 1225).
lab = cv2.cvtColor(shirt, cv2.COLOR_BGR2LAB).astype(np.float32)
hazy = inside & (xx >= 1250) & (yy >= 560)
clear = inside & (xx >= 1130) & (xx < 1225) & (yy >= 620) & (yy < 900)
mapped = lab.copy()
for c in range(3):
    h, k = lab[..., c][hazy], lab[..., c][clear]
    mapped[..., c] = (lab[..., c] - h.mean()) / (h.std() + 1e-6) * k.std() + k.mean()
mapped = cv2.cvtColor(np.clip(mapped, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR).astype(np.float32)
ramp = (np.clip((xx - 1225) / 65.0, 0, 1) * (yy >= 555) * inside)[..., None]
shirt = np.clip(mapped * ramp + shirt.astype(np.float32) * (1 - ramp), 0, 255).astype(np.uint8)

# 4. The faint lines where the words were, filled again from the cloth around them, with a little grain.
edge_x = np.interp(yy, [p[1] for p in back], [p[0] for p in back])
strips = (((yy >= 668) & (yy < 708)) | ((yy >= 712) & (yy < 756))) & inside & (xx >= 1240) & (xx < edge_x - 6)
shirt = fill(shirt, strips, (1150, 600, 1500, 800), cv2.xphoto.INPAINT_FSR_BEST)
grain = np.random.default_rng(3).normal(0, 2.2, shirt.shape) * strips[..., None]
shirt = np.clip(shirt.astype(np.float32) + grain, 0, 255).astype(np.uint8)

# 5. Shirt over river, soft outline; only the bottom-right corner changes.
soft = cv2.GaussianBlur(inside.astype(np.float32), (0, 0), 1.1)[..., None]
corner = ((yy >= 550) & (xx >= 1220))[..., None]
merged = shirt.astype(np.float32) * soft + river.astype(np.float32) * (1 - soft)
final = np.where(corner, merged, src.astype(np.float32))
final = np.clip(final, 0, 255).astype(np.uint8)

rgb = cv2.cvtColor(final, cv2.COLOR_BGR2RGB)
from PIL import Image  # noqa: E402  (only needed to write WebP the same way as the other pictures)
img = Image.fromarray(rgb)
img.save(SITE / "img/hero-poster.webp", "WEBP", quality=82, method=6)
img.crop((360, 250, 1250, 941)).save(SITE / "img/hero-poster-m.webp", "WEBP", quality=82, method=6)
img.save("/tmp/hero/clean8.png")
print("written img/hero-poster.webp and img/hero-poster-m.webp")
