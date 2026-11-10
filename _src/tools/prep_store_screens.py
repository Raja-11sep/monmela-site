# Turns raw phone screenshots (1080 × 2400) into:
#   - Play Store screenshots: 1080 × 1920 (9:16), teal background, caption on top, screen below
#   - website phone screens:  720 × 1520 (same size as the existing img/app-*.webp)
# Privacy: every real person's name, photo, place and chat text is blurred. Raw screenshots are
# NOT kept in the repo because they show real people.
# Usage: python3 _src/tools/prep_store_screens.py <raw folder> <fonts folder> <play output folder>
import pathlib
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

RAW, FONTS, PLAY_OUT = (pathlib.Path(a) for a in sys.argv[1:4])
WEB_OUT = pathlib.Path(__file__).resolve().parents[2] / "img"
STATUS, NAV = 120, 2280  # status bar ends / navigation bar starts (1080 × 2400 phone)

TEAL, TEAL_DARK, CREAM, MARIGOLD = "#12766C", "#0B5A52", "#FAF7F2", "#F2B230"


def load(name):
    return Image.open(RAW / f"{name}.png").convert("RGB")


def blur(im, boxes, circles=(), radius=18, strength=28):
    """Blur rounded boxes and round avatars (x1, y1, x2, y2). strength 28 hides faces and text."""
    blurred = im.filter(ImageFilter.GaussianBlur(strength))
    mask = Image.new("L", im.size, 0)
    d = ImageDraw.Draw(mask)
    for b in boxes:
        d.rounded_rectangle(b, radius, fill=255)
    for c in circles:
        d.ellipse(c, fill=255)
    # Blur inside each avatar only, then put the circle back on the page colour so it stays round.
    out = Image.composite(blurred, im, mask)
    for c in circles:
        inner = im.crop(c).filter(ImageFilter.GaussianBlur(strength // 2))
        circle = Image.new("L", inner.size, 0)
        ImageDraw.Draw(circle).ellipse((0, 0, inner.width - 1, inner.height - 1), fill=255)
        bg = Image.new("RGB", inner.size, im.getpixel((c[0] - 6, c[1] + 2)))
        out.paste(Image.composite(inner, bg, circle), c[:2])
    return out


def blur_except(im, area, keep, radius=40, strength=34):
    """Blur a whole photo area but keep small parts (badges, buttons) sharp."""
    blurred = im.filter(ImageFilter.GaussianBlur(strength))
    mask = Image.new("L", im.size, 0)
    d = ImageDraw.Draw(mask)
    d.rounded_rectangle(area, radius, fill=255)
    for k in keep:
        d.rounded_rectangle(k, 40, fill=0)
    return Image.composite(blurred, im, mask)


def remove_band(im, top, bottom, filler_y):
    """Cut rows top..bottom out of the scrolling area and close the gap (fills the end with a blank row)."""
    out = im.copy()
    content_end = 1876  # just above the divider line of the fixed "Save changes" bar
    out.paste(im.crop((0, bottom, im.width, content_end)), (0, top))
    row = im.crop((0, filler_y, im.width, filler_y + 1))
    for y in range(content_end - (bottom - top), content_end):
        out.paste(row, (0, y))
    return out


# ---------------------------------------------------------------- privacy edits
screens = {}

# Today's picks: photo, name and place blurred; match % and the "why you match" chips stay.
im = load("picks")
screens["picks"] = blur_except(im, (40, 360, 1040, 1610), keep=[(758, 388, 1012, 472), (68, 388, 172, 492)])

# Filter sheet: blur the photo behind the sheet.
im = load("filters")
screens["filters"] = blur_except(im, (40, 335, 1040, 1150), keep=[(758, 363, 1012, 447), (68, 363, 172, 467)])

# Requests: photo, name, age, place and the message.
im = load("requests")
screens["requests"] = blur(im, [(236, 460, 482, 520), (236, 515, 710, 562), (92, 625, 260, 690)],
                           circles=[(70, 435, 210, 575)])

# Chats: photos, names and last messages (dates stay).
im = load("chats")
boxes, circles = [], []
for top, name_right in [(300, 316), (500, 364), (700, 394)]:
    circles.append((50, top, 180, top + 130))
    boxes += [(214, top + 12, name_right, top + 66), (214, top + 68, 905, top + 122)]
screens["chats"] = blur(im, boxes, circles)

# Looking for + languages: nothing personal.
screens["looking"] = load("looking-for")

# Photo verification: nothing personal on this screen.
screens["verify"] = load("verify")

# Safety + Account: hide the admin-only "Review verifications" row.
screens["safety"] = remove_band(load("safety"), 610, 750, filler_y=1860)


# ---------------------------------------------------------------- website (720 × 1520)
def web(im):
    out = im.copy()
    row = im.crop((0, STATUS + 2, im.width, STATUS + 3))
    for y in range(STATUS + 2):  # clean status bar: paint it with the colour just below
        out.paste(row, (0, y))
    return out.crop((0, 0, im.width, NAV)).resize((720, 1520), Image.LANCZOS)


for key, file in [("looking", "app-looking-for"), ("picks", "app-picks")]:
    web(screens[key]).save(WEB_OUT / f"{file}.webp", "WEBP", quality=82, method=6)


# ---------------------------------------------------------------- Play Store (1080 × 1920)
title_font = ImageFont.truetype(str(FONTS / "PlayfairDisplay-Bold.ttf"), 78)
sub_font = ImageFont.truetype(str(FONTS / "PlusJakartaSans-Medium.ttf"), 38)

PLAY = [  # order = order on the store listing; the first three matter most
    ("picks", "Meet people who get you", "New picks every morning, with your match %"),
    ("verify", "Get photo verified", "One quick selfie earns your verified badge"),
    ("requests", "Say hello first", "Send a friend request with a short note"),
    ("chats", "Chat once you're both in", "Only friends can message you"),
    ("looking", "Adda, study, food & more", "Pick what you want friends for"),
    ("filters", "You choose who you see", "Age range, and same-gender-only if you like"),
    ("safety", "Safe by design", "Verified badge, block and pause anytime"),
]


def play_shot(screen, title, sub):
    canvas = Image.new("RGB", (1080, 1920), TEAL)
    # Soft vertical gradient: lighter teal at top → darker at the bottom.
    grad = Image.linear_gradient("L").resize((1080, 1920))
    canvas = Image.composite(Image.new("RGB", canvas.size, TEAL_DARK), canvas, grad)
    d = ImageDraw.Draw(canvas)
    d.text((540, 150), title, font=title_font, fill=CREAM, anchor="mm")
    d.rounded_rectangle((500, 212, 580, 220), 4, fill=MARIGOLD)  # small marigold accent
    d.text((540, 280), sub, font=sub_font, fill="#CFE7E2", anchor="mm")

    # The phone screen: status and nav bars cropped, scaled to 800 px wide, bleeding off the bottom.
    body = screen.crop((0, STATUS, 1080, NAV)).resize((800, 1600), Image.LANCZOS)
    x, y = 140, 380
    shadow = Image.new("L", canvas.size, 0)
    ImageDraw.Draw(shadow).rounded_rectangle((x - 6, y + 10, x + 806, y + 1640), 48, fill=110)
    canvas.paste(Image.new("RGB", canvas.size, "#06302C"), mask=shadow.filter(ImageFilter.GaussianBlur(24)))
    frame = Image.new("L", body.size, 0)
    ImageDraw.Draw(frame).rounded_rectangle((0, 0, 799, 1640), 44, fill=255)
    canvas.paste(body, (x, y), frame)
    return canvas


PLAY_OUT.mkdir(parents=True, exist_ok=True)
for i, (key, title, sub) in enumerate(PLAY, 1):
    play_shot(screens[key], title, sub).save(PLAY_OUT / f"{i}-{key}.png", optimize=True)
    print("play", i, key)
