"""Cut the five Join us card pictures out of the card mockup (Bengali_Adda_Community_Join_Cards).

    python3 _src/tools/make_join_cards.py /path/to/mockup.png

For each card: keep the photo above the baked-in title, paint out the round icon (the page draws
its own), fill the rounded corners, scale up 2x, and fade the bottom into the card's dusk green so
the page's own words sit on it. Writes img/join-<n>.webp (n = the story number the card used before)."""
import sys
from pathlib import Path
import numpy as np
import cv2
from PIL import Image, ImageFilter

SITE = Path(__file__).resolve().parents[2]
DUSK = np.array([0x0B, 0x3B, 0x37], float)
# (output number, card left x, top y, right x in the mockup, y where the baked title starts, icon centre,
#  where to borrow the patch that covers the icon, as an offset from it)
CARDS = [
    (4, 104, 225, 542, 425, (161, 274), (150, -6)),     # campus ambassador
    (3, 559, 225, 997, 425, (620, 274), (0, 72)),     # venue or event partner
    (2, 1014, 225, 1453, 425, (1076, 274), (0, 70)),  # creator
    (5, 104, 565, 641, 768, (161, 616), (170, -10)),     # adda host
    (6, 662, 565, 1209, 760, (729, 616), "sky"),       # just tell me at launch
]

def cut(mock, x0, y0, x1, ytext, icon, borrow):
    bgr = cv2.cvtColor(np.asarray(mock), cv2.COLOR_RGB2BGR)
    # The baked icon disc: covered with a nearby patch of the same photo, blended in with a soft edge.
    disc = np.zeros(bgr.shape[:2], float)
    cv2.circle(disc, (icon[0], icon[1] + 3), 41, 1.0, -1)   # disc plus its shadow below
    if borrow == "sky":   # plain sky: each row takes the sky colour just right of the disc
        cx, cy = icon
        patch = bgr.astype(float).copy()
        right = np.median(bgr[:, cx + 46:cx + 100].astype(float), axis=1, keepdims=True)
        right = cv2.GaussianBlur(right, (0, 0), 14)
        patch[:] = right
        patch += np.random.default_rng(1).normal(0, 1.6, patch.shape)   # a little grain like the photo
    elif borrow:
        dx, dy = borrow
        patch = np.roll(bgr, (-dy, -dx), axis=(0, 1)).astype(float)
    else:   # no clean patch nearby: fill from the surrounding colours (fine for plain sky)
        known = (1 - cv2.dilate(disc, np.ones((9, 9), np.uint8)))[..., None]
        patch = np.zeros(bgr.shape, float)
        for sigma in (40, 18, 8):
            num = cv2.GaussianBlur(bgr * known, (0, 0), sigma)
            den = cv2.GaussianBlur(known[..., 0], (0, 0), sigma)[..., None]
            fill = num / np.maximum(den, 1e-6)
            trust = np.clip(den * 3, 0, 1)
            patch = patch * (1 - trust) + fill * trust
    alpha = cv2.GaussianBlur(disc, (0, 0), 5)[..., None]
    bgr = (bgr * (1 - alpha) + patch * alpha).round().astype(np.uint8)
    # Rounded top corners show the cream page: paint them from their surroundings.
    box = np.zeros(bgr.shape[:2], bool)
    for cx in (x0, x1):
        box[y0 - 4:y0 + 26, cx - 26:cx + 26] = True
    cream = np.abs(bgr.astype(int) - [244, 249, 253]).sum(2) < 90
    mask = cv2.dilate((box & cream).astype(np.uint8) * 255, np.ones((5, 5), np.uint8))
    clean = cv2.inpaint(bgr, mask, 7, cv2.INPAINT_TELEA)
    photo = cv2.cvtColor(clean[y0 + 2:ytext, x0 + 2:x1 - 2], cv2.COLOR_BGR2RGB)
    img = Image.fromarray(photo).resize((photo.shape[1] * 2, photo.shape[0] * 2), Image.LANCZOS)
    img = img.filter(ImageFilter.UnsharpMask(radius=1.6, percent=60, threshold=2))
    a = np.asarray(img).astype(float)
    h = a.shape[0]
    t = np.clip((np.arange(h) - h * 0.72) / (h * 0.28), 0, 1)[:, None, None] ** 1.3   # bottom 28%: fade to dusk
    a = a * (1 - t) + DUSK * t
    return Image.fromarray(a.round().astype(np.uint8))

def main(src):
    mock = Image.open(src).convert("RGB")
    for n, x0, y0, x1, ytext, icon, borrow in CARDS:
        out = cut(mock, x0, y0, x1, ytext, icon, borrow)
        out.save(SITE / f"img/join-{n}.webp", quality=84, method=6)
        print(n, out.size)

if __name__ == "__main__":
    main(sys.argv[1])
