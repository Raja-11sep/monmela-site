# Prepares app screenshots for the website's phone mockups.
#   - status bar (top 70 px): replaced by copying the row just below it upward (clean, no icons)
#   - system navigation bar (bottom 80 px): cropped off
#   - optional fixes: hide a toast by pasting rows from another screenshot; blur a photo for privacy
# Usage: python3 _src/tools/prep_screens.py <folder with welcome.jpg looking-for.jpg quiz.jpg picks.jpg>
# Raw screenshots are NOT kept in the repo (the picks photo shows real people before blurring).
import pathlib
import sys

from PIL import Image, ImageDraw, ImageFilter

SRC = sys.argv[1].rstrip("/") + "/"
OUT = str(pathlib.Path(__file__).resolve().parents[2] / "img") + "/"
STATUS, NAV_TOP = 70, 1520


def clean(path):
    im = Image.open(SRC + path).convert("RGB")
    row = im.crop((0, STATUS + 2, im.width, STATUS + 3))
    for y in range(STATUS + 2):           # paint the status bar with the colours just below it
        im.paste(row, (0, y))
    return im.crop((0, 0, im.width, NAV_TOP))


def rounded_mask(size, box, radius):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).rounded_rectangle(box, radius, fill=255)
    return m


welcome = clean("welcome.jpg")
looking = clean("looking-for.jpg")
quiz = clean("quiz.jpg")
picks = clean("picks.jpg")

# Quiz screen: a "Screenshot saved" toast covers the bottom bar. Both screens show the same
# Profile tab, Save button and bar, so take those rows from the "looking for" screenshot.
quiz.paste(looking.crop((0, 1262, 720, NAV_TOP)), (0, 1262))

# Picks screen: blur the photo (strangers' faces), keep the match badge and the name sharp.
photo = (27, 224, 693, 1056)
blurred = picks.filter(ImageFilter.GaussianBlur(22))
mask = rounded_mask(picks.size, photo, 40)                  # white = use the blurred pixels
d = ImageDraw.Draw(mask)
d.rounded_rectangle((505, 243, 673, 298), 27, fill=0)       # "35% match" badge stays sharp
d.rectangle((27, 940, 693, 1056), fill=0)                   # name + place stay sharp
for i, y in enumerate(range(880, 940)):                     # 60 px soft fade into the sharp part
    d.line((27, y, 693, y), fill=int(255 * (1 - i / 60)))
picks = Image.composite(blurred, picks, mask)

for name, im in [("app-welcome", welcome), ("app-looking-for", looking), ("app-quiz", quiz), ("app-picks", picks)]:
    im.save(OUT + name + ".webp", "WEBP", quality=82, method=6)
    print(name, im.size)
