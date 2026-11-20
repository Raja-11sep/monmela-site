"""The four Join us card pictures, from the photos for each role.

    python3 _src/tools/make_join_cards.py <ambassador.jpg> <venue.jpg> <creator.jpg> <host.jpg>

Each photo: the white border and rounded corners left from a screenshot are cut off, then it is
scaled up 2x (the photos are small) with a light sharpen, and saved as img/join-<n>.webp
(n = the story picture the card used before: 4 ambassador, 3 venue, 2 creator, 5 host)."""
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter

SITE = Path(__file__).resolve().parents[2]
NUMBERS = [4, 3, 2, 5]

def trim_white(im, inset=8):
    a = np.asarray(im).astype(int)
    photo = a.min(2) < 236                       # anything that isn't the white border
    rows = np.where(photo.mean(1) > 0.5)[0]
    cols = np.where(photo.mean(0) > 0.5)[0]
    return im.crop((cols[0] + inset, rows[0] + inset, cols[-1] + 1 - inset, rows[-1] + 1 - inset))

def main(paths):
    for n, path in zip(NUMBERS, paths):
        im = trim_white(Image.open(path).convert("RGB"))
        im = im.resize((im.width * 2, im.height * 2), Image.LANCZOS)
        im = im.filter(ImageFilter.UnsharpMask(radius=1.4, percent=55, threshold=2))
        im.save(SITE / f"img/join-{n}.webp", quality=86, method=6)
        print(n, im.size)

if __name__ == "__main__":
    main(sys.argv[1:5])
