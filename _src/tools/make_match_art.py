"""Pictures for the home page's "Matched by what you share" section, from two transparent PNGs.

    python3 _src/tools/make_match_art.py <match-cards.png> <victoria-memorial-line-art.png>

img/match-cards.webp (+ -m for phones): the two profile cards with their 86% badge.
img/match-city.webp: the gold line drawing of Victoria Memorial and a boat (bottom left, faint).
Both are trimmed to what is drawn; the transparent edges are cut off."""
import sys
from pathlib import Path
from PIL import Image

SITE = Path(__file__).resolve().parents[2]

def trimmed(src):
    im = Image.open(src).convert("RGBA")
    return im.crop(im.getchannel("A").point(lambda a: 255 if a > 8 else 0).getbbox())

def main(cards_src, city_src):
    cards = trimmed(cards_src)
    cards.save(SITE / "img/match-cards.webp", quality=88, method=6)
    cards.resize((cards.width * 2 // 3, cards.height * 2 // 3), Image.LANCZOS).save(
        SITE / "img/match-cards-m.webp", quality=86, method=6)
    city = trimmed(city_src)
    city.save(SITE / "img/match-city.webp", quality=88, method=6)
    print("cards", cards.size, "city", city.size)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
