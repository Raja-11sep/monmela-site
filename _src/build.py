# Builds the monmela.in website so every page shares the same header, footer and styles.
# Usage (from the site folder): python3 _src/build.py      needs: pip install qrcode
#   - Home and download pages: written here, bilingual piece by piece.
#   - Legal pages: _src/pages/<name>.en.html + <name>.bn.html inside the standard card layout.
#   - _src/ is not published: GitHub Pages (Jekyll) skips folders that start with "_".
import datetime
from html import escape as html_escape
import hashlib
import json
import pathlib
import re

from art import LOGO, alpana_tile, festoon, hero_art

ROOT = pathlib.Path(__file__).resolve().parent.parent      # the site folder (built files go here)
PAGES = pathlib.Path(__file__).resolve().parent / "pages"  # legal page bodies
SITE = "https://monmela.in"
# Being retired: the pages stay online (Play Store privacy / delete-account links, testers'
# download link) but ask Google to drop them from search (a "noindex" tag on every page).
NOINDEX = True
UPDATED_EN = "11 November 2026"
UPDATED_BN = "১১ নভেম্বর ২০২৬"
EMAIL = "monmela.team@gmail.com"

# Android app download (monmela.in/download).
# APK_FILE: the Play-signed universal APK, uploaded to the site repo at this path.
# PLAY_URL: set at public launch, e.g. "https://play.google.com/store/apps/details?id=<package>".
#   Then every download button goes to Google Play and /download redirects there (APK no longer offered).
APK_FILE = "app/mon-mela.apk"
PLAY_URL = ""
# Closed test (until launch): the site is for testers only, so every download button opens the
# app's Google Play page straight away (testers are already in; no group / "become a tester"
# steps). The APK stays on /download under "Can't use Google Play?".
# Empty it to go back to the two-step tester flow below (TEST_GROUP_URL + TEST_JOIN_URL).
TEST_PLAY_URL = "https://play.google.com/store/apps/details?id=com.monmela.app"
# Two-step tester flow, used only while TEST_PLAY_URL is empty: join the group, then become a tester.
# Empty both to hide the Google Play steps and offer only the APK.
TEST_GROUP_URL = "https://groups.google.com/g/mon-mela-testers"
TEST_JOIN_URL = "https://play.google.com/apps/testing/com.monmela.app"

# Shared adda links open the app (Android App Links). APP_SHA256: the app signing key and the
# upload key fingerprints from Play Console → Test and release → App integrity → App signing.
# Public values, not secrets. Empty = no assetlinks.json (links then open this site's adda page).
APP_ID = "com.monmela.app"
APP_SHA256 = []

# Our social pages: linked in the footer and listed in the structured data ("sameAs"),
# which tells Google these pages belong to the same Mon Mela.
INSTAGRAM_URL = "https://www.instagram.com/monmela.in/"
FACEBOOK_URL = "https://www.facebook.com/profile.php?id=61596312788249"


NAV = [
    ("./", "Home", "হোম"),
    ("terms.html", "Terms", "শর্তাবলি"),
    ("privacy.html", "Privacy", "প্রাইভেসি"),
    ("delete-account.html", "Delete account", "অ্যাকাউন্ট মুছুন"),
    ("child-safety.html", "Child safety", "শিশু সুরক্ষা"),
    ("download.html", "Download app", "অ্যাপ ডাউনলোড"),
]


def bn_num(n):
    """A number in Bengali digits, e.g. 4 -> ৪."""
    return str(n).translate(str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯"))


def both(en: str, bn: str, tag: str = "span", cls: str = "") -> str:
    """The same text in both languages; site.js shows only the chosen one."""
    c = f"l {cls}".strip()
    return f'<{tag} class="{c}" lang="en">{en}</{tag}><{tag} class="{c}" lang="bn">{bn}</{tag}>'


def asset(name):
    """URL of a local file with a short content hash, e.g. style.css?v=3f2a91c0."""
    return f"{name}?v={hashlib.sha1((ROOT / name).read_bytes()).hexdigest()[:8]}"


def script(name):
    return f'<script src="{asset(name)}" defer></script>'


def head(title_en, title_bn, description, path="", extra=""):
    return f"""<!doctype html>
<html lang="en" data-lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title_en}</title>
<meta name="title-en" content="{title_en}">
<meta name="title-bn" content="{title_bn}">
<meta name="description" content="{description}">
{'<meta name="robots" content="noindex, nofollow">' + chr(10) if NOINDEX else ""}<meta name="theme-color" content="#0B3B37">
<link rel="canonical" href="{SITE}/{path}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Mon Mela">
<meta property="og:locale" content="en_IN">
<meta property="og:locale:alternate" content="bn_IN">
<meta name="twitter:card" content="summary_large_image">
<meta property="og:title" content="{title_en}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{SITE}/{path}">
<!-- ?v= changes whenever og.png changes, so WhatsApp, Facebook and X fetch the new picture (made by tools/make_og.py) -->
<meta property="og:image" content="{SITE}/{asset("og.png")}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Mon Mela: মন মিললে, বন্ধু মেলে। Friends nearby who love what you love.">
<meta name="twitter:image" content="{SITE}/{asset("og.png")}">
<link rel="icon" href="{asset("favicon.ico")}" sizes="48x48">
<link rel="icon" href="{asset("favicon.svg")}" type="image/svg+xml">
<link rel="apple-touch-icon" href="{asset("apple-touch-icon.png")}">
<link rel="manifest" href="site.webmanifest">
<link rel="preload" href="fonts/anek-bangla-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{asset("style.css")}">
<script src="{asset("site.js")}"></script>
{script("music.js")}
{extra}
</head>"""


def header(on_home=False):
    """Floating top bar on every page: logo, section links (wide screens), language switch, Download.
    On the home page the links only scroll; elsewhere they open the home page at that section."""
    prefix = "" if on_home else "./"
    links = '<nav class="top-nav" aria-label="Sections">' + "".join(
        f'<a href="{prefix}#{anchor}">{both(en, bn)}</a>'
        for anchor, en, bn in [("how", "How it works", "কীভাবে"), ("adda-h", "Adda Tables", "আড্ডা টেবিল"),
                               ("safe", "Safety", "নিরাপত্তা"), ("qa", "Questions", "প্রশ্ন")]) + "</nav>"
    cta = get_app_button("btn btn-primary btn-small top-cta", short=True)
    return f"""<header class="top"><div class="top-inner">
  <a class="brand" href="./">{LOGO}{both("Mon Mela", "মনমেলা")}</a>
  {links}
  <div class="top-end">
    <div class="lang-switch" role="group" aria-label="Language">
      <button type="button" data-lang="en" aria-pressed="true">English</button>
      <button type="button" data-lang="bn" aria-pressed="false">বাংলা</button>
    </div>
    {cta}
  </div>
</div></header>"""


# Simple outline icons for the social links (drawn here, so no third-party scripts load).
INSTAGRAM_ICON = ('<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="5" '
                  'fill="none" stroke="currentColor" stroke-width="2"/><circle cx="12" cy="12" r="4" fill="none" '
                  'stroke="currentColor" stroke-width="2"/><circle cx="17.5" cy="6.5" r="1.3" fill="currentColor"/></svg>')
FACEBOOK_ICON = ('<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M14 8h2.5V4.5H14c-2.5 0-4 1.6-4 4.2V11H7.5v3.5H10V21h3.5'
                 'v-6.5H16l.5-3.5h-3V9c0-.6.4-1 1-1z" fill="currentColor"/></svg>')


def social_links():
    """Instagram / Facebook as labelled buttons, with the handle under the name. rel="me" says the
    pages are ours."""
    items = [(INSTAGRAM_URL, INSTAGRAM_ICON, "Instagram", "@monmela.in"),
             (FACEBOOK_URL, FACEBOOK_ICON, "Facebook", "Mon Mela")]
    return '<div class="foot-social">' + "".join(
        f'<a href="{url}" target="_blank" rel="noopener me">{svg}<span>{name}</span><small>{handle}</small></a>'
        for url, svg, name, handle in items) + "</div>"


UP_ICON = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 19V5M6 11l6-6 6 6"/></svg>'


def footer(on_home=False):
    """Footer on every page: alpana border, brand and Download, three link groups, then the closing
    scene (mela lights over a huge, fading মনমেলা) and the copyright line with Back to top.
    The section links only scroll on the home page; elsewhere they open the home page there."""
    home = "" if on_home else "./"

    def group(title_en, title_bn, items):
        lis = "".join(f'<li><a href="{href}">{both(en, bn)}</a></li>' for href, en, bn in items)
        return f'<div class="foot-col"><h2>{both(title_en, title_bn)}</h2><ul>{lis}</ul></div>'

    explore = group("Explore", "ঘুরে দেখুন", [
        (f"{home}#how", "How it works", "কীভাবে কাজ করে"), (f"{home}#adda-h", "Adda Tables", "আড্ডা টেবিল"),
        (f"{home}#safe", "Safety", "নিরাপত্তা"), (f"{home}#qa", "Questions", "প্রশ্ন")])
    help_ = group("Help", "সাহায্য", [
        ("terms.html", "Terms", "শর্তাবলি"), ("privacy.html", "Privacy", "প্রাইভেসি"),
        ("child-safety.html", "Child safety", "শিশু সুরক্ষা"), ("delete-account.html", "Delete account", "অ্যাকাউন্ট মুছুন")])
    return f"""<footer class="site-foot">
  <div class="alpana" aria-hidden="true"></div>
  <div class="foot-inner">
    <div class="foot-brand">
      <a class="brand" href="./">{LOGO}{both("Mon Mela", "মনমেলা")}</a>
      <p>{both("Friends who think like you, across West Bengal.", "মনের মতো বন্ধু, সারা পশ্চিমবঙ্গে।")}</p>
      {get_app_button("foot-get")}
    </div>
    <nav class="foot-cols" aria-label="Footer">
      {explore}
      {help_}
      <div class="foot-col foot-write">
        <h2>{both("Write to us", "আমাদের লিখুন")}</h2>
        <a class="foot-mail" href="mailto:{EMAIL}">{EMAIL}</a>
        <p>{both("Grievance Officer: Dhritisha Palmal", "অভিযোগ আধিকারিক: Dhritisha Palmal")}</p>
        {social_links()}
      </div>
    </nav>
  </div>
  <div class="foot-night" aria-hidden="true">
    <div class="foot-lights">{festoon(swags=5, per_swag=9, width=1800)}</div>
    <p class="foot-word">মনমেলা</p>
  </div>
  <div class="foot-base">
    <p>{both("© 2026 Mon Mela. Made in West Bengal.", "© ২০২৬ মনমেলা। পশ্চিমবঙ্গে তৈরি।")}</p>
    <a class="foot-up" href="#">{UP_ICON}<span>{both("Back to top", "ওপরে যান")}</span></a>
  </div>
</footer>
{music_player()}"""


def page(file, title_en, title_bn, sub_en, sub_bn, body_en, body_bn):
    html = f"""{head(f"{title_en} · Mon Mela", f"{title_bn} · মনমেলা",
                    "Mon Mela: a Bengali-first friendship app for adults in West Bengal.", file)}
<body class="doc">
{header()}
<section class="hero"><div class="hero-inner">
  <h1>{both(title_en, title_bn)}</h1>
  <p>{both(sub_en, sub_bn)}</p>
</div></section>
<main><article class="card">
<div class="l" lang="en">
{body_en}
</div>
<div class="l" lang="bn">
{body_bn}
</div>
</article></main>
{footer()}
</body>
</html>
"""
    (ROOT / file).write_text(html, encoding="utf-8")


def load(name):
    return (PAGES / name).read_text(encoding="utf-8").replace("{EMAIL}", EMAIL) \
        .replace("{UPDATED_EN}", UPDATED_EN).replace("{UPDATED_BN}", UPDATED_BN)


# ---------------------------------------------------------------- home page

# "Matched by what you share": your answers, and the people match.js matches you with in turn
# (the figure as built shows the first). Each person: who, their six answers, the ones you share
# (3 or 4, in the order they sit in the overlap), the match %, and the caption. The hero card's
# "Why you match" shows the first person's shared answers too.
VENN_YOU = [("Prinsep Ghat", "প্রিন্সেপ ঘাট"), ("Early riser", "ভোরে ওঠা"), ("Durga Puja", "দুর্গাপুজো"),
            ("Mishti doi", "মিষ্টি দই"), ("Feluda", "ফেলুদা"), ("Puri trips", "পুরী")]
VENN_PEOPLE = [
    {"who": ("Someone in Howrah", "হাওড়ার কেউ"), "score": 86,
     "items": [("Night owl", "রাত জাগা"), ("Prinsep Ghat", "প্রিন্সেপ ঘাট"), ("Durga Puja", "দুর্গাপুজো"),
               ("Football", "ফুটবল"), ("Mishti doi", "মিষ্টি দই"), ("Feluda", "ফেলুদা")],
     "shared": ["Prinsep Ghat", "Durga Puja", "Mishti doi", "Feluda"],
     "caption": ("You both love Prinsep Ghat, Durga Puja, mishti doi and Feluda: an 86% match.",
                 "দুজনেই প্রিন্সেপ ঘাট, দুর্গাপুজো, মিষ্টি দই আর ফেলুদা ভালোবাসেন: ৮৬% মিল।")},
    {"who": ("Someone in Siliguri", "শিলিগুড়ির কেউ"), "score": 78,
     "items": [("Trekking", "ট্রেকিং"), ("Early riser", "ভোরে ওঠা"), ("Momos", "মোমো"),
               ("Feluda", "ফেলুদা"), ("Cricket", "ক্রিকেট"), ("Mishti doi", "মিষ্টি দই")],
     "shared": ["Early riser", "Feluda", "Mishti doi"],
     "caption": ("You're both early risers who love Feluda and mishti doi: a 78% match.",
                 "দুজনেই ভোরে ওঠেন, ফেলুদা আর মিষ্টি দই ভালোবাসেন: ৭৮% মিল।")},
    {"who": ("Someone in Durgapur", "দুর্গাপুরের কেউ"), "score": 71,
     "items": [("Films", "সিনেমা"), ("Puri trips", "পুরী"), ("Night owl", "রাত জাগা"),
               ("Prinsep Ghat", "প্রিন্সেপ ঘাট"), ("Football", "ফুটবল"), ("Mishti doi", "মিষ্টি দই")],
     "shared": ["Prinsep Ghat", "Mishti doi", "Puri trips"],
     "caption": ("You both love Prinsep Ghat, mishti doi and trips to Puri: a 71% match.",
                 "দুজনেই প্রিন্সেপ ঘাট, মিষ্টি দই আর পুরী বেড়াতে ভালোবাসেন: ৭১% মিল।")},
]


def venn_rows(n, middle, step):
    """y of n lines spaced `step` apart, centred on `middle` (shared in the overlap, the rest at the sides)."""
    return [middle - (n - 1) * step / 2 + k * step for k in range(n)]


def venn():
    """Two people's quiz answers as overlapping circles: the overlap is what they share.
    Same idea as the logo (two rings, marigold where they meet).
    Geometry: circles r=120 at x=170 and x=270, so the overlap (lens) spans x 150-290.
    data-venn carries the answers and people for match.js, which animates the matching."""
    first = VENN_PEOPLE[0]
    you_only = [item for item in VENN_YOU if item[0] not in first["shared"]]
    them_only = [item for item in first["items"] if item[0] not in first["shared"]]
    shared = [next(item for item in VENN_YOU if item[0] == en) for en in first["shared"]]
    data = html_escape(json.dumps({"you": VENN_YOU, "people": VENN_PEOPLE}, ensure_ascii=False), quote=True)
    def words(x, ys, items, cls=""):
        # One <text> per language for each line; site.js/CSS hide the other language.
        if not isinstance(ys, list):
            ys = [ys]
        out = []
        for i, (en, bn) in enumerate(items):
            dy = ys[i]
            out.append(f'<text x="{x}" y="{dy}" class="l {cls}" lang="en">{en}</text>'
                       f'<text x="{x}" y="{dy}" class="l {cls}" lang="bn">{bn}</text>')
        return "".join(out)

    return f"""<figure class="venn" data-venn="{data}">
<svg viewBox="0 0 440 320" aria-hidden="true">
  <defs><clipPath id="in-left"><circle cx="170" cy="170" r="120"/></clipPath></defs>
  <g class="who">
    {words(102, 30, [("You", "আপনি")])}
    {words(338, 30, [first["who"]])}
  </g>
  <circle class="ring ring-left" cx="170" cy="170" r="120"/>
  <circle class="ring ring-right" cx="270" cy="170" r="120"/>
  <g class="lens"><circle cx="270" cy="170" r="120" clip-path="url(#in-left)"/></g>
  <g class="side">
    {words(102, venn_rows(len(you_only), 176, 26), you_only)}
    {words(338, venn_rows(len(them_only), 176, 26), them_only)}
  </g>
  <g class="shared">
    {words(220, venn_rows(len(shared), 154 if len(shared) == 3 else 150, 26 if len(shared) == 3 else 24), shared)}
  </g>
  <g class="score">{words(220, 230, [(f"{first['score']}% match", f"{bn_num(first['score'])}% মিল")])}</g>
</svg>
<figcaption>{both(*first["caption"])}</figcaption>
<button class="venn-next" type="button" hidden>{both("Try someone else", "অন্য কাউকে দেখুন")}</button>
</figure>"""


def icon(name):
    paths = {
        "chat": '<path d="M5 6h14v9H9l-4 3z"/>',
        "people": '<circle cx="9" cy="9" r="3"/><circle cx="16" cy="10" r="2.5"/><path d="M3.5 19c.8-3 3-4.5 5.5-4.5s4.7 1.5 5.5 4.5M14 15c2.4-.4 4.6.8 5.5 3.5"/>',
        "badge": '<circle cx="12" cy="12" r="9"/><path d="M8 12.3l2.6 2.5L16 9.5"/>',
        "flag": '<path d="M6 21V4M6 4h11l-2.5 4L17 12H6"/>',
        "phone": '<path d="M7 3h3l1.5 4.5-2 1.3a11 11 0 0 0 5.7 5.7l1.3-2L21 14v3a2 2 0 0 1-2 2A16 16 0 0 1 5 5a2 2 0 0 1 2-2z"/>',
        "pin": '<path d="M12 21s-6-5.5-6-11a6 6 0 0 1 12 0c0 5.5-6 11-6 11z"/><circle cx="12" cy="10" r="2.2"/>',
        "lock": '<rect x="5" y="10" width="14" height="10" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/>',
        "adult": '<circle cx="12" cy="12" r="9.5"/><text x="12" y="15" text-anchor="middle">18+</text>',
    }
    return f'<svg viewBox="0 0 24 24" class="icon" aria-hidden="true">{paths[name]}</svg>'


# App screens shown in the phone mockups: file, alt text en/bn.
# Drawn by tools/make_app_screens.py in the app's new look (the app gets it before the Play Store release);
# after that, real screenshots can replace them (tools/prep_screens.py).
SCREENS = {
    "welcome": ("img/app-welcome.webp", "Mon Mela welcome screen with Continue with Google",
                "মনমেলার শুরুর স্ক্রিন, Google দিয়ে লগইন"),
    "looking": ("img/app-looking-for.webp", "Picking what you are looking for: adda, foodie, books and movies, the Puja gang",
                "কী খুঁজছেন বেছে নেওয়া: আড্ডা, খাওয়াদাওয়া, বই আর সিনেমা, পুজোর দল"),
    "quiz": ("img/app-quiz.webp", "Friendship quiz question 9 of 12: Your Durga Puja style?",
             "বন্ধুত্বের কুইজ, ১২টার মধ্যে ৯ নম্বর প্রশ্ন: দুর্গাপুজোয় আপনি কেমন?"),
    "picks": ("img/app-picks.webp", "Today's picks: Riti from Howrah, 86% match, and where your minds meet",
              "আজকের মানুষ: হাওড়ার রীতি, ৮৬% মিল, আর কোথায় মনের মিল"),
}


def phone(key, cls="", lazy=True, alt=True):
    """A phone frame around one app screen. alt=False for decorative copies."""
    src, alt_en, _ = SCREENS[key]
    loading = ' loading="lazy"' if lazy else ""
    alt_text = alt_en if alt else ""
    return (f'<div class="phone {cls}"><div class="screen">'
            f'<img src="{asset(src)}" alt="{alt_text}" width="720" height="1520"{loading}></div></div>')  # ?v= → new screenshot shows at once


def adda_card(cls, title_en, title_bn, when_en, when_bn, taken, seats, tag=None, full=True):
    """An Adda Table card in the app's style (decorative, for the Adda Tables band).
    full=False: a short card peeking out from behind (title, time and seats only).
    A full card also carries the later states of its button, seat count and note; motion.js plays
    them (ask -> request sent -> you're in). Without it only the first state shows."""
    def seats_text(n):
        return both(f"{n} of {seats} seats taken", f"{bn_num(seats)}টার মধ্যে {bn_num(n)}টা জায়গা ভরা")

    # The dot right after the taken ones is "yours": it fills when the host says yes.
    dots = "".join(f'<i class="{"on" if n < taken else "yours" if n == taken and full else ""}"></i>'
                   for n in range(seats))
    tag_html = f'<p class="ac-tag">{both(*tag)}</p>' if tag else ""
    count = (f'<span class="st st-ask">{seats_text(taken)}</span><span class="st st-in">{seats_text(taken + 1)}</span>'
             if full else seats_text(taken))
    rest = f"""
  <p class="ac-host">{icon("badge")}{both("Host is photo verified", "আয়োজক ছবি-যাচাই করা")}</p>
  <span class="ac-btn"><span class="st st-ask">{both("Ask for a seat", "জায়গা চান")}</span><span class="st st-wait"><i class="ac-pulse"></i>{both("Request sent", "অনুরোধ পাঠানো হয়েছে")}</span><span class="st st-in">{both("You're in! Group chat open", "জায়গা পেলেন! গ্রুপ চ্যাট খোলা")}</span></span>
  <p class="ac-note"><span class="st st-ask">{both("Exact spot shared once the host says yes", "আয়োজক রাজি হলে ঠিক জায়গা জানানো হবে")}</span><span class="st st-in">{both("Exact spot: the phuchka stall at Gariahat crossing", "ঠিক জায়গা: গড়িয়াহাট মোড়ের ফুচকার দোকান")}</span></p>""" if full else ""
    return f"""<div class="adda-card {cls}">
  {tag_html}<p class="ac-title">{both(title_en, title_bn)}</p>
  <p class="ac-when">{both(when_en, when_bn)}</p>
  <div class="ac-seats"><span class="ac-dots">{dots}</span><span class="ac-count">{count}</span></div>{rest}
</div>"""


# The story section: six moments of one friendship (pictures by tools/make_story.py).
# (big title in Bengali, its English line, text in English, text in Bengali, picture alt text)
STORY = [
    ("নতুন শহর", "A new city",
     "New job, new city, and evenings at the window. Everyone is busy, and there's no one to share a bhaar of cha with.",
     "নতুন চাকরি, নতুন শহর, সন্ধেগুলো কাটে জানলার ধারে। সবাই ব্যস্ত, এক ভাঁড় চা খাওয়ার সঙ্গী নেই।",
     "A young man sits alone at a window at night, looking out at the city lights"),
    ("একটা হ্যালো", "A hello",
     "Mon Mela shows someone nearby who also loves café adda and the hills. A wave, a wave back, and the chat opens.",
     "মনমেলা দেখাল কাছেই এমন একজনকে, যিনিও ক্যাফের আড্ডা আর পাহাড় ভালোবাসেন। হাত নাড়া, উত্তরে হাত নাড়া, আর চ্যাট খুলে গেল।",
     "A phone on a window sill showing a suggestion and a waving hand"),
    ("প্রথম আড্ডা", "The first adda",
     "Saturday, 5 pm, the para tea stall. Two cups of cha became six, and nobody looked at the time.",
     "শনিবার, বিকেল ৫টা, পাড়ার চায়ের দোকান। দু'ভাঁড় চা গড়াল ছ'ভাঁড়ে, ঘড়ি দেখল না কেউ।",
     "Three friends on a bench in front of a lit tea stall in the evening"),
    ("বইমেলা", "Boi Mela",
     "An Adda Table at the Book Fair: four people, too many books, and one shared jhola.",
     "বইমেলায় একটা আড্ডা টেবিল: চারজন মানুষ, অনেক বেশি বই, আর একটাই ঝোলা।",
     "Four friends at a book stall at the Kolkata Book Fair in the afternoon sun"),
    ("মেলার রাত", "A night at the mela",
     "Lights, the nagordola and phuchka. Now there's always someone to say \u201ccholo\u201d.",
     "আলো, নাগরদোলা আর ফুচকা। এখন \u201cচলো\u201d বলার লোক সবসময় আছে।",
     "Four friends at a fair at night, looking up at a lit giant wheel"),
    ("ঘাটে সন্ধে", "Evenings at the ghat",
     "The city doesn't feel new any more. It feels like home. Find your people on Mon Mela.",
     "শহরটা আর নতুন লাগে না, ঘর মনে হয়। মনমেলায় খুঁজে নিন আপনার মানুষদের।",
     "Four friends on a ghat of the Ganga at sunset, Howrah Bridge behind them"),
]


def music_button(cls="", play=("Play with music", "গান চালিয়ে দেখুন")):
    """A music on/off button (music.js shows it; without JavaScript there's no music).
    The story has one under its title; every page has the floating one (music_player)."""
    return (f'<button class="music-btn {cls}" type="button" aria-pressed="false" hidden>'
            f'<span class="mb-icon" aria-hidden="true"><i></i><i></i><i></i></span>'
            f'<span class="mb-play">{both(*play)}</span>'
            f'<span class="mb-pause">{both("Pause music", "গান থামান")}</span></button>')


def music_player():
    """The site's music, on every page: the floating button and the track (loaded only when it plays).
    The floating button also carries the "Tap for music" nudge that music.js shows when a page opens
    and the browser hasn't allowed sound yet."""
    nudge = f'<span class="mb-nudge">{both("Tap for music", "গান শুনতে ট্যাপ করুন")}</span>'
    return (music_button("music-float", ("Play music", "গান চালান")).replace("</button>", nudge + "</button>") +
            f'<audio class="site-audio" src="{asset("audio/story-theme.mp3")}" preload="none" loop></audio>')


def story_section():
    """Six chapters. Phones (and no JavaScript): each chapter is a picture card with its text.
    Wide screens with story.js: the pictures sit in one sticky frame on the right and cross-fade
    as each chapter scrolls past on the left."""
    chapters, frame, dots = [], [], []
    for i, (title_bn, title_en, en, bn, alt) in enumerate(STORY):
        src = asset(f"img/story-{i + 1}.webp")
        cta = f'<div class="actions">{get_app_button()}</div>' if i == len(STORY) - 1 else ""
        chapters.append(
            f'<li class="chapter" data-i="{i}">'
            f'<figure class="ch-pic"><img src="{src}" alt="{alt}" width="1000" height="1200" loading="lazy" decoding="async"></figure>'
            f'<div class="ch-text"><h3><span class="ch-bn" lang="bn">{title_bn}</span>'
            f'<span class="ch-en l" lang="en">{title_en}</span></h3><p>{both(en, bn)}</p>{cta}</div></li>')
        frame.append(f'<img class="sf-pic{" on" if i == 0 else ""}" src="{src}" alt="" width="1000" height="1200" loading="lazy" decoding="async">')
        dots.append(f'<span{" class=\"on\"" if i == 0 else ""}></span>')
    return f"""<section class="story" aria-labelledby="story-h">
    <div class="story-head">
      <h2 id="story-h">{both("A story of friendship", "একটা বন্ধুত্বের গল্প")}</h2>
      <p>{both("Six small moments, the way friendships start in Bengal.", "ছ'টা ছোট মুহূর্ত, বাংলায় যেভাবে বন্ধুত্ব শুরু হয়।")}</p>
      {music_button()}
      <p class="music-tune" hidden>{both("Tune: Purano Sei Diner Kotha", "সুর: পুরানো সেই দিনের কথা")}</p>
    </div>
    <div class="story-body">
      <ol class="story-chapters">{"".join(chapters)}</ol>
      <div class="story-frame" aria-hidden="true"><div class="sf-pics">{"".join(frame)}</div><div class="sf-dots">{"".join(dots)}</div></div>
    </div>
  </section>"""


def home():
    # How it works: four app screens in a row (a swipeable row on phones), then one line about chatting.
    steps = [
        ("welcome", "Sign in with Google", "Google দিয়ে লগইন",
         "One tap, no password. We never post anything for you.",
         "এক ট্যাপে, পাসওয়ার্ড ছাড়া। আপনার হয়ে কিছু পোস্ট হয় না।"),
        ("looking", "Say what you're looking for", "কী খুঁজছেন, বলুন",
         "Adda, a study partner, a gym buddy, the Puja gang: pick up to five.",
         "আড্ডা, পড়ার সঙ্গী, জিমের সঙ্গী, পুজোর দল: পাঁচটা পর্যন্ত বেছে নিন।"),
        ("quiz", "Answer the friendship quiz", "বন্ধুত্বের কুইজ",
         "Twelve easy questions. Your answers stay private; they only work out your match %.",
         "বারোটা সহজ প্রশ্ন। উত্তর গোপন থাকে, শুধু মিলের % হিসেব হয়।"),
        ("picks", "Meet today's picks", "আজকের মানুষেরা",
         "New people every morning, each with a match % and why you match.",
         "প্রতিদিন সকালে নতুন মানুষ, সঙ্গে মিলের % আর কেন মিল।"),
    ]
    # .how-thread: the kantha stitch to the next step (motion.js sews it in; static dashes without JS)
    thread = '<span class="how-thread" aria-hidden="true"></span>'
    steps_html = "".join(
        f'<li class="how-item">{thread if i < len(steps) - 1 else ""}{phone(k)}'
        f'<div class="how-cap"><h3>{both(t_en, t_bn)}</h3><p>{both(d_en, d_bn)}</p></div></li>'
        for i, (k, t_en, t_bn, d_en, d_bn) in enumerate(steps))

    safety = [
        ("chat", "Nobody can message you unless you accept their request.",
         "আপনি অনুরোধ না মানলে কেউ মেসেজ করতে পারে না।"),
        ("people", "Want to meet only people of your own gender? Turn it on, and only they will see you.",
         "শুধু নিজের লিঙ্গের মানুষের সঙ্গে আলাপ করতে চান? চালু করুন, তখন শুধু তাঁরাই আপনাকে দেখবেন।"),
        ("badge", "A ✓ Photo verified badge shows who has matched a live selfie to their photos.",
         "✓ ছবি যাচাই ব্যাজ দেখায় কে লাইভ সেলফি দিয়ে নিজের ছবি মিলিয়েছেন।"),
        ("flag", "Block or report anyone in two taps. Our team reviews reports.",
         "দু-ট্যাপে ব্লক বা রিপোর্ট। রিপোর্ট আমাদের টিম খতিয়ে দেখে।"),
        ("phone", "Call 112 (emergency) or 181 (women's helpline) straight from any chat.",
         "যেকোনো চ্যাট থেকে সরাসরি ১১২ (জরুরি) বা ১৮১ (মহিলা হেল্পলাইন)-এ ফোন।"),
        ("pin", "Others see only your district, never your exact location.",
         "অন্যরা শুধু আপনার জেলা দেখেন, সঠিক লোকেশন কখনও নয়।"),
    ]
    safety_html = "".join(f'<li>{icon(i)}<p>{both(en, bn)}</p></li>' for i, en, bn in safety)

    faq = [
        ("Is Mon Mela a dating app?", "মনমেলা কি ডেটিং অ্যাপ?",
         "No. It's for friendship: adda, study partners, travel buddies, people to go pandal hopping with.",
         "না। এটা বন্ধুত্বের জন্য: আড্ডা, পড়াশোনার সঙ্গী, ঘোরার সঙ্গী, পুজোয় ঠাকুর দেখার দল।"),
        ("What are Adda Tables?", "আড্ডা টেবিল কী?",
         "Small group meetups of 3 to 6 people at a café, phuchka stall, park or College Street. A photo-verified member hosts, you ask for a seat, and the host says yes. The exact spot and the group chat open only for the people at the table, and women can host women-only addas.",
         "৩ থেকে ৬ জনের ছোট আড্ডা, ক্যাফে, ফুচকার দোকান, পার্ক বা কলেজ স্ট্রিটে। ছবি-যাচাই করা কেউ আয়োজন করেন, আপনি জায়গা চান, আয়োজক রাজি হলে যোগ দিন। ঠিক জায়গা আর গ্রুপ চ্যাট শুধু আড্ডার মানুষদের জন্য, আর মহিলারা শুধু মহিলাদের আড্ডা বসাতে পারেন।"),
        ("Does it cost anything?", "এর জন্য কি টাকা লাগে?",
         "No. Mon Mela is free, with no ads, and we never sell your data.",
         "না। মনমেলা বিনামূল্যে, কোনো বিজ্ঞাপন নেই, আর আপনার তথ্য কখনও বিক্রি হয় না।"),
        ("Who can see my photos?", "আমার ছবি কারা দেখতে পান?",
         "Only members who get you as a suggestion, and people you have a connection request with. Never anyone you block, and never the open internet.",
         "শুধু সেই সদস্যরা যাঁদের তালিকায় আপনি আছেন, আর যাঁদের সঙ্গে কানেকশন রিকোয়েস্ট আছে। যাঁদের ব্লক করেছেন তাঁরা নন, আর ইন্টারনেটে খোলা কখনও নয়।"),
        ("When can I download it?", "কবে ডাউনলোড করতে পারব?",
         'Now, on Android: <a href="download.html">download Mon Mela here</a>. It comes to Google Play soon; iPhone follows later.',
         'এখনই, অ্যান্ড্রয়েডে: <a href="download.html">এখান থেকে মনমেলা ডাউনলোড করুন</a>। শিগগিরই Google Play-তে আসছে; iPhone পরে।'),
        ("How do I delete my account?", "অ্যাকাউন্ট কীভাবে মুছব?",
         'In the app: Profile, then Delete account. <a href="delete-account.html">More about deleting your account</a>.',
         'অ্যাপে: প্রোফাইল, তারপর অ্যাকাউন্ট মুছুন। <a href="delete-account.html">অ্যাকাউন্ট মোছা নিয়ে বিস্তারিত</a>।'),
        ("Who runs Mon Mela?", "মনমেলা কে চালান?",
         f'Mon Mela is run by Dhritisha Palmal in West Bengal, who is also our Grievance Officer. Write to <a href="mailto:{EMAIL}">{EMAIL}</a>.',
         f'মনমেলা পরিচালনা করেন পশ্চিমবঙ্গের Dhritisha Palmal, যিনি আমাদের অভিযোগ আধিকারিকও। লিখুন <a href="mailto:{EMAIL}">{EMAIL}</a>-এ।'),
    ]
    # Questions as a chat with Mon Mela: each question is a message you tap, the answer is Mon Mela's
    # reply (motion.js shows it "typing" first). The first one starts open to show how it works.
    typing = '<span class="ask-typing" aria-hidden="true"><i></i><i></i><i></i></span>'
    faq_html = "".join(
        f'<details{" open" if i == 0 else ""}><summary>{both(q_en, q_bn)}</summary>{typing}<p>{both(a_en, a_bn)}</p></details>'
        for i, (q_en, q_bn, a_en, a_bn) in enumerate(faq))

    # Title and description: the words people actually search for (Bengali friendship app,
    # Kolkata, West Bengal, adda), in under ~60 and ~155 characters so Google shows them whole.
    html = f"""{head(HOME_TITLE_EN, HOME_TITLE_BN, HOME_DESCRIPTION, "", script("story.js") + script("motion.js") + script("match.js") + home_schema(faq))}
<body class="home">
{header(on_home=True)}
<section class="hero-k">
  {festoon()}
  <div class="hero-k-text">
    <h1 lang="bn">মন মিললে, <br>বন্ধু মেলে।</h1>   <!-- in Bengali on both language versions; the line below explains it -->
    <p class="lede">{both(
        "New city, but no one to share a cup of cha with? Mon Mela finds friends nearby who love what you love.",
        "নতুন শহর, কিন্তু চায়ের সঙ্গী নেই? মনমেলা খুঁজে দেয় কাছেপিঠে মনের মতো বন্ধু।")}</p>
  </div>
  <div class="hero-k-art">
    {hero_art(asset("img/hero-ghat.webp"))}
    <!-- Two small cards in the app's own style, floating on the picture (decorative) -->
    <div class="float-card match-card" aria-hidden="true">
      <div class="mc-top">
        <svg class="mc-ring" viewBox="0 0 64 64"><circle class="track" cx="32" cy="32" r="26"/><circle class="fill" cx="32" cy="32" r="26" pathLength="100"/><text x="32" y="37" class="mc-pct">86%</text></svg>
        <div><p class="mc-who">{both("You and Riti", "আপনি আর রীতি")}</p><p class="mc-why">{both("Where your minds meet", "মনের মিল")}</p></div>
      </div>
      <ul class="mc-chips"><li>{both("Prinsep Ghat", "প্রিন্সেপ ঘাট")}</li><li>{both("Durga Puja", "দুর্গাপুজো")}</li><li>{both("Mishti doi", "মিষ্টি দই")}</li><li>{both("Feluda", "ফেলুদা")}</li></ul>
    </div>
    <div class="float-card seat-card" aria-hidden="true">
      <b>☕</b><span>{both("Phuchka adda, Gariahat: <em>2 seats left</em>", "গড়িয়াহাটে ফুচকা আড্ডা: <em>২টো জায়গা খালি</em>")}</span>
    </div>
  </div>
</section>

<main class="home-main">
  {story_section()}

  <section class="how" aria-labelledby="how">
    <h2 id="how">{both("How it works", "কীভাবে কাজ করে")}</h2>
    <ol class="how-row">{steps_html}</ol>
    <p class="how-then">{icon("chat")}<span>{both("<b>Then connect.</b> The chat opens only when both of you say yes.",
                                                  "<b>তারপর কানেক্ট।</b> দুজনেই রাজি হলে তবেই চ্যাট খোলে।")}</span></p>
  </section>

  <section class="match" aria-labelledby="match-h">
    <div class="match-inner">
      <div class="match-text">
        <h2 id="match-h">{both("Matched by what you share", "মিল খুঁজে দেয় আপনার উত্তর")}</h2>
        <p>{both("Every suggestion shows a match % and the answers you have in common, so the first message is easy.",
                 "প্রতিটি সাজেশনে থাকে মিলের % আর কোন কোন উত্তরে মিল, তাই প্রথম মেসেজটা লেখা সহজ।")}</p>
      </div>
      {venn()}
    </div>
  </section>

  <section class="adda" aria-labelledby="adda-h">
    <div class="adda-text">
      <h2 id="adda-h">{both("Adda Tables: meet in a small group", "আড্ডা টেবিল: ছোট দলে দেখা")}</h2>
      <p class="adda-lede">{both(
          "Rather meet a few people at once? Join a table of 3 to 6 at a café, a phuchka stall, a park or College Street.",
          "একসঙ্গে কয়েকজনের সঙ্গে আলাপ করতে চান? ক্যাফে, ফুচকার দোকান, পার্ক বা কলেজ স্ট্রিটে ৩ থেকে ৬ জনের আড্ডায় যোগ দিন।")}</p>
      <ul class="adda-points">
        <li>{icon("badge")}<p>{both("A photo-verified member hosts every table.", "প্রতিটি আড্ডা বসান ছবি-যাচাই করা একজন সদস্য।")}</p></li>
        <li class="pt-wait">{icon("chat")}<p>{both("Ask for a seat. You join when the host says yes.", "জায়গা চান। আয়োজক রাজি হলে যোগ দিন।")}</p></li>
        <li class="pt-in">{icon("pin")}<p>{both("The exact spot and the group chat open only for the people at the table.", "ঠিক জায়গা আর গ্রুপ চ্যাট খোলে শুধু আড্ডার মানুষদের জন্য।")}</p></li>
        <li>{icon("people")}<p>{both("Women can host women-only addas.", "মহিলারা শুধু মহিলাদের আড্ডা বসাতে পারেন।")}</p></li>
      </ul>
    </div>
    <div class="adda-art" aria-hidden="true">
      {adda_card("back", "Book adda, College Street", "বইয়ের আড্ডা, কলেজ স্ট্রিট", "Sunday, 11 am", "রবিবার, সকাল ১১টা", 2, 4,
                 ("Women only", "শুধু মহিলা"), full=False)}
      {adda_card("front", "Phuchka and adda, Gariahat", "ফুচকা আর আড্ডা, গড়িয়াহাট", "Saturday, 5:30 pm", "শনিবার, বিকেল ৫:৩০", 4, 6)}
    </div>
  </section>

  <section class="safety" aria-labelledby="safe">
    <div class="safety-head">
      <h2 id="safe">{both("Safe by design", "শুরু থেকেই নিরাপদ")}</h2>
      <p>{both("Built first for the people who usually feel least safe on social apps.",
               "সোশ্যাল অ্যাপে যাঁরা সবচেয়ে কম নিরাপদ বোধ করেন, তাঁদের কথা ভেবেই তৈরি।")}</p>
    </div>
    <ul>{safety_html}</ul>
  </section>

  <section class="faq ask" aria-labelledby="qa">
    <div class="ask-head">
      <h2 id="qa">{both("Questions", "প্রশ্ন")}</h2>
      <p class="ask-lede">{both("Ask us anything. Tap a question and Mon Mela replies.", "যা খুশি জিজ্ঞেস করুন। প্রশ্নে ট্যাপ করুন, মনমেলা উত্তর দেবে।")}</p>
    </div>
    <div class="ask-chat">{faq_html}</div>
    <p class="ask-more">{both("Can't find your answer?", "উত্তর পেলেন না?")} <a href="mailto:{EMAIL}">{EMAIL}</a></p>
  </section>
</main>
{footer(on_home=True)}
</body>
</html>
"""
    (ROOT / "index.html").write_text(html, encoding="utf-8")


# ------------------------------------------------------------ app download

HOME_TITLE_EN = "Mon Mela – Bengali Friendship App for Kolkata &amp; West Bengal"
HOME_TITLE_BN = "মনমেলা – কলকাতা ও পশ্চিমবঙ্গের বন্ধুত্বের অ্যাপ"
HOME_DESCRIPTION = ("Mon Mela (মনমেলা) is a free Bengali friendship app for Kolkata and West Bengal. "
                    "Find friends nearby who love what you love, and join adda meetups. Not a dating app.")


def strip_tags(html):
    """Plain text of an HTML snippet (for structured data, which must not contain markup)."""
    return re.sub(r"<[^>]+>", "", html)


def home_schema(faq):
    """Structured data (schema.org JSON-LD) for the home page, so Google understands what
    Mon Mela is: the organisation, the website, the Android app (free) and the FAQ.
    Only facts that are true on the page; no ratings (we don't have public ones yet)."""
    data = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Organization",
                "@id": f"{SITE}/#org",
                "name": "Mon Mela",
                "alternateName": "মনমেলা",
                "url": f"{SITE}/",
                "logo": f"{SITE}/icon-512.png",
                "email": EMAIL,
                "areaServed": "West Bengal, India",
                "sameAs": [INSTAGRAM_URL, FACEBOOK_URL],
            },
            {
                "@type": "WebSite",
                "@id": f"{SITE}/#website",
                "name": "Mon Mela",
                "alternateName": "মনমেলা",
                "url": f"{SITE}/",
                "inLanguage": ["en", "bn"],
                "publisher": {"@id": f"{SITE}/#org"},
            },
            {
                "@type": "MobileApplication",
                "name": "Mon Mela",
                "alternateName": "মনমেলা",
                "operatingSystem": "Android",
                "applicationCategory": "SocialNetworkingApplication",
                "description": HOME_DESCRIPTION,
                "url": f"{SITE}/",
                "downloadUrl": PLAY_URL or f"{SITE}/download",
                "inLanguage": ["bn", "en"],
                "offers": {"@type": "Offer", "price": "0", "priceCurrency": "INR"},
                "publisher": {"@id": f"{SITE}/#org"},
            },
            {
                "@type": "FAQPage",
                "mainEntity": [
                    {"@type": "Question", "name": q_en,
                     "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a_en)}}
                    for q_en, _q_bn, a_en, _a_bn in faq
                ],
            },
        ],
    }
    # "</" can't appear inside a <script> block; JSON allows it escaped as "<\/".
    return ('<script type="application/ld+json">'
            + json.dumps(data, ensure_ascii=False).replace("</", "<\\/") + "</script>")


def sitemap():
    """sitemap.xml: every public page with today's date, so Google finds and re-reads them.
    The URLs match each page's canonical link."""
    today = datetime.date.today().isoformat()
    paths = ["", "download", "privacy.html", "terms.html", "delete-account.html", "child-safety.html"]
    urls = "".join(f"  <url><loc>{SITE}/{p}</loc><lastmod>{today}</lastmod></url>\n" for p in paths)
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + "</urlset>\n",
        encoding="utf-8")
    # robots.txt: crawling stays allowed even with NOINDEX, because Google must read the pages to see
    # the noindex tag and drop them (a blocked page can stay in search). No sitemap while NOINDEX.
    robots = "User-agent: *\nAllow: /\n" if NOINDEX else f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n"
    (ROOT / "robots.txt").write_text(robots, encoding="utf-8")


def get_app_button(cls="btn btn-primary", short=False):
    """The site's one 'get the app' button: Google Play (the test now, the public app after launch)."""
    play = PLAY_URL or TEST_PLAY_URL
    if play:
        label = ("Get the app", "অ্যাপ নিন") if short else ("Get it on Google Play", "Google Play থেকে নিন")
        return f'<a class="{cls}" href="{play}">{both(*label)}</a>'
    label = ("Download", "ডাউনলোড") if short else ("Download for Android", "অ্যান্ড্রয়েডে ডাউনলোড করুন")
    return f'<a class="{cls}" href="download.html">{both(*label)}</a>'


def qr_svg(url):
    """QR code (inline SVG) so people on a computer can open the download page on their phone."""
    import qrcode
    import qrcode.image.svg
    img = qrcode.make(url, image_factory=qrcode.image.svg.SvgPathImage, border=2)
    svg = img.to_string(encoding="unicode")
    return svg[svg.index("<svg"):]  # drop the <?xml ...?> line


def download():
    """monmela.in/download: the address to share everywhere. Its target changes, the link never does."""
    page_url = f"{SITE}/download"

    if PLAY_URL:  # after launch: send everyone to Google Play
        html = f"""{head("Download Mon Mela", "মনমেলা ডাউনলোড", "Get Mon Mela on Google Play.", "download",
                        f'<meta http-equiv="refresh" content="0; url={PLAY_URL}">')}
<body class="home">
{header()}
<section class="intro"><p>{both("Opening Google Play…", "Google Play খুলছে…")}
  <a href="{PLAY_URL}">{both("Tap here if it doesn't open.", "না খুললে এখানে চাপুন।")}</a></p></section>
{footer()}
</body>
</html>
"""
        (ROOT / "download.html").write_text(html, encoding="utf-8")
        return

    steps = [
        ('Tap "Download APK". If Chrome says the file might be harmful, tap "Download anyway".',
         '"ডাউনলোড APK" চাপুন। Chrome যদি বলে ফাইলটি ক্ষতিকর হতে পারে, "Download anyway" চাপুন।'),
        ("Open the file: tap the download notification, or go to Files, then Downloads, then mon-mela.apk.",
         "ফাইলটি খুলুন: ডাউনলোডের নোটিফিকেশনে চাপুন, অথবা Files, তারপর Downloads, তারপর mon-mela.apk।"),
        ('If your phone asks, turn on "Allow from this source" for Chrome (or Files), then go back.',
         'ফোন জিজ্ঞেস করলে Chrome (বা Files)-এর জন্য "Allow from this source" চালু করে ফিরে আসুন।'),
        ('Tap "Install". If Play Protect shows a warning, tap "More details", then "Install anyway".',
         '"Install" চাপুন। Play Protect সতর্ক করলে "More details", তারপর "Install anyway" চাপুন।'),
        ("Open Mon Mela and sign in with Google.", "মনমেলা খুলে Google দিয়ে লগইন করুন।"),
    ]
    steps_html = "".join(f"<li><p>{both(en, bn)}</p></li>" for en, bn in steps)

    # Google Play test (while TEST_JOIN_URL is set): two steps, ONE big button at a time.
    # Without JavaScript both steps show their own button; download.js turns this into a guided
    # flow: the big button does step 1, then becomes step 2, and remembers where you were.
    play_flow = ""
    if TEST_PLAY_URL:  # testers: one button, straight to the app on Google Play
        play_flow = f"""<a class="btn btn-primary btn-big" href="{TEST_PLAY_URL}">{both("Open in Google Play", "Google Play-তে খুলুন")}</a>
        <p class="dl-meta">{both(
            "Use the Gmail you joined the Mon Mela test with.",
            "যে Gmail দিয়ে মনমেলা টেস্টে যোগ দিয়েছেন, সেটাই ব্যবহার করুন।")}</p>"""
    elif TEST_JOIN_URL:
        play_flow = f"""<div class="flow" id="flow">
        <ol class="play-steps">
          <li id="step1"><span>{both("Join the Mon Mela testers group", "মনমেলা টেস্টার গ্রুপে যোগ দিন")}</span>
            <a class="btn btn-primary step-btn" href="{TEST_GROUP_URL}" target="_blank" rel="noopener">{both("Join group", "গ্রুপে যোগ দিন")}</a></li>
          <li id="step2"><span>{both("Become a tester, then install from Google Play", "টেস্টার হন, তারপর Google Play থেকে ইনস্টল করুন")}</span>
            <a class="btn btn-primary step-btn" href="{TEST_JOIN_URL}" target="_blank" rel="noopener">{both("Become a tester", "টেস্টার হন")}</a></li>
        </ol>
        <!-- download.js shows this single button instead of the two above -->
        <a class="btn btn-primary btn-big" id="flow-btn" href="{TEST_GROUP_URL}" target="_blank" rel="noopener" hidden
           data-group="{TEST_GROUP_URL}" data-join="{TEST_JOIN_URL}">
          <span class="l" lang="en" data-en1="Step 1: Join the testers group" data-en2="Step 2: Become a tester"
                data-en3="Open the tester page again">Step 1: Join the testers group</span><span class="l" lang="bn"
                data-bn1="ধাপ ১: টেস্টার গ্রুপে যোগ দিন" data-bn2="ধাপ ২: টেস্টার হন"
                data-bn3="টেস্টার পেজ আবার খুলুন">ধাপ ১: টেস্টার গ্রুপে যোগ দিন</span></a>
        <p class="dl-meta" id="flow-hint">{both(
            "Use the same Gmail as your phone's Play Store. It takes about a minute.",
            "ফোনের Play Store-এ যে Gmail আছে সেটাই ব্যবহার করুন। মিনিটখানেক লাগে।")}</p>
        <p class="dl-meta" id="flow-done" hidden>{both(
            'On the tester page, tap "Download it on Google Play" and install. Not working yet? Wait 15 minutes after joining the group, then try again.',
            'টেস্টার পেজে "Download it on Google Play" চেপে ইনস্টল করুন। কাজ না করলে গ্রুপে যোগ দেওয়ার ১৫ মিনিট পরে আবার চেষ্টা করুন।')}
          <button type="button" class="link-btn" id="flow-restart">{both("Start again", "আবার শুরু করুন")}</button></p>
      </div>"""

    # The APK: during the Play test it's folded away under "Can't use Google Play?" with its own
    # install steps; without a Play test it's the main, big button and the steps get a section.
    on_play = bool(TEST_PLAY_URL or TEST_JOIN_URL)
    apk_button_cls = "btn-ghost" if on_play else "btn-primary btn-big"
    apk_button = (f'<a class="btn {apk_button_cls}" id="apk" href="{APK_FILE}" download="mon-mela.apk">'
                  f'{both("Download APK", "ডাউনলোড APK")}</a>'
                  f'<p class="dl-meta">{both("Android app", "অ্যান্ড্রয়েড অ্যাপ")}<span id="apk-size"></span></p>')
    if on_play:
        apk_block = f"""<details class="apk-more" id="get">
        <summary>{both("Can't use Google Play? Download the APK instead", "Google Play চালাতে পারছেন না? APK ডাউনলোড করুন")}</summary>
        {apk_button}
        <ol class="apk-steps">{steps_html}</ol>
      </details>"""
        steps_section = ""
    else:
        apk_block = f'<div id="get">{apk_button}</div>'
        steps_section = f"""<section class="steps" aria-labelledby="install">
    <h2 id="install">{both("Installing the APK", "APK কীভাবে ইনস্টল করবেন")}</h2>
    <ol>{steps_html}</ol>
  </section>
"""

    help_items = [
        ("Google Play says the app isn't available", "Google Play বলছে অ্যাপটি পাওয়া যাচ্ছে না",
         "Mon Mela is in a closed test, so only testers can install it. Check that your phone's Play Store uses "
         f"the Gmail you joined the test with. Not a tester yet? Write to us at {EMAIL}.",
         "মনমেলা এখন ক্লোজড টেস্টে, তাই শুধু টেস্টাররাই ইনস্টল করতে পারেন। ফোনের Play Store-এ সেই Gmail আছে কি না দেখুন, "
         f"যেটা দিয়ে টেস্টে যোগ দিয়েছেন। এখনও টেস্টার নন? আমাদের লিখুন: {EMAIL}।"),
        ("Chrome says the file might be harmful", "Chrome বলছে ফাইলটি ক্ষতিকর হতে পারে",
         'Chrome says this about every app downloaded outside the Play Store. Tap "Download anyway".',
         'Play Store-এর বাইরে থেকে নামানো সব অ্যাপের ক্ষেত্রেই Chrome এটা বলে। "Download anyway" চাপুন।'),
        ("Nothing happens when I tap Download", "ডাউনলোড চাপলে কিছু হচ্ছে না",
         f"You may be inside Instagram, Facebook or another app's browser, which often blocks downloads. "
         f"Open <strong>monmela.in/download</strong> in Chrome and try again.",
         f"আপনি হয়তো Instagram, Facebook বা অন্য কোনো অ্যাপের ভেতরের ব্রাউজারে আছেন, যেখানে ডাউনলোড প্রায়ই আটকে যায়। "
         f"Chrome-এ <strong>monmela.in/download</strong> খুলে আবার চেষ্টা করুন।"),
        ('"App not installed" or "problem parsing the package"', '"App not installed" বা "problem parsing the package"',
         "The download probably didn't finish. Delete mon-mela.apk from Downloads and download it again on Wi-Fi "
         "or a steady connection. Mon Mela needs Android 7 or newer and some free space.",
         "সম্ভবত ডাউনলোড পুরো হয়নি। Downloads থেকে mon-mela.apk মুছে Wi-Fi বা ভালো নেটওয়ার্কে আবার ডাউনলোড করুন। "
         "মনমেলা চালাতে Android 7 বা তার নতুন ভার্সন আর কিছুটা ফাঁকা জায়গা লাগে।"),
        ('"Conflicts with an existing package"', '"Conflicts with an existing package"',
         "An older copy of Mon Mela from somewhere else is on your phone. Uninstall it, then install this one. "
         "Your account and chats are safe: they're stored online, not on the phone.",
         "অন্য জায়গা থেকে নেওয়া মনমেলার পুরোনো কপি ফোনে আছে। সেটা আনইনস্টল করে এটা ইনস্টল করুন। "
         "আপনার অ্যাকাউন্ট আর চ্যাট নিরাপদ: সেগুলো অনলাইনে রাখা থাকে, ফোনে নয়।"),
        ("How do I update the app?", "অ্যাপ আপডেট করব কীভাবে?",
         "Download it again from this page and install it over the old one. Nothing is lost. "
         "Once Mon Mela is on Google Play, you can update it there.",
         "এই পেজ থেকে আবার ডাউনলোড করে পুরোনোটার ওপরেই ইনস্টল করুন। কিছুই হারাবে না। "
         "মনমেলা Google Play-তে এলে সেখান থেকেই আপডেট করতে পারবেন।"),
    ]
    help_html = "".join(
        f'<details><summary>{both(q_en, q_bn)}</summary><p>{both(a_en, a_bn)}</p></details>'
        for q_en, q_bn, a_en, a_bn in help_items)

    html = f"""{head("Download Mon Mela for Android", "অ্যান্ড্রয়েডে মনমেলা ডাউনলোড",
                    "Download the Mon Mela app for Android: free, Bengali-first friendship app for West Bengal.",
                    "download", script("download.js"))}
<body class="home dl">
{header()}
<section class="intro">
  {festoon()}
  <div class="intro-inner">
    <div>
      <h1>{both("Mon Mela for your Android phone", "আপনার অ্যান্ড্রয়েড ফোনে মনমেলা")}</h1>
      <p class="lede">{both(
          "Free. For Mon Mela testers: tap the button to open the app on Google Play and install or update it.",
          "বিনামূল্যে। মনমেলা টেস্টারদের জন্য: বোতাম চাপলেই Google Play-তে অ্যাপটি খুলবে, সেখান থেকে ইনস্টল বা আপডেট করুন।")}</p>

      <!-- Shown by download.js inside Instagram/Facebook-style in-app browsers -->
      <div class="dl-note" id="inapp" hidden>
        <p>{both("Downloads often fail inside Instagram, Facebook and similar apps. Open this page in your browser first.",
                 "Instagram, Facebook-এর মতো অ্যাপের ভেতরে ডাউনলোড প্রায়ই আটকে যায়। আগে পেজটা ব্রাউজারে খুলুন।")}</p>
        <div class="actions">
          <a class="btn btn-primary" href="intent://monmela.in/download#Intent;scheme=https;end">{both("Open in browser", "ব্রাউজারে খুলুন")}</a>
          <button type="button" class="btn btn-ghost" id="copy">{both("Copy link", "লিংক কপি করুন")}</button>
        </div>
        <input id="page-link" readonly value="{page_url}" aria-label="Page link">
      </div>

      <!-- Shown by download.js on iPhone and iPad -->
      <div class="dl-note" id="ios" hidden>
        <p>{both("Mon Mela is on Android for now. The iPhone version comes later.",
                 "মনমেলা এখন শুধু অ্যান্ড্রয়েডে। iPhone ভার্সন পরে আসবে।")}</p>
      </div>

      {play_flow}
      {apk_block}
      <!-- Shown by download.js if the APK isn't on the site yet, instead of a broken button -->
      <p class="dl-note" id="soon" hidden>{both("The download will be ready very soon. Please check back in a day.",
                                               "ডাউনলোড খুব শিগগিরই তৈরি হবে। একদিন পরে আবার দেখুন।")}</p>
      <p class="not-dating">{both("For friendship, not dating. Adults 18+ only.", "বন্ধুত্বের জন্য, ডেটিংয়ের জন্য নয়। শুধু ১৮+।")}</p>
    </div>

    <div class="dl-visual">
      {phone("welcome", lazy=False)}
      <!-- Computers only (CSS): scan to open this page on the phone -->
      <figure class="dl-qr">
        {qr_svg(page_url)}
        <figcaption>{both("On a computer? Scan with your phone's camera to open this page there.",
                          "কম্পিউটারে আছেন? ফোনের ক্যামেরায় স্ক্যান করে পেজটা ফোনে খুলুন।")}</figcaption>
      </figure>
    </div>
  </div>
</section>

<main class="home-main">
  {steps_section}
  <section class="faq" aria-labelledby="help">
    <h2 id="help">{both("If something goes wrong", "সমস্যা হলে")}</h2>
    {help_html}
  </section>
</main>
{footer()}
</body>
</html>
"""
    (ROOT / "download.html").write_text(html, encoding="utf-8")


def adda():
    """monmela.in/adda?id=…: where a shared Adda Table link lands when the app can't open it
    (no app yet, iPhone, computer). With the app on Android, the link opens the table in the app
    directly (App Links: .well-known/assetlinks.json) and this page never shows.
    GitHub Pages serves adda.html at /adda. Not in the sitemap and noindex: it has no content of its own."""
    get_url = PLAY_URL or TEST_PLAY_URL or f"{SITE}/download"  # people without the app
    html = f"""{head("You're invited to an adda", "আপনাকে একটা আড্ডায় ডাকা হয়েছে",
                    "Someone shared an Adda Table on Mon Mela. Open it in the app to see who's going.",
                    "adda", script("adda.js"))}
<body class="home dl">
{header()}
<section class="intro">
  {festoon()}
  <div class="intro-inner">
    <div>
      <h1>{both("You're invited to an adda", "আপনাকে একটা আড্ডায় ডাকা হয়েছে")}</h1>
      <p class="lede">{both(
          "Someone shared an Adda Table with you. Open it in the Mon Mela app to see the topic, "
          "who's going, and ask for a seat.",
          "কেউ আপনার সঙ্গে একটা আড্ডা টেবিল শেয়ার করেছেন। বিষয়, কারা যাচ্ছেন দেখতে আর জায়গা চাইতে "
          "মনমেলা অ্যাপে খুলুন।")}</p>

      <!-- adda.js shows this on Android when the link has a table id. Without the app installed,
           Android opens get_url instead. -->
      <div class="actions" id="open" hidden>
        <a class="btn btn-primary btn-big" id="open-btn" href="{get_url}"
           data-host="monmela.in" data-fallback="{get_url}">{both("Open in the app", "অ্যাপে খুলুন")}</a>
      </div>
      <p class="dl-meta" id="open-hint" hidden>{both(
          "Don't have the app yet? The button takes you to Google Play.",
          "অ্যাপ নেই? বোতামটা আপনাকে Google Play-তে নিয়ে যাবে।")}</p>

      <div class="actions" id="get">
        <a class="btn btn-ghost" href="{get_url}">{both("Get the app", "অ্যাপ নিন")}</a>
      </div>

      <!-- Shown by adda.js on iPhone and iPad -->
      <div class="dl-note" id="ios" hidden>
        <p>{both("Mon Mela is on Android for now. The iPhone version comes later.",
                 "মনমেলা এখন শুধু অ্যান্ড্রয়েডে। iPhone ভার্সন পরে আসবে।")}</p>
      </div>
      <p class="not-dating">{both("For friendship, not dating. Adults 18+ only.", "বন্ধুত্বের জন্য, ডেটিংয়ের জন্য নয়। শুধু ১৮+।")}</p>
    </div>

    <div class="dl-visual">
      {phone("welcome", lazy=False)}
    </div>
  </div>
</section>
{footer()}
</body>
</html>
"""
    (ROOT / "adda.html").write_text(html, encoding="utf-8")


def assetlinks():
    """.well-known/assetlinks.json: proves to Android that this site belongs to the app, so
    /adda links open the app without asking. Needs the app's SHA-256 signing fingerprints
    (Play Console → App integrity). Written only once APP_SHA256 is filled in."""
    if not APP_SHA256:
        return
    data = [{"relation": ["delegate_permission/common.handle_all_urls"],
             "target": {"namespace": "android_app", "package_name": APP_ID,
                        "sha256_cert_fingerprints": APP_SHA256}}]
    folder = ROOT / ".well-known"
    folder.mkdir(exist_ok=True)
    (folder / "assetlinks.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


(ROOT / "img" / "alpana.svg").write_text(alpana_tile(), encoding="utf-8")
home()
download()
page("privacy.html", "Privacy Policy", "প্রাইভেসি পলিসি",
     f"Last updated: {UPDATED_EN}", f"সর্বশেষ আপডেট: {UPDATED_BN}",
     load("privacy.en.html"), load("privacy.bn.html"))
page("terms.html", "Terms of Use", "ব্যবহারের শর্তাবলি",
     f"Last updated: {UPDATED_EN}", f"সর্বশেষ আপডেট: {UPDATED_BN}",
     load("terms.en.html"), load("terms.bn.html"))
page("delete-account.html", "Delete your account", "অ্যাকাউন্ট মুছে ফেলুন",
     "How to delete your Mon Mela account and data", "মনমেলা অ্যাকাউন্ট ও তথ্য কীভাবে মুছবেন",
     load("delete.en.html"), load("delete.bn.html"))
page("child-safety.html", "Child Safety Standards", "শিশু সুরক্ষা নীতি",
     f"Last updated: {UPDATED_EN}", f"সর্বশেষ আপডেট: {UPDATED_BN}",
     load("child.en.html"), load("child.bn.html"))
adda()
assetlinks()
sitemap()
print("built")
