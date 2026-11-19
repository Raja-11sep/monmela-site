# Draws the four app screens shown in "How it works" in the app's new look ("Mela at dusk").
# They are designs, not screenshots: the app gets this look before the Play Store release.
# Once it has it, real screenshots can replace these (tools/prep_screens.py).
#   pip install playwright && playwright install chromium
#   python3 _src/tools/make_app_screens.py [photo.jpg]
# Writes img/app-welcome.webp, app-looking-for.webp, app-quiz.webp, app-picks.webp (720 x 1520).
# photo.jpg (optional): the portrait for "Riti" on Today's picks. It is cropped and its face softly
# blurred into _src/tools/picks-photo.webp; only that blurred copy is kept, never the original.
import base64
import pathlib
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageOps
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[2]
PHOTO = pathlib.Path(__file__).with_name("picks-photo.webp")

# Where to crop the portrait (left, top, right, bottom) and where the face is, in the original photo's pixels.
# Tuned for the photo used now; change them for a different photo.
CROP = (180, 450, 1480, 1535)
FACE = (630, 620, 1030, 1080)
# Blur strong enough that people who know the photo can't place it, while it still reads as
# a young woman: the face is a soft shape, the dress, flowers and wall turn to colour, and the
# picture is mirrored.
PHOTO_BLUR = 10         # px in the original photo, the whole picture
FACE_BLUR = 30          # px in the original photo, the face on top of that

# The app's dusk palette (same as the website's dark sections)
BG, DEEP, INK, MUTED, GOLD = "#0A3532", "#072B28", "#FFF6E5", "#B9D6CF", "#F5B023"
LINE, GLASS, DARK = "rgba(255,246,229,.14)", "rgba(255,246,229,.07)", "#1C2626"
D = "'Anek Bangla', 'Hind Siliguri', sans-serif"   # headings
B = "'Hind Siliguri', sans-serif"                  # body text

def font(name):
    """A font file from fonts/ as a data: URL (the page is drawn from a string, so it can't load files)."""
    return "data:font/woff2;base64," + base64.b64encode((ROOT / "fonts" / name).read_bytes()).decode()


CSS = f"""
@font-face {{ font-family: 'Anek Bangla'; font-weight: 500 800; src: url({font('anek-bangla-latin.woff2')}); unicode-range: U+0000-00FF, U+2000-206F; }}
@font-face {{ font-family: 'Anek Bangla'; font-weight: 500 800; src: url({font('anek-bangla-bengali.woff2')}); unicode-range: U+0980-09FF, U+200C-200D, U+0964-0965; }}
@font-face {{ font-family: 'Hind Siliguri'; font-weight: 400; src: url({font('hind-siliguri-latin-400.woff2')}); unicode-range: U+0000-00FF, U+2000-206F; }}
@font-face {{ font-family: 'Hind Siliguri'; font-weight: 600; src: url({font('hind-siliguri-latin-600.woff2')}); unicode-range: U+0000-00FF, U+2000-206F; }}
@font-face {{ font-family: 'Hind Siliguri'; font-weight: 400; src: url({font('hind-siliguri-bengali-400.woff2')}); unicode-range: U+0980-09FF, U+0964-0965; }}
@font-face {{ font-family: 'Hind Siliguri'; font-weight: 600; src: url({font('hind-siliguri-bengali-600.woff2')}); unicode-range: U+0980-09FF, U+0964-0965; }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; }}
/* padding-top: room for the phone's status bar and camera (the website's phone frame draws the camera) */
.s {{ position: relative; width: 360px; height: 760px; padding-top: 38px; overflow: hidden; background: {BG}; color: {INK}; font-family: {B}; }}
p, h1, h2 {{ margin: 0; }}
.btn {{ display: flex; align-items: center; justify-content: center; gap: 8px; height: 50px; border-radius: 999px; font: 700 16px {B}; }}
.gold {{ background: {GOLD}; color: {DARK}; }}
.glass {{ background: {GLASS}; box-shadow: inset 0 0 0 1px {LINE}; }}
"""

ICONS = {  # 24 x 24 outline icons
    "people": '<circle cx="9" cy="8" r="3.2"/><path d="M3.5 19c.6-3.4 2.9-5.2 5.5-5.2s4.9 1.8 5.5 5.2"/><circle cx="17" cy="9" r="2.4"/><path d="M15.5 13.8c2.3.1 4.2 1.7 4.8 4.6"/>',
    "cup": '<path d="M5 9h11v4a5 5 0 0 1-5 5h-1a5 5 0 0 1-5-5z"/><path d="M16 10.5h1.2a2.3 2.3 0 0 1 0 4.6H16"/><path d="M8.5 3.5c0 1 1 1.4 1 2.4M12.5 3.5c0 1 1 1.4 1 2.4"/>',
    "inbox": '<path d="M4 13l2.5-7h11L20 13v5H4z"/><path d="M4 13h4.5l1 2h5l1-2H20"/>',
    "chat": '<path d="M5 6h14v9H9l-4 3z"/>',
    "me": '<circle cx="12" cy="8" r="3.6"/><path d="M5 20c.8-4 3.6-6 7-6s6.2 2 7 6"/>',
    "wave": '<path d="M8 13V6.5a1.5 1.5 0 0 1 3 0V12M11 11V5a1.5 1.5 0 0 1 3 0v6M14 11V6.5a1.5 1.5 0 0 1 3 0V14a6 6 0 0 1-6 6h-.5a6 6 0 0 1-4.6-2.2L4 15.5a1.5 1.5 0 0 1 2.3-1.9L8 15"/>',
    "badge": '<circle cx="12" cy="12" r="9"/><path d="M8 12.3l2.6 2.5L16 9.5"/>',
    "pin": '<path d="M12 21s-6-5.5-6-11a6 6 0 0 1 12 0c0 5.5-6 11-6 11z"/><circle cx="12" cy="10" r="2.2"/>',
    "sliders": '<path d="M4 7h10M18 7h2M4 17h2M10 17h10"/><circle cx="16" cy="7" r="2"/><circle cx="8" cy="17" r="2"/>',
    "back": '<path d="M15 5l-7 7 7 7"/>',
    "check": '<path d="M5 12.5l4.5 4.5L19 7.5"/>',
    "lock": '<rect x="5" y="10.5" width="14" height="10" rx="2.5"/><path d="M8.5 10.5V8a3.5 3.5 0 0 1 7 0v2.5"/>',
    "book": '<path d="M4 5.5c3-1 5.5-.8 8 1 2.5-1.8 5-2 8-1V19c-3-1-5.5-.8-8 1-2.5-1.8-5-2-8-1z"/><path d="M12 6.5V20"/>',
    "ball": '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5l4 3-1.5 4.5h-5L8 10.5z"/>',
    "food": '<path d="M7 3.5v7a2 2 0 0 0 2 2h0a2 2 0 0 0 2-2v-7M9 12.5V21M16.5 21V3.5c-2 1-3 3.5-3 7h3"/>',
    "hike": '<path d="M3.5 19l5.5-9 3.5 5 2.5-3.5 5.5 7.5z"/>',
    "music": '<path d="M9 18V6l10-2v12"/><circle cx="6.5" cy="18" r="2.5"/><circle cx="16.5" cy="16" r="2.5"/>',
    "film": '<rect x="4" y="5" width="16" height="14" rx="2.5"/><path d="M8 5v14M16 5v14M4 12h16"/>',
    "work": '<rect x="4" y="7.5" width="16" height="11.5" rx="2.5"/><path d="M9 7.5V6a1.5 1.5 0 0 1 1.5-1.5h3A1.5 1.5 0 0 1 15 6v1.5M4 12.5h16"/>',
    "lamp": '<path d="M12 3c-3 3.5-4.5 6-4.5 8.5a4.5 4.5 0 0 0 9 0C16.5 9 15 6.5 12 3z"/><path d="M8.5 20.5h7"/>',
}


def ic(name, size=20, color="currentColor", sw=1.8):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="{sw}" '
            f'stroke-linecap="round" stroke-linejoin="round" style="flex: none">{ICONS[name]}</svg>')


def festoon():
    """A string of mela lights along the top of the screen."""
    colours = ["#F5B023", "#FFE7B3", "#E2553A", "#7FD8CC"] * 4
    ys = [6 + 14 * ((i % 5) - 2) ** 2 / 4 for i in range(15)]
    glows = "".join(f'<circle cx="{12 + i * 24}" cy="{y + 3:.1f}" r="8" fill="#F5B023" opacity=".14"/>' for i, y in enumerate(ys))
    bulbs = "".join(f'<circle cx="{12 + i * 24}" cy="{y + 3:.1f}" r="3.8" fill="{colours[i]}"/>' for i, y in enumerate(ys))
    wire = " ".join(f"Q {12 + i * 24 - 12} {ys[i] + 12:.1f} {12 + i * 24} {ys[i]:.1f}" for i in range(1, 15))
    return (f'<svg width="360" height="30" viewBox="0 0 360 30" style="display: block">'
            f'<path d="M 12 {ys[0]:.1f} {wire}" fill="none" stroke="rgba(255,246,229,.25)" stroke-width="1.2"/>{glows}{bulbs}</svg>')


def logo(size):
    """The Mon Mela mark: two rings, marigold where they meet."""
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 48 48"><circle cx="24" cy="24" r="24" fill="{INK}"/>'
            '<circle cx="19" cy="24" r="9" fill="none" stroke="#0F766E" stroke-width="3.2"/>'
            '<circle cx="29" cy="24" r="9" fill="none" stroke="#0F766E" stroke-width="3.2"/>'
            f'<path d="M24 16.6a9 9 0 0 1 0 14.8a9 9 0 0 1 0-14.8z" fill="{GOLD}"/></svg>')


def make_photo(src):
    """Crop the portrait for the picks card: blur it all, blur the face more (feathered oval, so no
    hard edge), and mirror it."""
    im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).ellipse(FACE, fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(50))          # feather the oval's edge
    soft = im.filter(ImageFilter.GaussianBlur(PHOTO_BLUR))
    im = Image.composite(im.filter(ImageFilter.GaussianBlur(FACE_BLUR)), soft, mask)
    im = ImageOps.mirror(im.crop(CROP)).resize((628, 524), Image.LANCZOS)   # 2x the card's photo area (314 x 262)
    im.save(PHOTO, "WEBP", quality=84, method=6)
    print("wrote", PHOTO.name)


def riti():
    """Riti's photo on the picks card (from picks-photo.webp, made by make_photo)."""
    data = base64.b64encode(PHOTO.read_bytes()).decode()
    return f'<img src="data:image/webp;base64,{data}" alt="" style="display: block; width: 100%; height: 100%; object-fit: cover">'


def riti_drawn():
    """Riti, illustrated (no real people): kept for the design canvas; the website now uses a photo."""
    return """<svg viewBox="0 0 300 340" preserveAspectRatio="xMidYMid slice" style="display: block; width: 100%; height: 100%">
<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#6E5A8A"/><stop offset=".6" stop-color="#E39A5B"/><stop offset="1" stop-color="#F4CB8E"/></linearGradient></defs>
<rect width="300" height="340" fill="url(#sky)"/>
<path d="M0 238 L60 200 L60 238 M60 200 L120 238 M180 238 L240 200 L240 238 M240 200 L300 238" stroke="#4E3A57" stroke-width="3" fill="none" opacity=".45"/>
<path d="M0 238 H300" stroke="#4E3A57" stroke-width="4" opacity=".5"/>
<circle cx="150" cy="58" r="27" fill="#1D1414"/><circle cx="150" cy="122" r="63" fill="#1D1414"/>
<ellipse cx="150" cy="142" rx="50" ry="58" fill="#9A6340"/>
<path d="M99 132 C101 90 131 76 150 76 C170 76 199 90 201 132 C187 106 168 98 150 98 C132 98 113 106 99 132 Z" fill="#1D1414"/>
<circle cx="150" cy="116" r="4.5" fill="#C8321E"/>
<path d="M125 142 q8 6 16 0 M159 142 q8 6 16 0" stroke="#2A1810" stroke-width="3.2" fill="none" stroke-linecap="round"/>
<path d="M135 170 q15 12 30 0" stroke="#2A1810" stroke-width="3.2" fill="none" stroke-linecap="round"/>
<circle cx="99" cy="162" r="5.5" fill="#F5B023"/><circle cx="201" cy="162" r="5.5" fill="#F5B023"/>
<rect x="134" y="190" width="32" height="30" fill="#8A5636"/>
<path d="M56 340 C62 266 102 222 150 218 C198 222 238 266 244 340 Z" fill="#F6EBD9"/>
<path d="M98 236 C142 262 172 298 188 340 L160 340 C148 306 124 276 84 252 Z" fill="#C8321E"/></svg>"""


def ring(pct, size):
    c = 2 * 3.14159 * 26
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 64 64" style="flex: none">'
            f'<circle cx="32" cy="32" r="26" fill="none" stroke="rgba(255,246,229,.18)" stroke-width="6"/>'
            f'<circle cx="32" cy="32" r="26" fill="none" stroke="{GOLD}" stroke-width="6" stroke-linecap="round" '
            f'stroke-dasharray="{c * pct / 100:.1f} {c:.1f}" transform="rotate(-90 32 32)"/>'
            f'<text x="32" y="37.5" text-anchor="middle" style="font: 700 16px {D}; fill: {INK}">{pct}%</text></svg>')


def bridge():
    """Howrah Bridge in thin lines, low at the back of the welcome screen."""
    return f"""<svg width="360" height="150" viewBox="0 0 360 150" style="position: absolute; left: 0; bottom: 0; opacity: .22" fill="none" stroke="{MUTED}" stroke-width="1.6">
<path d="M0 120 H360"/><path d="M40 120 V30 M70 120 V30 M290 120 V30 M320 120 V30"/>
<path d="M40 30 H70 M290 30 H320 M40 52 L70 30 M40 30 L70 52 M290 52 L320 30 M290 30 L320 52"/>
<path d="M70 34 C130 80 230 80 290 34"/><path d="M0 70 C14 80 28 90 40 96 M320 96 C332 90 346 80 360 70"/>
<path d="M100 120 V60 M130 120 V72 M160 120 V77 M200 120 V77 M230 120 V72 M260 120 V60"/>
<path d="M0 134 C60 128 120 140 180 134 S300 128 360 134" stroke-opacity=".7"/></svg>"""


def progress(step, total):
    bars = "".join(f'<span style="flex: 1; height: 4px; border-radius: 4px; background: {GOLD if i < step else LINE}"></span>' for i in range(total))
    return f'<div style="display: flex; gap: 6px">{bars}</div>'


def welcome():
    return f"""<div class="s">
{festoon()}{bridge()}
<div style="display: flex; flex-direction: column; align-items: center; gap: 12px; padding-top: 86px; text-align: center">
{logo(76)}
<h1 style="font: 800 46px/1.15 {D}; color: {INK}">মনমেলা</h1>
<p style="font: 600 17px {D}; color: {GOLD}">মন মিললে, বন্ধু মেলে।</p>
</div>
<div class="glass" style="position: absolute; left: 18px; right: 18px; top: 378px; padding: 22px 20px 18px; border-radius: 26px; background: rgba(7,43,40,.75); text-align: center">
<h2 style="font: 700 22px/1.25 {D}; text-wrap: balance">Make friends who get you</h2>
<p style="margin: 8px 0 18px; font-size: 14.5px; line-height: 1.5; color: {MUTED}">Meet people near you who share your interests: adda, study, sports, travel and more.</p>
<div class="btn gold"><span style="display: grid; place-items: center; width: 26px; height: 26px; border-radius: 50%; background: #fff; font: 700 15px {B}; color: #0F766E">G</span>Continue with Google</div>
<p style="margin-top: 12px; font-size: 12px; color: {MUTED}">By continuing, you agree to our Terms and Privacy Policy.</p>
</div>
<p style="position: absolute; left: 0; right: 0; bottom: 26px; text-align: center; font-size: 13px; color: {MUTED}">18+ only. Made in Kolkata.</p>
</div>"""


def looking_for():
    options = [("cup", "Adda", True), ("book", "Study partner", False), ("ball", "Gym / sports", False),
               ("food", "Foodie", True), ("hike", "Travel / trekking", False), ("music", "Music, art and culture", False),
               ("film", "Books / movies", True), ("work", "Career networking", False), ("lamp", "Puja and festival gang", True)]
    chips = "".join(
        f'<span style="display: flex; align-items: center; gap: 7px; height: 42px; padding: 0 15px; border-radius: 999px; font: 600 14.5px {B}; '
        + (f'background: {GOLD}; color: {DARK}">{ic("check", 18, DARK, 2.4)}' if on else f'background: {GLASS}; color: {INK}; box-shadow: inset 0 0 0 1px {LINE}">{ic(i, 18, MUTED)}')
        + f'{label}</span>'
        for i, label, on in options)
    return f"""<div class="s">
{festoon()}
<div style="padding: 14px 20px 0">
{progress(2, 4)}
<p style="margin-top: 22px; font: 600 14px {D}; color: {GOLD}">কী খুঁজছেন?</p>
<h1 style="margin-top: 2px; font: 700 28px/1.2 {D}">Looking for friends for</h1>
<p style="margin-top: 6px; font-size: 14.5px; line-height: 1.5; color: {MUTED}">Pick up to 5. We suggest people who want the same.</p>
<div style="display: flex; flex-wrap: wrap; gap: 9px; margin-top: 22px">{chips}</div>
</div>
<div style="position: absolute; left: 20px; right: 20px; bottom: 24px">
<p style="margin-bottom: 12px; text-align: center; font: 600 13.5px {B}; color: {MUTED}">4 of 5 picked</p>
<div class="btn gold">Continue</div>
</div>
</div>"""


def quiz():
    options = ["Pandal hopping all night", "A few famous pandals", "Para puja with family", "Escape the crowds"]
    rows = "".join(
        f'<div style="display: flex; align-items: center; gap: 12px; min-height: 54px; padding: 0 16px; border-radius: 18px; font: 600 15.5px {B}; '
        + (f'background: rgba(245,176,35,.14); box-shadow: inset 0 0 0 2px {GOLD}">'
           f'<span style="display: grid; place-items: center; width: 22px; height: 22px; border-radius: 50%; background: {GOLD}">{ic("check", 14, DARK, 3)}</span>'
           if i == 0 else
           f'background: {GLASS}; box-shadow: inset 0 0 0 1px {LINE}"><span style="width: 22px; height: 22px; border-radius: 50%; box-shadow: inset 0 0 0 2px {MUTED}"></span>')
        + f'{o}</div>'
        for i, o in enumerate(options))
    levels = ["Not important", "A little", "Somewhat", "Very important"]
    pills = "".join(
        f'<span style="display: grid; place-items: center; height: 40px; border-radius: 999px; font: 600 13.5px {B}; '
        + (f'background: {INK}; color: {BG}' if lv == "Very important" else f'background: {GLASS}; color: {INK}; box-shadow: inset 0 0 0 1px {LINE}')
        + f'">{lv}</span>'
        for lv in levels)
    return f"""<div class="s">
<div style="display: flex; align-items: center; gap: 8px; padding: 14px 12px 0 6px">
<span style="display: grid; place-items: center; width: 40px; height: 40px">{ic("back", 22, INK)}</span>
<div style="flex: 1">{progress(9, 12)}</div>
<span style="width: 52px; text-align: right; font: 600 13.5px {B}; color: {MUTED}">9 of 12</span>
</div>
<div style="padding: 20px 20px 0">
<p style="font: 600 14px {D}; color: {GOLD}">বাংলা · Bengal</p>
<h1 style="margin-top: 4px; font: 700 29px/1.2 {D}">Your Durga Puja style?</h1>
<div style="display: flex; flex-direction: column; gap: 10px; margin-top: 20px">{rows}</div>
<p style="margin-top: 24px; font: 600 15px {B}">How important is this to you?</p>
<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 10px">{pills}</div>
</div>
<div style="position: absolute; left: 20px; right: 20px; bottom: 24px">
<p style="display: flex; align-items: center; justify-content: center; gap: 6px; margin-bottom: 12px; font-size: 13px; color: {MUTED}">{ic("lock", 16, MUTED)}Answers stay private. They only make your match %.</p>
<div class="btn gold">Next question</div>
</div>
</div>"""


def picks():
    chips = "".join(f'<span style="padding: 4px 11px; border-radius: 999px; background: rgba(245,176,35,.14); color: #FFE7B3; font: 600 13px {B}">{t}</span>'
                    for t in ["Prinsep Ghat", "Durga Puja", "Mishti doi", "Feluda"])
    tabs = [("people", "Picks"), ("cup", "Adda"), ("inbox", "Requests"), ("chat", "Chats"), ("me", "Me")]
    nav = "".join(
        (f'<span style="display: flex; align-items: center; gap: 6px; height: 42px; padding: 0 14px; border-radius: 999px; background: {GOLD}; color: {DARK}; font: 700 14px {B}">{ic(i, 19, DARK, 2)}{t}</span>'
         if t == "Picks" else f'<span style="display: grid; place-items: center; width: 42px; height: 42px; color: {MUTED}">{ic(i, 21)}</span>')
        for i, t in tabs)
    return f"""<div class="s">
{festoon()}
<div style="display: flex; justify-content: space-between; align-items: flex-end; padding: 12px 18px 0">
<div><p style="font: 600 14px {D}; color: {GOLD}">শুভ সন্ধ্যা, অর্জুন</p><h1 style="font: 700 27px/1.15 {D}">Today's picks</h1></div>
<span class="glass" style="display: grid; place-items: center; width: 40px; height: 40px; border-radius: 50%">{ic("sliders", 19, INK)}</span>
</div>
<p style="margin: 5px 18px 12px; font-size: 13.5px; color: {MUTED}">4 people picked for you. New picks every morning.</p>
<div class="glass" style="margin: 0 14px; padding: 9px; border-radius: 26px">
<div style="position: relative; height: 262px; border-radius: 19px; overflow: hidden">{riti()}
<div style="position: absolute; top: 10px; right: 10px; display: flex; align-items: center; gap: 5px; padding: 4px 11px 4px 4px; border-radius: 999px; background: rgba(7,43,40,.82)">{ring(86, 38)}<span style="font: 600 12.5px {B}">match</span></div>
<div style="position: absolute; left: 0; right: 0; bottom: 0; padding: 34px 14px 12px; background: linear-gradient(180deg, rgba(7,43,40,0), rgba(7,43,40,.9))">
<div style="display: flex; align-items: center; gap: 7px"><h2 style="font: 700 24px/1.1 {D}">Riti, 24</h2>{ic("badge", 20, GOLD, 2)}</div>
<p style="display: flex; align-items: center; gap: 4px; margin-top: 3px; font-size: 13.5px; color: #E4F1EE">{ic("pin", 15)}Howrah</p>
</div></div>
<div style="padding: 12px 6px 4px">
<p style="margin-bottom: 7px; font-size: 13px; color: {MUTED}">Where your minds meet</p>
<div style="display: flex; flex-wrap: wrap; gap: 6px">{chips}</div>
<div style="display: flex; gap: 9px; margin-top: 14px">
<div class="btn glass" style="height: 46px; padding: 0 18px; font: 600 15px {B}">{ic("wave", 19)}Wave</div>
<div class="btn gold" style="flex: 1; height: 46px">Say hello</div>
</div></div></div>
<div style="position: absolute; left: 14px; right: 14px; bottom: 14px; display: flex; justify-content: space-between; align-items: center; padding: 7px; border-radius: 999px; background: rgba(7,43,40,.94); box-shadow: inset 0 0 0 1px {LINE}">{nav}</div>
</div>"""


SCREENS = {"app-welcome": welcome, "app-looking-for": looking_for, "app-quiz": quiz, "app-picks": picks}

if __name__ == "__main__":
    if len(sys.argv) > 1:
        make_photo(sys.argv[1])
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 360, "height": 760}, device_scale_factor=2)
        for name, draw in SCREENS.items():
            page.set_content(f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{draw()}</body></html>")
            page.evaluate("document.fonts.ready")
            page.wait_for_timeout(300)
            png = ROOT / f"img/{name}.png"
            page.screenshot(path=str(png), clip={"x": 0, "y": 0, "width": 360, "height": 760})
            Image.open(png).convert("RGB").save(ROOT / f"img/{name}.webp", "WEBP", quality=86, method=6)
            png.unlink()
            print("wrote", f"img/{name}.webp")
        browser.close()
