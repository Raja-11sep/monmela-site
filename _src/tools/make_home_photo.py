"""Make the home page hero pictures from the raw riverside photo (no words or icons baked in).

    python3 _src/tools/make_home_photo.py /path/to/raw-photo.png

Writes img/home-hero.webp (the full photo, for wide screens) and img/home-hero-m.webp
(a 5:3 crop that keeps all five faces, for phones). The five round icons are separate files
(img/home-icon-1..5.png) laid out as HTML, so they wrap with the screen."""
import sys
from pathlib import Path
from PIL import Image

SITE = Path(__file__).resolve().parents[2]

def main(src):
    photo = Image.open(src).convert("RGB")
    photo.save(SITE / "img/home-hero.webp", quality=82, method=6)
    phone = photo.crop((480, 140, 1640, 835)).resize((1080, 647), Image.LANCZOS)  # five faces, 5:3
    phone.save(SITE / "img/home-hero-m.webp", quality=80, method=6)
    print(photo.size, phone.size)

if __name__ == "__main__":
    main(sys.argv[1])
