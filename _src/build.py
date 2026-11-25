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
from urllib.parse import quote

from art import LOGO, alpana_tile, festoon, hero_art

ROOT = pathlib.Path(__file__).resolve().parent.parent      # the site folder (built files go here)
PAGES = pathlib.Path(__file__).resolve().parent / "pages"  # legal page bodies
SITE = "https://monmela.in"
# Mon Mela is the brand for good (20 Nov 2026), so Google may list every page again.
# True = a "noindex" tag on every page and no sitemap (asks Google to drop the site).
NOINDEX = False
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

# HOME_BRAND: another name for the home page only (None = Mon Mela, as on every other page).
HOME_BRAND = None
# The hero's photo (wide, friends, no text on it). Until our own arrives: story photo 6, the ghat at sunset.
HERO_PHOTO = "img/hero-friends.webp"
HERO_PHOTO_FALLBACK = "img/story-3.webp"
# HERO_STYLE "poster": the friends-on-the-ghat poster (img/hero-poster.webp; its old logo and words removed)
# with our own chips, logo and words laid over it. "photo": the photo on the right, words on the left.
HERO_STYLE = "light"   # "light": the bright riverside home page (Nov 2026); "poster" / "photo": earlier versions

# The "Join us" pages (join, ambassador, partners, creators, host) all send people to ONE Google Form,
# so every application lands in one sheet. The form's first question is "How would you like to be
# part of Mon Mela?" with exactly the ROLES labels below as its options.
# JOIN_FORM_URL: the form's link (…/viewform). JOIN_FORM_ROLE_ENTRY: that question's prefill id, e.g.
# "entry.1234567890" (Form ⋮ → Get pre-filled link → pick an option → copy link → the entry.… part),
# so each page's button arrives with its role already picked. Empty URL = the buttons open an e-mail
# to us instead, with the questions in it.
JOIN_FORM_URL = ""
JOIN_FORM_ROLE_ENTRY = ""
ROLES = {
    "ambassador": "Campus ambassador",
    "partner": "Venue or event partner",
    "creator": "Creator",
    "host": "Adda host",
}

# Our social pages: linked in the footer and listed in the structured data ("sameAs"),
# which tells Google these pages belong to the same Mon Mela.
# None hides one (footer and structured data).
INSTAGRAM_URL = "https://www.instagram.com/monmela.in/"
INSTAGRAM_HANDLE = "@monmela.in"
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
    """Floating top bar on every page: logo, section links, language switch, Download.
    Wide screens: the links sit in the bar. Narrower: a second row under the logo. Phones drop
    Questions (class "wide-only"; it is also in the footer) so the other four fit in one row.
    On the home page the links only scroll; elsewhere they open the home page at that section."""
    prefix = "" if on_home else "./"
    links = '<nav class="top-nav" aria-label="Sections">' + "".join(
        f'<a href="{prefix}#{anchor}"{' class="wide-only"' if anchor == "qa" else ""}>{both(en, bn)}</a>'
        for anchor, en, bn in [("how", "How it works", "কীভাবে"), ("adda-h", "Adda Tables", "আড্ডা টেবিল"),
                               ("safe", "Safety", "নিরাপত্তা"), ("qa", "Questions", "প্রশ্ন")]) + \
        f'<a href="join.html">{both("Join us", "যুক্ত হোন")}</a></nav>'
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
    items = [(INSTAGRAM_URL, INSTAGRAM_ICON, "Instagram", INSTAGRAM_HANDLE),
             (FACEBOOK_URL, FACEBOOK_ICON, "Facebook", "Mon Mela")]
    items = [item for item in items if item[0]]  # only pages that exist
    if not items:
        return ""
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
        (f"{home}#safe", "Safety", "নিরাপত্তা"), (f"{home}#qa", "Questions", "প্রশ্ন"),
        ("join.html", "Join us", "যুক্ত হোন")])
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
        "cap": '<path d="M2.5 9.5L12 5l9.5 4.5L12 14z"/><path d="M6.5 11.5v4c1.5 1.5 3.5 2.2 5.5 2.2s4-.7 5.5-2.2v-4M21.5 9.5v5"/>',
        "award": '<circle cx="12" cy="9" r="5"/><path d="M9 13.5L7.5 21l4.5-2.5 4.5 2.5-1.5-7.5"/>',
        "star": '<path d="M12 3.5l2.6 5.3 5.8.8-4.2 4.1 1 5.8-5.2-2.7-5.2 2.7 1-5.8-4.2-4.1 5.8-.8z"/>',
        "spark": '<path d="M12 3v4M12 17v4M3 12h4M17 12h4M6 6l2.5 2.5M15.5 15.5L18 18M18 6l-2.5 2.5M8.5 15.5L6 18"/>',
        "cup": '<path d="M5 9h11v5a5 5 0 0 1-5 5h-1a5 5 0 0 1-5-5z"/><path d="M16 11h1.5a2.5 2.5 0 0 1 0 5H16M8 3.5c0 1.5 1.5 1.5 1.5 3M12 3.5c0 1.5 1.5 1.5 1.5 3"/>',
        "ball": '<circle cx="12" cy="12" r="8.5"/><path d="M12 3.5v17M3.5 12h17M6 6c3 2 3 10 0 12M18 6c-3 2-3 10 0 12"/>',
        "fest": '<path d="M4 20l4-12 8 8z"/><path d="M14 4v2M18 6l-1.5 1.5M20 10h-2"/>',
        "music": '<path d="M9 18V6l11-2v12"/><circle cx="6.5" cy="18" r="2.5"/><circle cx="17.5" cy="16" r="2.5"/>',
        "food": '<path d="M7 3v8M4.5 3v5a2.5 2.5 0 0 0 5 0V3M7 11v10M17 21V3c-2.5 1.5-3.5 4.5-3.5 8h3.5"/>',
        "travel": '<path d="M3 14l18-7-4 13-5-5-4 2 1-4z"/>',
        "book": '<path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H20v15H6.5A2.5 2.5 0 0 0 4 20.5z"/><path d="M4 20.5A2.5 2.5 0 0 1 6.5 18H20v3H6.5"/>',
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


# The story section: three moments of one friendship (cut from six, Nov 2026, to keep the page short).
# Pictures: img/story-1…3.webp, 1600 x 900 photos
# (supplied Nov 2026; they replaced the drawings by tools/make_story.py). Also used on the Join us cards.
# (big title in Bengali, its English line, text in English, text in Bengali, picture alt text)
STORY = [
    ("নতুন শহর", "A new city",
     "New job, new city, and evenings at the window. Everyone is busy, and there's no one to share a bhaar of cha with.",
     "নতুন চাকরি, নতুন শহর, সন্ধেগুলো কাটে জানলার ধারে। সবাই ব্যস্ত, এক ভাঁড় চা খাওয়ার সঙ্গী নেই।",
     "A young man at his desk at night looks out of the window at Howrah Bridge under a full moon"),
    ("একটা হ্যালো", "A hello",
     "Mon Mela shows someone nearby who also loves café adda and the hills. A wave, a wave back, and the chat opens.",
     "মনমেলা দেখাল কাছেই এমন একজনকে, যিনিও ক্যাফের আড্ডা আর পাহাড় ভালোবাসেন। হাত নাড়া, উত্তরে হাত নাড়া, আর চ্যাট খুলে গেল।",
     "Friends laughing at a cafe table in the evening, a phone on the table in front"),
    ("প্রথম আড্ডা", "The first adda",
     "Saturday, 5 pm, the para tea stall. Two cups of cha became six, and nobody looked at the time.",
     "শনিবার, বিকেল ৫টা, পাড়ার চায়ের দোকান। দু'ভাঁড় চা গড়াল ছ'ভাঁড়ে, ঘড়ি দেখল না কেউ।",
     "Six friends on a bench at a lit tea stall in the evening, a tram passing behind"),
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
    """Three chapters. Phones (and no JavaScript): each chapter is a picture card with its text.
    Wide screens with story.js: the pictures sit in one sticky frame on the right and cross-fade
    as each chapter scrolls past on the left."""
    chapters, frame, dots = [], [], []
    # Where each photo's people are, so the 3:2 frame keeps them in view (CSS object-position).
    focus = ["80% 50%", "60% 50%", "50% 55%", "45% 55%", "55% 55%", "55% 60%"]
    for i, (title_bn, title_en, en, bn, alt) in enumerate(STORY):
        src = asset(f"img/story-{i + 1}.webp")
        pos = f' style="object-position: {focus[i]}"'
        cta = f'<div class="actions">{get_app_button()}</div>' if i == len(STORY) - 1 else ""
        chapters.append(
            f'<li class="chapter" data-i="{i}">'
            f'<figure class="ch-pic"><img src="{src}" alt="{alt}" width="1600" height="900"{pos} loading="lazy" decoding="async"></figure>'
            f'<div class="ch-text"><h3><span class="ch-bn" lang="bn">{title_bn}</span>'
            f'<span class="ch-en l" lang="en">{title_en}</span></h3><p>{both(en, bn)}</p>{cta}</div></li>')
        frame.append(f'<img class="sf-pic{" on" if i == 0 else ""}" src="{src}" alt="" width="1600" height="900"{pos} loading="lazy" decoding="async">')
        dots.append(f'<span{" class=\"on\"" if i == 0 else ""}></span>')
    return f"""<section class="story" aria-labelledby="story-h">
    <div class="story-head">
      <h2 id="story-h">{both("A story of friendship", "একটা বন্ধুত্বের গল্প")}</h2>
      <p>{both("Three small moments, the way friendships start in Bengal.", "তিনটে ছোট মুহূর্ত, বাংলায় যেভাবে বন্ধুত্ব শুরু হয়।")}</p>
      {music_button()}
      <p class="music-tune" hidden>{both("Tune: Purano Sei Diner Kotha", "সুর: পুরানো সেই দিনের কথা")}</p>
    </div>
    <div class="story-body">
      <ol class="story-chapters">{"".join(chapters)}</ol>
      <div class="story-frame" aria-hidden="true"><div class="sf-pics">{"".join(frame)}</div><div class="sf-dots">{"".join(dots)}</div></div>
    </div>
  </section>"""


# ---------------------------------------------------------------- home page pieces (Nov 2026 redesign)

# Three short marigold strokes, like a hand-drawn "shine" mark beside a heading.
SPARK = ('<svg class="spark" viewBox="0 0 40 40" aria-hidden="true"><path d="M20 4v9M6 12l6 6M34 12l-6 6"/></svg>')
# A brush-stroke underline under the hero's Bengali line.
SWOOSH = ('<svg class="swoosh" viewBox="0 0 300 20" preserveAspectRatio="none" aria-hidden="true">'
          '<path d="M4 15C80 5 180 3 296 9"/></svg>')

# The five feature cards' drawings: flat shapes in the site's colours (viewBox 96 x 72).
GIVES_ART = {
    # three friends, arms round each other
    "people": '<path d="M14 66c0-16 6-26 14-26s14 10 14 26z" fill="#F5B023"/><path d="M54 66c0-16 6-26 14-26s14 10 14 26z" fill="#D9482B"/>'
              '<path d="M34 66c0-18 6-29 14-29s14 11 14 29z" fill="#0F766E"/>'
              '<circle cx="28" cy="25" r="8" fill="#8D5524"/><circle cx="48" cy="21" r="8.5" fill="#A0673A"/><circle cx="68" cy="25" r="8" fill="#6B3E1F"/>'
              '<path d="M20 24a8 8 0 0 1 16-2c-5-3-11-2-16 2z" fill="#13201E"/><path d="M39.5 20a8.5 8.5 0 0 1 17-1c-5-3-12-3-17 1z" fill="#13201E"/>'
              '<path d="M60 25a8 8 0 0 1 16-3c-2 4-2 10 1 14-6-1-12-5-17-11z" fill="#13201E"/>',
    # a small round table with two bhaars of cha, and seats around it
    "table": '<ellipse cx="48" cy="40" rx="30" ry="9" fill="#0F766E"/><rect x="45" y="44" width="6" height="20" rx="2" fill="#115E59"/>'
             '<rect x="34" y="62" width="28" height="5" rx="2.5" fill="#115E59"/>'
             '<path d="M36 24h10l-2 12h-6z" fill="#C2552D"/><path d="M52 22h10l-2 13h-6z" fill="#C2552D"/>'
             '<path d="M40 19c0-4 3-4 3-8M56 17c0-4 3-4 3-8" stroke="#B9D6CF" stroke-width="2" stroke-linecap="round" fill="none"/>'
             '<circle cx="12" cy="44" r="6" fill="#F5B023"/><circle cx="84" cy="44" r="6" fill="#F5B023"/>'
             '<circle cx="22" cy="60" r="6" fill="#F5B023"/><circle cx="74" cy="60" r="6" fill="none" stroke="#F5B023" stroke-width="2.5"/>',
    # a tea stall with a striped awning: hosting your own adda
    "stall": '<rect x="18" y="30" width="60" height="36" rx="3" fill="#0F766E"/><rect x="26" y="40" width="18" height="16" rx="2" fill="#FCEBC1"/>'
             '<rect x="52" y="40" width="18" height="26" rx="2" fill="#115E59"/>'
             '<path d="M12 18h72l-4 14H16z" fill="#FFF6E5"/>'
             '<path d="M12 18h12l-1 14h-7zM36 18h12v14H36zM60 18h12l1 14h-12z" fill="#D9482B"/>'
             '<path d="M16 32q3 5 7 0q3 5 7 0q3 5 7 0q3 5 7 0q3 5 7 0q3 5 7 0q3 5 7 0q3 5 7 0q3 5 6 0" fill="#D9482B"/>'
             '<rect x="10" y="12" width="76" height="7" rx="3" fill="#F5B023"/>',
    # a shield with a tick: safe by design
    "shield": '<path d="M48 6l26 9v18c0 16-11 28-26 34C33 61 22 49 22 33V15z" fill="#0F766E"/>'
              '<path d="M48 13l19 7v13c0 12-8 21-19 26-11-5-19-14-19-26V20z" fill="none" stroke="#F5B023" stroke-width="3"/>'
              '<path d="M38 36l7 7 14-15" stroke="#FFF6E5" stroke-width="5" stroke-linecap="round" stroke-linejoin="round" fill="none"/>',
    # a phone saying অ and A: made for Bengal, in two languages
    "phone": '<rect x="30" y="4" width="36" height="64" rx="8" fill="#13201E"/><rect x="34" y="11" width="28" height="50" rx="4" fill="#FFF6E5"/>'
             '<text x="48" y="31" font-size="16" font-weight="700" fill="#0F766E" font-family="Anek Bangla, sans-serif" text-anchor="middle">অ</text>'
             '<text x="48" y="49" font-size="14" font-weight="700" fill="#D9482B" font-family="Anek Bangla, sans-serif" text-anchor="middle">A</text>'
             '<rect x="41" y="53" width="14" height="3" rx="1.5" fill="#F5B023"/>',
}

# The closing band's line drawing: Victoria Memorial and Howrah Bridge (marigold, 320 x 90).
SKYLINE = ('<svg class="skyline" viewBox="0 0 320 90" aria-hidden="true">'
           '<path d="M2 86h316"/>'
           # Victoria Memorial: wings, a central dome with its lantern and angel, two corner cupolas
           '<path d="M8 86V64h104v22M8 64h104M20 64V56h80v8M44 56c0-18 32-18 32 0M60 38v-8M57 30h6M60 30l3-5"/>'
           '<path d="M16 64v-6c0-5 8-5 8 0v6M96 64v-6c0-5 8-5 8 0v6M28 86V72M40 86V72M52 86V72M68 86V72M80 86V72M92 86V72"/>'
           # Howrah Bridge: two towers, the cantilever arms and the deck
           '<path d="M168 86V30M178 86V30M262 86V30M272 86V30M168 30h10M262 30h10"/>'
           '<path d="M130 70h182M130 70l38-40M178 30l42 24 42-24M312 70l-40-40M178 46l84 0M150 70l18-18M290 70l-18-18"/>'
           '<path d="M188 36v34M200 43v27M212 50v20M228 50v20M240 43v27M252 36v34"/>'
           '</svg>')


def home_hero():
    """The hero: our friends photo on the right, fading into dusk on the left where the words are,
    and a soft wave into the cream page below. The Bengali line is in the same brush script on both
    language versions; the lede says it in English for English readers."""
    photo = HERO_PHOTO if (ROOT / HERO_PHOTO).exists() else HERO_PHOTO_FALLBACK
    trust = [("badge", "Photo-verified members", "ছবি-যাচাই করা সদস্য"), ("adult", "18+ only", "শুধু ১৮+"),
             ("star", "Free, no ads", "বিনামূল্যে, বিজ্ঞাপন নেই")]
    trust_html = "".join(f"<li>{icon(i)}{both(en, bn)}</li>" for i, en, bn in trust)
    return f"""<section class="hero-m">
  <div class="hero-m-photo"><img src="{asset(photo)}" alt="" width="1600" height="900" fetchpriority="high"></div>
  <div class="hero-m-text">
    {SPARK}
    <h1>{both("Mon Mela", "মনমেলা")}</h1>
    <p class="hero-m-script" lang="bn">মন মিললে, বন্ধু মেলে।{SWOOSH}</p>
    <p class="lede">{both(
        "Find friends nearby who love what you love. Join small addas, host your own, and be part of Bengal's friendliest community.",
        "কাছেপিঠে মনের মতো বন্ধু খুঁজুন। ছোট আড্ডায় যোগ দিন, নিজেই আড্ডা বসান, আর হয়ে উঠুন বাংলার সবচেয়ে বন্ধুত্বপূর্ণ দলের অংশ।")}</p>
    <div class="actions">{get_app_button("btn btn-primary btn-big")}</div>
    <ul class="hero-m-trust">{trust_html}</ul>
  </div>
  <svg class="hero-m-wave" viewBox="0 0 1440 90" preserveAspectRatio="none" aria-hidden="true"><path d="M0 46C260 96 560 6 900 40c220 22 380 26 540-6v56H0z"/></svg>
</section>"""


def home_hero_poster():
    """The poster hero: one wide photo of friends round a phone at the ghat. Four chips sit where the
    photo's dashed lines lead (the same spots as in the original artwork, in % of the picture). Phones get a closer crop of the
    friends and no chips."""
    chips = [  # icon, English, Bengali, left %, top %, width %, height %
        ("people", "Find your people", "নিজের মানুষ খুঁজুন", 19.9, 17.6, 14.6, 10.1),
        ("cup", "Join an Adda Table", "আড্ডা টেবিলে যোগ দিন", 44.3, 11.4, 15.5, 9.5),
        ("star", "Host your own adda", "নিজেই আড্ডা বসান", 74.8, 23.6, 16.1, 9.8),
        ("badge", "Photo-verified members", "ছবি-যাচাই করা সদস্য", 4.8, 39.0, 16.7, 10.9),
    ]
    chips_html = "".join(
        f'<li style="left:{l}%;top:{t}%;width:{w}%;height:{h}%">{icon(i)}<span>{both(en, bn)}</span></li>'
        for i, en, bn, l, t, w, h in chips)
    return f"""<section class="hero-p">
  <div class="hero-p-frame">
    <picture>
      <source media="(max-width: 760px)" srcset="{asset("img/hero-poster-m.webp")}" width="890" height="691">
      <img src="{asset("img/hero-poster.webp")}" alt="Five friends laughing round a phone on the ghat steps at dusk, Howrah Bridge behind them"
           width="1672" height="941" fetchpriority="high">
    </picture>
    <ul class="hero-p-chips" aria-hidden="true">{chips_html}</ul>
    <!-- The picture speaks for itself (the header has the app button). The heading is for screen
         readers and search engines. -->
    <h1 class="sr-only">{both("Mon Mela: friends and adda meetups in West Bengal", "মনমেলা: পশ্চিমবঙ্গে বন্ধু আর আড্ডা")}</h1>
  </div>
  <svg class="hero-m-wave" viewBox="0 0 1440 90" preserveAspectRatio="none" aria-hidden="true"><path d="M0 46C260 96 560 6 900 40c220 22 380 26 540-6v56H0z"/></svg>
</section>"""


def home_hero_light():
    """The bright home page hero: the raw riverside photo (img/home-hero.webp, made by
    tools/make_home_photo.py), the big name and its line over a soft haze on the left, then the five
    round icons as a real HTML row under the picture, so they wrap to fit any screen."""
    # (icon file number, English, Bengali)
    icons = [
        (1, "Find your<br>people", "নিজের<br>মানুষ খুঁজুন"),
        (2, "Join<br>addas", "আড্ডায়<br>যোগ দিন"),
        (3, "Explore<br>your city", "নিজের শহর<br>ঘুরে দেখুন"),
        (4, "Safe and<br>trusted", "নিরাপদ আর<br>ভরসার"),
        (5, "Feel at<br>home", "আপন<br>মনে হবে"),
    ]
    row = "".join(f'<li><img src="{asset(f"img/home-icon-{n}.png")}" alt="" width="74" height="74"><span>{both(en, bn)}</span></li>'
                  for n, en, bn in icons)
    return f"""<section class="hero-l">
  <div class="hero-l-frame">
    <picture>
      <source media="(max-width: 760px)" srcset="{asset("img/home-hero-m.webp")}" width="1080" height="647">
      <img src="{asset("img/home-hero.webp")}" alt="Five friends laughing round a phone on the grass by the river at sunset, Howrah Bridge behind them"
           width="1884" height="835" fetchpriority="high">
    </picture>
    <div class="hero-l-text">
      <h1>{both("Mon Mela", "মনমেলা")}</h1>
      <p>{both("Find your people, join addas, and be a part of Bengal's friendliest community.",
               "নিজের মানুষ খুঁজুন, আড্ডায় যোগ দিন, আর হয়ে উঠুন বাংলার সবচেয়ে বন্ধুত্বপূর্ণ দলের অংশ।")}{SWOOSH}</p>
    </div>
    <svg class="hero-l-wave" viewBox="0 0 1440 90" preserveAspectRatio="none" aria-hidden="true"><path d="M0 52C240 6 520 4 760 30c260 28 470 40 680 2v58H0z"/></svg>
  </div>
  <ul class="hero-l-row">{row}</ul>
</section>"""


def home_match():
    """Matched by what you share: the words and a strip of common interests on the left, two
    profile cards with their match % on the right (img/match-cards.webp, a transparent picture),
    and the line that says what they share. Same dusk green as the story and the footer."""
    interests = [("book", "Bengali<br>books", "বাংলা<br>বই"), ("music", "Music &amp;<br>movies", "গান আর<br>সিনেমা"),
                 ("food", "Food<br>lovers", "খেতে<br>ভালোবাসি"), ("ball", "Football", "ফুটবল"),
                 ("travel", "Travel<br>in WB", "বাংলায়<br>ঘোরা")]
    chips = "".join(f"<li>{icon(i)}<span>{both(en, bn)}</span></li>" for i, en, bn in interests)
    return f"""<section class="match2" aria-labelledby="match-h">
    <img class="match2-city" src="{asset("img/match-city.webp")}" alt="" width="1080" height="686" loading="lazy">
    <div class="match2-inner">
      <div class="match2-text">
        <h2 id="match-h">{both("Matched by what you share", "মিল খুঁজে দেয় আপনার উত্তর")}{SWOOSH}</h2>
        <p>{both("From adda topics to favourite music, we find people in West Bengal who share your vibe. "
                 "Every suggestion shows a match % and what you have in common, so the first message is easy.",
                 "আড্ডার বিষয় থেকে প্রিয় গান, পশ্চিমবঙ্গে আপনার মনের মতো মানুষ খুঁজে দিই আমরা। প্রতিটি সাজেশনে "
                 "থাকে মিলের % আর কোথায় কোথায় মিল, তাই প্রথম মেসেজটা লেখা সহজ।")}</p>
        <div class="interests"><b>{both("Common <br>interests:", "যেসব <br>মিল খুঁজি:")}</b><ul>{chips}</ul></div>
      </div>
      <figure class="match2-art">
        <picture>
          <source media="(max-width: 760px)" srcset="{asset("img/match-cards-m.webp")}">
          <img src="{asset("img/match-cards.webp")}" width="1316" height="895" loading="lazy"
               alt="Two profile cards, Arka and Mousumi from Kolkata, with an 86% match between them">
        </picture>
        <figcaption><span class="pill">{both("You both love adda and Kolkata!",
                                 "আপনাদের দুজনেরই প্রিয় আড্ডা আর কলকাতা!")}</span></figcaption>
      </figure>
    </div>
  </section>"""


def home_how():
    """How it works in three steps, each with its drawing, over the green Kolkata skyline."""
    steps = [
        ("how-1", "Create your profile", "প্রোফাইল তৈরি করুন",
         "Tell us about yourself: your interests, city and more.", "নিজের কথা বলুন: আপনার শখ, শহর আর আরও অনেক কিছু।"),
        ("how-2", "Find and join addas", "আড্ডা খুঁজুন, যোগ দিন",
         "Join an Adda Table nearby, or host your own.", "কাছের আড্ডা টেবিলে যোগ দিন, বা নিজেই বসান।"),
        ("how-3", "Make new friends", "নতুন বন্ধু পান",
         "Chat, meet and enjoy great conversations.", "চ্যাট করুন, দেখা করুন, জমিয়ে আড্ডা দিন।"),
    ]
    lis = "".join(
        f"""<li><div><h3>{both(t_en, t_bn)}</h3><p>{both(d_en, d_bn)}</p></div>
      <img src="{asset(f"img/{img}.webp")}" alt="" loading="lazy"></li>"""
        for img, t_en, t_bn, d_en, d_bn in steps)
    return f"""<section class="how-l" id="how" aria-labelledby="how-h">
    <h2 id="how-h">{SPARK}<span>{both("How Mon Mela works", "মনমেলা কীভাবে কাজ করে")}</span>{SPARK}</h2>
    <ol>{lis}</ol>
    <img class="skyline-strip" src="{asset("img/skyline-strip.webp")}" alt="" loading="lazy" width="1672" height="103">
  </section>"""


def home_gives():
    """Five cards right under the hero: what the app gives you, each with a small drawing."""
    cards = [
        ("people", "lilac", "Find your people", "নিজের মানুষ খুঁজুন",
         "New picks every morning, with a match % and why you click.",
         "প্রতিদিন সকালে নতুন মানুষ, সঙ্গে মিলের % আর কেন মিল।"),
        ("table", "haldi", "Join an Adda Table", "আড্ডা টেবিলে যোগ দিন",
         "Small meetups of 3 to 6 at a cafe, a park or a phuchka stall.",
         "ক্যাফে, পার্ক বা ফুচকার দোকানে ৩ থেকে ৬ জনের ছোট আড্ডা।"),
        ("stall", "peach", "Host your own adda", "নিজেই আড্ডা বসান",
         "Pick the topic, place and seats, and you choose who joins.",
         "বিষয়, জায়গা আর আসন ঠিক করুন, কে আসবেন তাও আপনি ঠিক করেন।"),
        ("shield", "mint", "Safe by design", "শুরু থেকেই নিরাপদ",
         "Photo-verified members, private meeting spots and two-tap reporting.",
         "ছবি-যাচাই করা সদস্য, গোপন দেখার জায়গা আর দু-ট্যাপে রিপোর্ট।"),
        ("phone", "rose", "Made for Bengal", "বাংলার জন্য তৈরি",
         "In Bengali and English, from Kolkata to Cooch Behar.",
         "বাংলা আর ইংরেজিতে, কলকাতা থেকে কোচবিহার।"),
    ]
    lis = "".join(
        f'<li class="gv-{tint}"><svg class="gv-art" viewBox="0 0 96 72" aria-hidden="true">{GIVES_ART[art]}</svg>'
        f"<h3>{both(t_en, t_bn)}</h3><p>{both(d_en, d_bn)}</p></li>"
        for art, tint, t_en, t_bn, d_en, d_bn in cards)
    return f"""<section class="gives" aria-labelledby="gives-h">
    <div class="gives-head">
      <h2 id="gives-h">{SPARK}<span>{both("What Mon Mela gives you", "মনমেলা আপনাকে যা দেয়")}</span>{SPARK}</h2>
      <p>{both("A whole city of addas, in your pocket.", "গোটা শহরের আড্ডা, আপনার পকেটে।")}</p>
    </div>
    <ul class="gives-row">{lis}</ul>
  </section>"""


def home_ready():
    """The closing band before the footer: skyline drawing, one line, the app button."""
    return f"""<section class="ready" aria-labelledby="ready-h">
    <div class="ready-inner">
      {SKYLINE}
      <div class="ready-text">
        <h2 id="ready-h">{both("Ready to be part of Mon Mela?", "মনমেলার অংশ হতে তৈরি?")}</h2>
        <p>{both("Download the app and find your adda.", "অ্যাপটা নিন, আর খুঁজে নিন আপনার আড্ডা।")}</p>
      </div>
      {get_app_button("btn btn-primary btn-big")}
    </div>
  </section>"""


def with_home_brand(html):
    """The home page under HOME_BRAND's name (both languages); other pages keep Mon Mela."""
    if not HOME_BRAND:
        return html
    return html.replace("Mon Mela", HOME_BRAND[0]).replace("মনমেলা", HOME_BRAND[1])


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
    html = f"""{head(HOME_TITLE_EN, HOME_TITLE_BN, HOME_DESCRIPTION, "", script("story.js") + script("motion.js") + home_schema(faq))}
<body class="home">
{header(on_home=True)}
{home_hero_light() if HERO_STYLE == "light" else home_hero_poster() if HERO_STYLE == "poster" else home_hero()}

<main class="home-main">
  {home_how() if HERO_STYLE == "light" else home_gives()}

  {story_section()}

  <section class="how" aria-labelledby="inside">
    <h2 id="inside">{both("Inside the app", "অ্যাপের ভেতরে")}</h2>
    <ol class="how-row">{steps_html}</ol>
    <p class="how-then">{icon("chat")}<span>{both("<b>Then connect.</b> The chat opens only when both of you say yes.",
                                                  "<b>তারপর কানেক্ট।</b> দুজনেই রাজি হলে তবেই চ্যাট খোলে।")}</span></p>
  </section>

{home_match()}

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

  {home_ready()}
</main>
{footer(on_home=True)}
</body>
</html>
"""
    (ROOT / "index.html").write_text(with_home_brand(html), encoding="utf-8")


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
                "sameAs": [url for url in (INSTAGRAM_URL, FACEBOOK_URL) if url],
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
    paths = ["", "download", "join", "ambassador", "partners", "creators", "host", "privacy.html", "terms.html", "delete-account.html", "child-safety.html"]
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
                    "adda", '<meta name="robots" content="noindex">' + chr(10) + script("adda.js"))}
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


def form_link(role, body):
    """The join form with this role pre-picked; until the form exists, an e-mail to us with the questions."""
    label = ROLES[role]
    if JOIN_FORM_URL:
        prefill = f"?usp=pp_url&{JOIN_FORM_ROLE_ENTRY}={quote(label)}" if JOIN_FORM_ROLE_ENTRY else ""
        return JOIN_FORM_URL + prefill, ' target="_blank" rel="noopener"'
    return f"mailto:{EMAIL}?subject={quote(label + ' - Mon Mela')}&body={quote(body)}", ""


def bullet_list(items):
    """A plain list of (English, Bengali) lines, marigold markers."""
    return "<ul>" + "".join(f"<li>{both(en, bn)}</li>" for en, bn in items) + "</ul>"


def icon_list(items):
    """Icon + title + line items (the "What you get" style)."""
    return "<ul>" + "".join(f"<li>{icon(i)}<div><h3>{both(t_en, t_bn)}</h3><p>{both(d_en, d_bn)}</p></div></li>"
                            for i, t_en, t_bn, d_en, d_bn in items) + "</ul>"


def join_page(file, path, title, description, intro, art, main):
    """Shared frame of the ambassador and partner pages: dusk intro with an Adda Table card pair, then sections."""
    h1_en, h1_bn, lede_en, lede_bn, button, meta = intro
    html = f"""{head(*title, description, path)}
<body class="home join">
{header()}
<section class="intro">
  {festoon()}
  <div class="intro-inner">
    <div>
      <h1>{both(h1_en, h1_bn)}</h1>
      <p class="lede">{both(lede_en, lede_bn)}</p>
      <div class="actions">{button}</div>
      <p class="dl-meta">{both(*meta)}</p>
    </div>
    <div class="adda-art join-art" aria-hidden="true">{art}</div>
  </div>
</section>
<main class="home-main">
{main}
</main>
{footer()}
</body>
</html>
"""
    (ROOT / file).write_text(html, encoding="utf-8")


def steps_list(items):
    """A numbered run of steps (the download page's dashed-line style), each with a title and a line."""
    lis = "".join(f"<li><h3>{both(t_en, t_bn)}</h3><p>{both(d_en, d_bn)}</p></li>" for t_en, t_bn, d_en, d_bn in items)
    return f"<ol>{lis}</ol>"


def ambassador():
    """monmela.in/ambassador: the Founding Ambassador programme for college students (tried here first,
    then moved to monmela.in)."""
    href, target = form_link("ambassador",
                             "Name:\nCollege:\nCourse and year:\nAge:\nPhone / WhatsApp:\n"
                             "Clubs or groups you run or are part of:\nThe first adda you'd host on campus:\n"
                             "Android phone (yes/no):\nInstagram (optional):\n")
    apply_btn = lambda cls: f'<a class="btn {cls}" href="{href}"{target}>{both("Apply now", "আবেদন করুন")}</a>'

    steps = steps_list([
        ("Try the app before launch", "লঞ্চের আগেই অ্যাপ চালান",
         "We add you to the test. Use it for a week and tell us what to fix.",
         "আমরা আপনাকে টেস্টে যোগ করব। এক সপ্তাহ ব্যবহার করে বলুন কী ঠিক করা দরকার।"),
        ("Plan two campus addas", "ক্যাম্পাসে দুটো আড্ডার পরিকল্পনা",
         "A cha adda after class, a fest-prep meetup, a match screening: pick the date and place with us.",
         "ক্লাসের পর চায়ের আড্ডা, ফেস্টের প্রস্তুতি, খেলা দেখা: তারিখ আর জায়গা আমাদের সঙ্গে ঠিক করুন।"),
        ("Host them in launch week", "লঞ্চের সপ্তাহে আড্ডা বসান",
         "Open them as Adda Tables in the app and welcome the people who join.",
         "অ্যাপে আড্ডা টেবিল হিসেবে খুলুন, আর যাঁরা আসেন তাঁদের স্বাগত জানান।"),
        ("Bring your people", "নিজের লোকেদের আনুন",
         "From launch day, invite 10 classmates, and send us a short voice note each week.",
         "লঞ্চের দিন থেকে ১০ জন সহপাঠীকে ডাকুন, আর প্রতি সপ্তাহে একটা ছোট ভয়েস নোট পাঠান।"),
    ])
    perks = [
        ("award", "Founding Ambassador certificate", "ফাউন্ডিং অ্যাম্বাসাডর সার্টিফিকেট",
         "Signed by the founder, plus a LinkedIn recommendation when you finish all four steps.",
         "প্রতিষ্ঠাতার সই করা, আর চারটে ধাপ শেষ করলে LinkedIn-এ সুপারিশ।"),
        ("star", "Your name on this page", "এই পেজে আপনার নাম",
         "With your college, and a shout-out on our Instagram, if you agree.",
         "কলেজের নাম সহ, আর আপনি রাজি থাকলে আমাদের Instagram-এ উল্লেখ।"),
        ("spark", "Free premium for life", "সারাজীবন বিনামূল্যে প্রিমিয়াম",
         "Whatever premium features come later, you never pay for them.",
         "পরে যে প্রিমিয়াম ফিচারই আসুক, আপনাকে কখনও টাকা দিতে হবে না।"),
        ("chat", "A real say in the app", "অ্যাপে আপনার কথার দাম",
         "Talk to the founder directly, try new features first, and shape what we build.",
         "সরাসরি প্রতিষ্ঠাতার সঙ্গে কথা বলুন, নতুন ফিচার সবার আগে চালান, আর ঠিক করুন আমরা কী বানাব।"),
        ("people", "A path to City Lead", "সিটি লিড হওয়ার সুযোগ",
         "After 30 days, the most active ambassador leads the next campuses in the city.",
         "৩০ দিন পরে সবচেয়ে সক্রিয় অ্যাম্বাসাডর শহরের পরের ক্যাম্পাসগুলোর দায়িত্ব নেবেন।"),
    ]
    perks_html = "".join(f"<li>{icon(i)}<div><h3>{both(t_en, t_bn)}</h3><p>{both(d_en, d_bn)}</p></div></li>"
                         for i, t_en, t_bn, d_en, d_bn in perks)

    def bullets(items):
        return "<ul>" + "".join(f"<li>{both(en, bn)}</li>" for en, bn in items) + "</ul>"

    who = bullets([
        ("College students in West Bengal, 18 or older", "পশ্চিমবঙ্গের কলেজ পড়ুয়া, বয়স ১৮ বা তার বেশি"),
        ("You already run or join things: a club, fest team, hostel group, sports team or quiz society",
         "আপনি আগে থেকেই কিছু চালান বা তাতে আছেন: ক্লাব, ফেস্ট টিম, হস্টেলের দল, খেলার দল বা কুইজ সোসাইটি"),
        ("An Android phone", "একটা অ্যান্ড্রয়েড ফোন"),
    ])
    know = bullets([
        ("This is an unpaid volunteer role. There's no stipend, salary or job offer.",
         "এটা অবৈতনিক স্বেচ্ছাসেবী ভূমিকা। কোনো স্টাইপেন্ড, বেতন বা চাকরির প্রস্তাব নেই।"),
        ("Addas happen in public places only, like cafes, canteens and sports grounds.",
         "আড্ডা হয় শুধু সবার জন্য খোলা জায়গায়, যেমন ক্যাফে, ক্যান্টিন আর খেলার মাঠ।"),
        ("We never ask you to add people to groups or to share anyone's number.",
         "আমরা কখনও কাউকে গ্রুপে যোগ করতে বা কারও নম্বর দিতে বলি না।"),
        ("After you apply, we call you within a few days for a 10-minute chat.",
         "আবেদনের পর কয়েক দিনের মধ্যে ১০ মিনিট কথা বলতে আমরা ফোন করব।"),
    ])

    main = f"""  <section class="steps" aria-labelledby="do">
    <h2 id="do">{both("What you'll do", "আপনার কাজ")}</h2>
    {steps}
  </section>
  <section class="perks" aria-labelledby="get">
    <h2 id="get">{both("What you get", "আপনি যা পাবেন")}</h2>
    <ul>{perks_html}</ul>
  </section>
  <section class="fit">
    <div><h2>{both("Who can apply", "কারা আবেদন করতে পারেন")}</h2>{who}</div>
    <div><h2>{both("Good to know", "জেনে রাখুন")}</h2>{know}</div>
  </section>
  <section class="cta-band">
    {festoon()}
    <h2>{both("Your campus, your adda", "আপনার ক্যাম্পাস, আপনার আড্ডা")}</h2>
    <p>{both("We're starting with a few colleges. Apply now to be one of the first.",
             "আমরা কয়েকটা কলেজ দিয়ে শুরু করছি। প্রথম দিকের একজন হতে এখনই আবেদন করুন।")}</p>
    <div class="actions">{apply_btn("btn-primary btn-big")}</div>
  </section>"""

    join_page("ambassador.html", "ambassador",
              ("Campus Ambassador programme | Mon Mela", "ক্যাম্পাস অ্যাম্বাসাডর প্রোগ্রাম | মনমেলা"),
              "Become a Founding Ambassador of Mon Mela: plan small addas on your campus and lead the launch at your college.",
              ("Bring adda back to your campus", "ক্যাম্পাসে আবার আড্ডা জমান",
               "Become a Founding Ambassador of Mon Mela. Plan small addas with people from your college, "
               "help shape the app before it opens to everyone, and lead its launch on your campus.",
               "মনমেলার ফাউন্ডিং অ্যাম্বাসাডর হোন। কলেজের মানুষদের সঙ্গে ছোট ছোট আড্ডার পরিকল্পনা করুন, "
               "সবার জন্য খোলার আগেই অ্যাপটা গড়তে সাহায্য করুন, আর নিজের ক্যাম্পাসে লঞ্চের নেতৃত্ব দিন।",
               apply_btn("btn-primary btn-big"),
               ("A 30-day volunteer pilot for college students aged 18 and over.",
                "১৮ বা তার বেশি বয়সী কলেজ পড়ুয়াদের জন্য ৩০ দিনের স্বেচ্ছাসেবী পাইলট।")),
              adda_card("back", "Fest-prep adda, campus lawn", "ফেস্টের প্রস্তুতি আড্ডা, ক্যাম্পাসের লন",
                        "Friday, 4 pm", "শুক্রবার, বিকেল ৪টে", 3, 6, full=False)
              + adda_card("front", "Cha after class, college canteen", "ক্লাসের পর চা, কলেজ ক্যান্টিন",
                          "Wednesday, 5 pm", "বুধবার, বিকেল ৫টা", 3, 5,
                          tag=("Campus adda", "ক্যাম্পাস আড্ডা")),
              main)


def partners():
    """monmela.in/partners: cafes, sports venues, college fests and communities that host our addas
    (tried here first, then moved to monmela.in)."""
    href, target = form_link("partner",
                             "Name of your place or group:\nType (cafe, restaurant, sports venue, fest, club, community):\n"
                             "Area:\nContact person:\nPhone:\nQuiet days and hours:\nA perk you could offer groups:\n")
    interest = both("I'm interested", "আমি আগ্রহী")
    interest_btn = lambda cls: f'<a class="btn {cls}" href="{href}"{target}>{interest}</a>'
    mail_btn = f'<a class="btn btn-ghost" href="mailto:{EMAIL}">{both("Write to us", "আমাদের লিখুন")}</a>'

    kinds = [
        ("cup", "Cafes and restaurants", "ক্যাফে আর রেস্তোরাঁ",
         "Groups on slow weekday evenings, and a mention on our Instagram",
         "সপ্তাহের ফাঁকা সন্ধেয় দল, আর আমাদের Instagram-এ উল্লেখ",
         "A table you can keep for a group, and a small perk, like a free cha refill",
         "একটা দলের জন্য একটা টেবিল, আর ছোট একটা সুবিধা, যেমন আরেক কাপ চা ফ্রি"),
        ("ball", "Sports venues", "খেলার জায়গা",
         "Players for empty off-peak slots at your turf, court or club",
         "আপনার টার্ফ, কোর্ট বা ক্লাবের ফাঁকা স্লটে খেলোয়াড়",
         "A group rate in those slots", "সেই স্লটে দলের জন্য কম দাম"),
        ("fest", "College fests and clubs", "কলেজ ফেস্ট আর ক্লাব",
         "An ice-breaker corner where students meet new people, and help with promotion",
         "নতুন মানুষের সঙ্গে আলাপের একটা কর্নার, আর প্রচারে সাহায্য",
         "A small space at your event, and our name on your posters",
         "অনুষ্ঠানে একটু জায়গা, আর পোস্টারে আমাদের নাম"),
        ("book", "Communities", "কমিউনিটি",
         "Book clubs, running groups, quiz clubs: an easy way to bring new members to your meetups",
         "বইয়ের ক্লাব, দৌড়ের দল, কুইজ ক্লাব: আপনার মিটআপে নতুন সদস্য আনার সহজ উপায়",
         "One open Mon Mela meetup a month", "মাসে একটা সবার জন্য খোলা মনমেলা মিটআপ"),
    ]
    cards = "".join(f"""<li>{icon(i)}<h3>{both(t_en, t_bn)}</h3>
      <dl><dt>{both("You get", "আপনি পাবেন")}</dt><dd>{both(g_en, g_bn)}</dd>
      <dt>{both("We ask", "আমরা চাই")}</dt><dd>{both(a_en, a_bn)}</dd></dl></li>"""
                    for i, t_en, t_bn, g_en, g_bn, a_en, a_bn in kinds)

    steps = steps_list([
        ("Tell us about your place", "আপনার জায়গার কথা বলুন",
         "Your quiet days and hours, and what you can offer a group.",
         "কোন দিন আর কখন ফাঁকা থাকে, আর একটা দলকে কী দিতে পারেন।"),
        ("We point hosts to you", "আয়োজকদের আপনার কাছে পাঠাই",
         "When members plan an adda nearby, we suggest your place.",
         "কাছাকাছি কেউ আড্ডার পরিকল্পনা করলে আমরা আপনার জায়গার কথা বলি।"),
        ("Groups arrive", "দল আসে",
         "Small groups of photo-verified members come in, and with your permission we share the best moments on Instagram.",
         "ছবি-যাচাই করা সদস্যদের ছোট দল আসে, আর আপনার অনুমতি নিয়ে সেরা মুহূর্তগুলো আমরা Instagram-এ দিই।"),
    ])

    main = f"""  <section class="partner-kinds" aria-labelledby="who">
    <h2 id="who">{both("Who we work with", "কাদের সঙ্গে কাজ করি")}</h2>
    <ul>{cards}</ul>
  </section>
  <section class="steps" aria-labelledby="how">
    <h2 id="how">{both("How it works", "কীভাবে হয়")}</h2>
    {steps}
  </section>
  <section class="cta-band">
    {festoon()}
    <h2>{both("Let's talk", "চলুন কথা বলি")}</h2>
    <p>{both("Fill in a short form or write to us, and we'll get back to you within two days.",
             "একটা ছোট ফর্ম ভরুন বা আমাদের লিখুন, দু'দিনের মধ্যে উত্তর দেব।")}</p>
    <div class="actions">{interest_btn("btn-primary btn-big")}{mail_btn}</div>
  </section>"""

    join_page("partners.html", "partners",
              ("Partner with Mon Mela", "মনমেলার পার্টনার হোন"),
              "Cafes, sports venues, college fests and communities: host small Mon Mela meetups and welcome new groups.",
              ("Host addas with us", "আমাদের সঙ্গে আড্ডা জমান",
               "Mon Mela brings small, friendly groups of 4 to 6 people together at real places. "
               "Welcome them in your quiet hours, and we'll help them find you.",
               "মনমেলা ৪ থেকে ৬ জনের ছোট, বন্ধুত্বপূর্ণ দলকে আসল জায়গায় একসঙ্গে আনে। "
               "আপনার ফাঁকা সময়ে তাঁদের স্বাগত জানান, আর আমরা তাঁদের আপনার কাছে পৌঁছে দেব।",
               interest_btn("btn-primary btn-big"),
               ("No fees and no contracts. It starts with a conversation.",
                "কোনো ফি নেই, কোনো চুক্তি নেই। শুরুটা শুধু একটু কথা দিয়ে।")),
              adda_card("back", "Badminton and adda, Salt Lake", "ব্যাডমিন্টন আর আড্ডা, সল্টলেক",
                        "Sunday, 7 am", "রবিবার, সকাল ৭টা", 3, 4, full=False)
              + adda_card("front", "Board games and cha, a cafe near you", "বোর্ড গেম আর চা, কাছের ক্যাফেতে",
                          "Thursday, 6:30 pm", "বৃহস্পতিবার, সন্ধে ৬:৩০", 4, 6,
                          tag=("Partner cafe", "পার্টনার ক্যাফে")),
              main)


def card_picture(story_file):
    """A join card's picture: our own photo img/join-<n>.webp when it's there (n = the story picture's
    number), otherwise the home page story picture."""
    own = story_file.replace("story-", "join-")
    return own if (ROOT / own).exists() else story_file


def join_hub():
    """monmela.in/join: every way to be part of Mon Mela, one card each. Linked from the header
    and footer ("Join us"). Tried here first, then moved to monmela.in."""
    roles = [
        ("cap", "img/join-4.webp", "Campus ambassador", "ক্যাম্পাস অ্যাম্বাসাডর",
         "College students who want to start addas on their campus.",
         "যে কলেজ পড়ুয়ারা নিজের ক্যাম্পাসে আড্ডা শুরু করতে চান।", "ambassador.html", None),
        ("cup", "img/story-3.webp", "Venue or event partner", "জায়গা বা অনুষ্ঠানের পার্টনার",
         "Cafes, restaurants, sports venues and college fests that welcome our groups.",
         "ক্যাফে, রেস্তোরাঁ, খেলার জায়গা আর কলেজ ফেস্ট, যাঁরা আমাদের দলকে স্বাগত জানান।", "partners.html", None),
        ("star", "img/story-2.webp", "Creator", "ক্রিয়েটর",
         "Bengali creators on Instagram, YouTube and meme pages.",
         "Instagram, YouTube আর মিম পেজের বাঙালি ক্রিয়েটর।", "creators.html", None),
        ("people", "img/join-5.webp", "Adda host", "আড্ডার হোস্ট",
         "Club leads, group admins and hobby groups who bring people together.",
         "ক্লাবের দায়িত্বে থাকা মানুষ, গ্রুপ অ্যাডমিন আর শখের দল, যাঁরা মানুষকে একসঙ্গে আনেন।", "host.html", None),
    ]
    # Picture cards: the picture fills the card, a dusk shade rises from the bottom under the words,
    # the icon sits in a white disc top left. The pictures are decorative (alt=""): the words say it all.
    cards = "".join(
        f"""<li><a class="role" href="{link}"{tgt or ""}>
      <img src="{asset(card_picture(img))}" alt="" loading="lazy">
      {icon(i)}<span class="role-text"><h3>{both(t_en, t_bn)}</h3><p>{both(d_en, d_bn)}</p></span></a></li>"""
        for i, img, t_en, t_bn, d_en, d_bn, link, tgt in roles)
    main = f"""  <section class="roles" aria-labelledby="ways">
    <h2 id="ways">{both("Choose your way in", "কীভাবে যুক্ত হবেন, বেছে নিন")}</h2>
    <ul>{cards}</ul>
    <p class="roles-note">{both(
        f'Want to help some other way? Write to us at <a href="mailto:{EMAIL}">{EMAIL}</a>.',
        f'অন্যভাবে সাহায্য করতে চান? লিখুন <a href="mailto:{EMAIL}">{EMAIL}</a>-এ।')}</p>
  </section>"""
    join_page("join.html", "join",
              ("Join Mon Mela", "মনমেলায় যুক্ত হোন"),
              "Campus ambassadors, partner venues, creators and adda hosts: the ways to be part of Mon Mela.",
              ("Be part of Mon Mela", "মনমেলার অংশ হোন",
               "Mon Mela is being built by the people who use it. Start addas on your campus, welcome groups "
               "at your cafe, make content with us, or host your club's meetups.",
               "মনমেলা গড়ে উঠছে এর মানুষদের হাতেই। নিজের ক্যাম্পাসে আড্ডা শুরু করুন, আপনার ক্যাফেতে দলকে "
               "স্বাগত জানান, আমাদের সঙ্গে কনটেন্ট বানান, বা নিজের ক্লাবের মিটআপ বসান।",
               f'<a class="btn btn-primary btn-big" href="#ways">{both("See the ways to join", "যুক্ত হওয়ার উপায় দেখুন")}</a>',
               ("Free to join. Volunteer roles are unpaid.", "যুক্ত হতে টাকা লাগে না। স্বেচ্ছাসেবী ভূমিকাগুলো অবৈতনিক।")),
              adda_card("back", "Quiz night, Jadavpur", "কুইজ নাইট, যাদবপুর",
                        "Friday, 7 pm", "শুক্রবার, সন্ধে ৭টা", 5, 6, full=False)
              + adda_card("front", "Trek planning adda, Gariahat", "ট্রেকের পরিকল্পনা আড্ডা, গড়িয়াহাট",
                          "Sunday, 11 am", "রবিবার, সকাল ১১টা", 3, 6,
                          tag=("Founding host", "ফাউন্ডিং হোস্ট")),
              main)


def creators():
    """monmela.in/creators: Bengali creators join a list now; paid collaborations open after launch."""
    href, target = form_link("creator",
                             "Name:\nInstagram / YouTube / page link:\nFollowers:\nAverage views on your last 10 posts:\n"
                             "Share of your audience in West Bengal (from your insights):\nWhat you make content about:\n"
                             "Phone or e-mail:\n")
    apply_btn = f'<a class="btn btn-primary btn-big" href="{href}"{target}>{both("Join the creator list", "ক্রিয়েটর তালিকায় নাম দিন")}</a>'
    main = f"""  <section class="fit">
    <div><h2>{both("What we look for", "আমরা যা খুঁজি")}</h2>{bullet_list([
        ("Most of your audience lives in West Bengal", "আপনার দর্শকদের বেশিরভাগ পশ্চিমবঙ্গের"),
        ("You make content in Bengali or Benglish", "আপনি বাংলা বা বাংলা-ইংরেজি মিশিয়ে কনটেন্ট বানান"),
        ("Real views and comments matter more to us than follower count",
         "ফলোয়ার সংখ্যার চেয়ে আসল ভিউ আর কমেন্ট আমাদের কাছে বেশি দামি"),
        ("Friendly content that's fine for a general audience", "সবার দেখার মতো, বন্ধুত্বপূর্ণ কনটেন্ট"),
    ])}</div>
    <div><h2>{both("Good to know", "জেনে রাখুন")}</h2>{bullet_list([
        ("Paid work starts after the app's public launch. Before that, nothing is paid.",
         "টাকার কাজ শুরু হবে অ্যাপ সবার জন্য খোলার পর। তার আগে কোনো পেমেন্ট নেই।"),
        ("Every fee and date is agreed in writing before you post.", "পোস্টের আগে ফি আর তারিখ লিখিতভাবে ঠিক হয়।"),
        ("Every paid post is marked as a paid partnership, as Indian advertising rules require.",
         "ভারতের বিজ্ঞাপনের নিয়ম মেনে প্রতিটা টাকার পোস্টে পেইড পার্টনারশিপ লেখা থাকে।"),
        ("We never pay for followers, likes or fake engagement.", "ফলোয়ার, লাইক বা ভুয়ো এনগেজমেন্টের জন্য আমরা কখনও টাকা দিই না।"),
    ])}</div>
  </section>
  <section class="perks" aria-labelledby="get">
    <h2 id="get">{both("What you get", "আপনি যা পাবেন")}</h2>
    {icon_list([
        ("award", "Paid collaborations", "টাকার বিনিময়ে কাজ",
         "After launch, selected creators get a paid brief, usually a reel and stories.",
         "লঞ্চের পর বাছাই করা ক্রিয়েটররা টাকার বিনিময়ে কাজ পাবেন, সাধারণত একটা রিল আর কয়েকটা স্টোরি।"),
        ("spark", "Early access", "সবার আগে অ্যাপ",
         "Try the app before everyone else, and tell us what your audience would love.",
         "সবার আগে অ্যাপ চালান, আর বলুন আপনার দর্শকদের কী ভালো লাগবে।"),
        ("cup", "First invites to our addas", "আমাদের আড্ডায় প্রথম আমন্ত্রণ",
         "Come to our first meetups and events in Kolkata, and film them if you like.",
         "কলকাতায় আমাদের প্রথম মিটআপ আর অনুষ্ঠানে আসুন, চাইলে ভিডিও করুন।"),
        ("people", "Work that lasts", "লম্বা সম্পর্ক",
         "If your audience loves Mon Mela, we come back to you first.",
         "আপনার দর্শকদের মনমেলা ভালো লাগলে, পরের বারও আমরা আগে আপনার কাছেই আসব।"),
    ])}
  </section>
  <section class="steps" aria-labelledby="how">
    <h2 id="how">{both("How it works", "কীভাবে হয়")}</h2>
    {steps_list([
        ("Join the list", "তালিকায় নাম দিন",
         "Send us your page, followers, average views and how much of your audience is in West Bengal.",
         "আপনার পেজ, ফলোয়ার, গড় ভিউ আর দর্শকদের কতটা পশ্চিমবঙ্গে, তা আমাদের পাঠান।"),
        ("We look at your posts", "আমরা আপনার পোস্ট দেখি", "We reply within a week.", "এক সপ্তাহের মধ্যে উত্তর দিই।"),
        ("After launch, a brief", "লঞ্চের পর কাজের বিবরণ",
         "What to make, the fee and the date, agreed in writing.", "কী বানাবেন, ফি আর তারিখ, লিখিতভাবে ঠিক হয়।"),
        ("You post", "আপনি পোস্ট করেন", "Marked as a paid partnership, with a link to the app.",
         "পেইড পার্টনারশিপ লেখা, সঙ্গে অ্যাপের লিংক।"),
    ])}
  </section>
  <section class="cta-band">
    {festoon()}
    <h2>{both("Make your audience's next adda", "আপনার দর্শকদের পরের আড্ডা জমান")}</h2>
    <p>{both("It takes two minutes to join the list.", "তালিকায় নাম দিতে দু'মিনিট লাগে।")}</p>
    <div class="actions">{apply_btn}</div>
  </section>"""
    join_page("creators.html", "creators",
              ("Creators | Mon Mela", "ক্রিয়েটর | মনমেলা"),
              "Bengali creators: join the Mon Mela creator list now. Paid collaborations open after the public launch.",
              ("Create with Mon Mela", "মনমেলার সঙ্গে কনটেন্ট বানান",
               "We're looking for Bengali creators whose followers love adda, food, books, football and their city. "
               "Join our creator list now. Paid collaborations open after the public launch.",
               "আমরা এমন বাঙালি ক্রিয়েটর খুঁজছি যাঁদের দর্শকেরা আড্ডা, খাওয়াদাওয়া, বই, ফুটবল আর নিজের শহর ভালোবাসেন। "
               "এখনই ক্রিয়েটর তালিকায় নাম দিন। টাকার কাজ শুরু হবে অ্যাপ সবার জন্য খোলার পর।",
               apply_btn,
               ("Instagram, YouTube, meme pages and blogs. Every size is welcome.",
                "Instagram, YouTube, মিম পেজ আর ব্লগ। ছোট-বড় সবাইকে স্বাগত।")),
              adda_card("back", "Phuchka crawl, Vivekananda Park", "ফুচকা অভিযান, বিবেকানন্দ পার্ক",
                        "Saturday, 6 pm", "শনিবার, সন্ধে ৬টা", 4, 6, full=False)
              + adda_card("front", "Creators' adda, College Street", "ক্রিয়েটরদের আড্ডা, কলেজ স্ট্রিট",
                          "Sunday, 4 pm", "রবিবার, বিকেল ৪টে", 4, 6,
                          tag=("Creator meetup", "ক্রিয়েটর মিটআপ")),
              main)


def host():
    """monmela.in/host: club leads, group admins and hobby groups become Founding Hosts of Adda Tables."""
    href, target = form_link("host",
                             "Name:\nYour club, group or community (with a link if it has one):\nWhat kind of meetups you run:\n"
                             "Area:\nHow many people usually come:\nPhone or e-mail:\n")
    apply_btn = f'<a class="btn btn-primary btn-big" href="{href}"{target}>{both("Become a Founding Host", "ফাউন্ডিং হোস্ট হোন")}</a>'
    main = f"""  <section class="perks" aria-labelledby="tools">
    <h2 id="tools">{both("What the app does for you", "অ্যাপ আপনার জন্য যা করে")}</h2>
    {icon_list([
        ("people", "You choose who joins", "কে আসবেন, আপনি ঠিক করেন",
         "People ask for a seat, and you say yes or no. You set the number of seats.",
         "মানুষ জায়গা চান, আপনি হ্যাঁ বা না বলেন। কতগুলো জায়গা, তাও আপনি ঠিক করেন।"),
        ("pin", "The exact spot stays private", "ঠিক জায়গা গোপন থাকে",
         "Only the people you accept see where you're meeting.", "শুধু যাঁদের আপনি নেন, তাঁরাই জানেন কোথায় দেখা হবে।"),
        ("badge", "Women-only and verified-only tables", "শুধু মহিলাদের আর শুধু যাচাই করা সদস্যদের টেবিল",
         "Hosts are photo verified, and you can open a table to women only or verified members only.",
         "হোস্টরা ছবি-যাচাই করা, আর আপনি টেবিল শুধু মহিলাদের বা শুধু যাচাই করা সদস্যদের জন্য খুলতে পারেন।"),
        ("chat", "A group chat for every adda", "প্রতিটা আড্ডার গ্রুপ চ্যাট",
         "It opens for the people at your table, without sharing phone numbers.",
         "টেবিলের মানুষদের জন্য খোলে, কারও ফোন নম্বর না দিয়েই।"),
    ])}
  </section>
  <section class="fit">
    <div><h2>{both("Who it's for", "কাদের জন্য")}</h2>{bullet_list([
        ("Club and society leads in colleges", "কলেজের ক্লাব আর সোসাইটির দায়িত্বে থাকা মানুষ"),
        ("Admins of local Facebook and WhatsApp groups", "পাড়ার বা শহরের Facebook আর WhatsApp গ্রুপের অ্যাডমিন"),
        ("Hobby groups: trekking, photography, books, music, board games, running",
         "শখের দল: ট্রেকিং, ফটোগ্রাফি, বই, গান, বোর্ড গেম, দৌড়"),
        ("Anyone who loves bringing people together, 18 or older",
         "মানুষকে একসঙ্গে আনতে ভালোবাসেন এমন যে কেউ, বয়স ১৮ বা তার বেশি"),
    ])}</div>
    <div><h2>{both("What we ask", "আমরা যা চাই")}</h2>{bullet_list([
        ("Host at least 2 addas in the first month after launch", "লঞ্চের পর প্রথম মাসে অন্তত ২টো আড্ডা বসান"),
        ("Meet in public places only: cafes, parks, sports grounds", "দেখা শুধু সবার জন্য খোলা জায়গায়: ক্যাফে, পার্ক, খেলার মাঠ"),
        ("No selling, recruiting or paid entry at addas", "আড্ডায় কিছু বিক্রি, লোক টানা বা টাকা নিয়ে ঢোকানো চলবে না"),
        ("Tell us what works and what doesn't", "কী ভালো চলছে আর কী নয়, আমাদের জানান"),
    ])}</div>
  </section>
  <section class="perks paper" aria-labelledby="get">
    <h2 id="get">{both("As a Founding Host", "ফাউন্ডিং হোস্ট হিসেবে")}</h2>
    {icon_list([
        ("spark", "Try it before launch", "লঞ্চের আগেই চালান",
         "We add you to the test, so your first tables are ready on day one.",
         "আমরা আপনাকে টেস্টে যোগ করব, যাতে প্রথম দিনেই আপনার টেবিল তৈরি থাকে।"),
        ("star", "Get featured", "আমাদের পেজে আপনি", "We introduce you and your group on our Instagram.",
         "আমাদের Instagram-এ আপনাকে আর আপনার দলকে পরিচয় করিয়ে দিই।"),
        ("chat", "A direct line to us", "সরাসরি আমাদের সঙ্গে কথা", "Ask for the features your group needs, and we listen.",
         "আপনার দলের যা দরকার, সেই ফিচার চান, আমরা শুনি।"),
        ("award", "Free premium for life", "সারাজীবন বিনামূল্যে প্রিমিয়াম", "Whatever premium features come later, you never pay.",
         "পরে যে প্রিমিয়াম ফিচারই আসুক, আপনাকে টাকা দিতে হবে না।"),
    ])}
  </section>
  <section class="cta-band">
    {festoon()}
    <h2>{both("Bring your people along", "আপনার মানুষদের সঙ্গে নিয়ে আসুন")}</h2>
    <p>{both("We're picking our first hosts in Kolkata and around West Bengal.",
             "কলকাতা আর পশ্চিমবঙ্গ জুড়ে আমরা প্রথম হোস্টদের বেছে নিচ্ছি।")}</p>
    <div class="actions">{apply_btn}</div>
  </section>"""
    join_page("host.html", "host",
              ("Host an adda | Mon Mela", "আড্ডা বসান | মনমেলা"),
              "Club leads, group admins and hobby groups: become a Founding Host and run your meetups as Adda Tables.",
              ("Host addas your way", "নিজের মতো আড্ডা বসান",
               "Run a book club, a trekking group, a board-game night or a local community? Bring it to Mon Mela "
               "as a Founding Host, and fill your meetups with people who share your interests.",
               "বইয়ের ক্লাব, ট্রেকিংয়ের দল, বোর্ড গেমের সন্ধে বা পাড়ার কোনো কমিউনিটি চালান? ফাউন্ডিং হোস্ট হয়ে "
               "মনমেলায় নিয়ে আসুন, আর একই শখের মানুষে ভরিয়ে তুলুন আপনার মিটআপ।",
               apply_btn,
               ("For club leads, group admins and anyone who brings people together. 18+ only.",
                "ক্লাবের দায়িত্বে থাকা মানুষ, গ্রুপ অ্যাডমিন আর যাঁরা মানুষকে একসঙ্গে আনেন, তাঁদের জন্য। শুধু ১৮+।")),
              adda_card("back", "Book club, College Street", "বইয়ের ক্লাব, কলেজ স্ট্রিট",
                        "Sunday, 11 am", "রবিবার, সকাল ১১টা", 4, 8, full=False)
              + adda_card("front", "Board-game night, Salt Lake", "বোর্ড গেমের সন্ধে, সল্টলেক",
                          "Saturday, 7 pm", "শনিবার, সন্ধে ৭টা", 5, 8,
                          tag=("Founding host", "ফাউন্ডিং হোস্ট")),
              main)


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
join_hub()
ambassador()
partners()
creators()
host()
assetlinks()
sitemap()
print("built")
