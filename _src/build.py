# Builds the monmela.in website so every page shares the same header, footer and styles.
# Usage (from the site folder): python3 _src/build.py      needs: pip install qrcode
#   - Home and download pages: written here, bilingual piece by piece.
#   - Legal pages: _src/pages/<name>.en.html + <name>.bn.html inside the standard card layout.
#   - _src/ is not published: GitHub Pages (Jekyll) skips folders that start with "_".
import datetime
import hashlib
import json
import pathlib
import re

from art import alpana_tile, hero_art, rings_stitched

ROOT = pathlib.Path(__file__).resolve().parent.parent      # the site folder (built files go here)
PAGES = pathlib.Path(__file__).resolve().parent / "pages"  # legal page bodies
SITE = "https://monmela.in"
UPDATED_EN = "11 November 2026"
UPDATED_BN = "১১ নভেম্বর ২০২৬"
EMAIL = "monmela.team@gmail.com"

# Android app download (monmela.in/download).
# APK_FILE: the Play-signed universal APK, uploaded to the site repo at this path.
# PLAY_URL: set at public launch, e.g. "https://play.google.com/store/apps/details?id=<package>".
#   Then every download button goes to Google Play and /download redirects there (APK no longer offered).
APK_FILE = "app/mon-mela.apk"
PLAY_URL = ""
# Closed test on Google Play (until launch): testers join the group, then become testers and install.
# Empty both to hide the Google Play steps and offer only the APK.
TEST_GROUP_URL = "https://groups.google.com/g/mon-mela-testers"
TEST_JOIN_URL = "https://play.google.com/apps/testing/com.monmela.app"

# Our social pages: linked in the footer and listed in the structured data ("sameAs"),
# which tells Google these pages belong to the same Mon Mela.
INSTAGRAM_URL = "https://www.instagram.com/monmelaapp/"
FACEBOOK_URL = "https://www.facebook.com/profile.php?id=61596312788249"

LOGO = """<svg viewBox="0 0 48 48" aria-hidden="true"><circle cx="24" cy="24" r="24" fill="#fff"/>
<circle cx="19" cy="24" r="9" fill="none" stroke="#0F766E" stroke-width="3.2"/>
<circle cx="29" cy="24" r="9" fill="none" stroke="#0F766E" stroke-width="3.2"/>
<path d="M24 16.6a9 9 0 0 1 0 14.8a9 9 0 0 1 0-14.8z" fill="#F5B023"/></svg>"""

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
<meta name="theme-color" content="#115E59">
<link rel="canonical" href="{SITE}/{path}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Mon Mela">
<meta property="og:locale" content="en_IN">
<meta property="og:locale:alternate" content="bn_IN">
<meta name="twitter:card" content="summary_large_image">
<meta property="og:title" content="{title_en}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{SITE}/{path}">
<meta property="og:image" content="{SITE}/og.png">
<link rel="icon" href="{asset("favicon.ico")}" sizes="48x48">
<link rel="icon" href="{asset("favicon.svg")}" type="image/svg+xml">
<link rel="apple-touch-icon" href="{asset("apple-touch-icon.png")}">
<link rel="manifest" href="site.webmanifest">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Hind+Siliguri:wght@400;500;600;700&family=Inter:wght@400;500;600;700&family=Tiro+Bangla&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{asset("style.css")}">
<script src="{asset("site.js")}"></script>
{extra}
</head>"""


def header(on_home=False):
    """Sticky top bar on every page: logo, section links (wide screens), language switch, Download.
    On the home page the links only scroll; elsewhere they open the home page at that section."""
    prefix = "" if on_home else "./"
    links = '<nav class="top-nav" aria-label="Sections">' + "".join(
        f'<a href="{prefix}#{anchor}">{both(en, bn)}</a>'
        for anchor, en, bn in [("how", "How it works", "কীভাবে"), ("safe", "Safety", "নিরাপত্তা"),
                               ("qa", "Questions", "প্রশ্ন")]) + "</nav>"
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
    """Round Instagram / Facebook buttons. rel="me" says the pages are ours."""
    items = [(INSTAGRAM_URL, "Mon Mela on Instagram", INSTAGRAM_ICON),
             (FACEBOOK_URL, "Mon Mela on Facebook", FACEBOOK_ICON)]
    return '<p class="social">' + "".join(
        f'<a href="{url}" target="_blank" rel="noopener me" aria-label="{label}" title="{label}">{svg}</a>'
        for url, label, svg in items) + "</p>"


def footer():
    links = "".join(f'<li><a href="{href}">{both(en, bn)}</a></li>' for href, en, bn in NAV)
    return f"""<footer class="site-foot">
  <div class="alpana" aria-hidden="true"></div>
  <div class="foot-inner">
    <div class="foot-brand">
      <a class="brand" href="./">{LOGO}{both("Mon Mela", "মনমেলা")}</a>
      <p>{both("Friends who think like you, across West Bengal.", "মনের মতো বন্ধু, সারা পশ্চিমবঙ্গে।")}</p>
      {social_links()}
    </div>
    <div>
      <h2>{both("Write to us", "আমাদের লিখুন")}</h2>
      <p><a href="mailto:{EMAIL}">{EMAIL}</a></p>
      <p>{both("Grievance Officer: Dhritisha Palmal", "অভিযোগ আধিকারিক: Dhritisha Palmal")}</p>
    </div>
    <nav aria-label="Pages">
      <h2>{both("Pages", "পেজ")}</h2>
      <ul>{links}</ul>
    </nav>
  </div>
  <p class="foot-base">{both("© 2026 Mon Mela · Made in West Bengal", "© ২০২৬ মনমেলা · পশ্চিমবঙ্গে তৈরি")}</p>
</footer>"""


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

def venn():
    """Two people's quiz answers as overlapping circles: the overlap is what they share.
    Same idea as the logo (two rings, marigold where they meet).
    Geometry: circles r=120 at x=170 and x=270, so the overlap (lens) spans x 150-290."""
    def words(x, y, items, cls=""):
        # One <text> per language for each line; site.js/CSS hide the other language.
        out = []
        for i, (en, bn) in enumerate(items):
            dy = y + i * 26
            out.append(f'<text x="{x}" y="{dy}" class="l {cls}" lang="en">{en}</text>'
                       f'<text x="{x}" y="{dy}" class="l {cls}" lang="bn">{bn}</text>')
        return "".join(out)

    return f"""<figure class="venn">
<svg viewBox="0 0 440 320" aria-hidden="true">
  <defs><clipPath id="in-left"><circle cx="170" cy="170" r="120"/></clipPath></defs>
  <g class="who">
    {words(102, 30, [("You", "আপনি")])}
    {words(338, 30, [("Someone in Howrah", "হাওড়ার কেউ")])}
  </g>
  <circle class="ring ring-left" cx="170" cy="170" r="120"/>
  <circle class="ring ring-right" cx="270" cy="170" r="120"/>
  <g class="lens"><circle cx="270" cy="170" r="120" clip-path="url(#in-left)"/></g>
  <g class="side">
    {words(102, 150, [("Early riser", "ভোরে ওঠা"), ("Biryani", "বিরিয়ানি"), ("Puri trips", "পুরী")])}
    {words(338, 150, [("Night owl", "রাত জাগা"), ("Momos", "মোমো"), ("Football", "ফুটবল")])}
  </g>
  <g class="shared">
    {words(220, 128, [("Café adda", "ক্যাফেতে আড্ডা"), ("The hills", "পাহাড়"), ("Rabindrasangeet", "রবীন্দ্রসংগীত")])}
  </g>
  <g class="score">{words(220, 230, [("86% match", "৮৬% মিল")])}</g>
</svg>
<figcaption>{both(
    "You both love café adda, the hills and Rabindrasangeet: an 86% match.",
    "দুজনেই ক্যাফের আড্ডা, পাহাড় আর রবীন্দ্রসংগীত ভালোবাসেন: ৮৬% মিল।")}</figcaption>
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


# App screens shown in the phone mockups (made by tools/prep_screens.py): file, alt text en/bn
SCREENS = {
    "welcome": ("img/app-welcome.webp", "Mon Mela welcome screen with Continue with Google",
                "মনমেলার শুরুর স্ক্রিন, Google দিয়ে লগইন"),
    "looking": ("img/app-looking-for.webp", "Picking what you are looking for: adda, study partner, gym, foodie",
                "কী খুঁজছেন বেছে নেওয়া: আড্ডা, পড়ার সঙ্গী, জিম, খাওয়াদাওয়া"),
    "quiz": ("img/app-quiz.webp", "Friendship quiz: all 12 questions answered",
             "বন্ধুত্বের কুইজ: ১২টা প্রশ্নেরই উত্তর দেওয়া"),
    "picks": ("img/app-picks.webp", "Today's picks: a suggestion with 82% match and why you match",
              "আজকের মানুষ: ৮২% মিল আর কেন মিল"),
    # "Inside the app" row (names, photos and messages blurred by tools/prep_store_screens.py)
    "requests": ("img/app-requests.webp", "A friend request with a short hello, and Accept or Decline",
                 "ছোট শুভেচ্ছা সহ বন্ধুত্বের অনুরোধ, মানুন বা না বলুন"),
    "chats": ("img/app-chats.webp", "The Chats tab with three friends", "তিনজন বন্ধুর সঙ্গে চ্যাটের তালিকা"),
    "verify": ("img/app-verify.webp", "Photo verification: copy a pose in a quick selfie",
               "ছবি যাচাই: একটা ভঙ্গি নকল করে সেলফি"),
    "filters": ("img/app-filters.webp", "Who to suggest: age range and same-gender-only switch",
                "কাকে সাজেস্ট করা হবে: বয়স আর শুধু নিজের লিঙ্গ"),
    "safety": ("img/app-safety.webp", "Safety and account settings: verification, safety tips, blocked people, pause",
               "নিরাপত্তা আর অ্যাকাউন্ট: যাচাই, টিপস, ব্লক, পজ"),
}


def phone(key, cls="", lazy=True, alt=True):
    """A phone frame around one app screen. alt=False for decorative copies."""
    src, alt_en, _ = SCREENS[key]
    loading = ' loading="lazy"' if lazy else ""
    alt_text = alt_en if alt else ""
    return (f'<div class="phone {cls}"><div class="screen">'
            f'<img src="{asset(src)}" alt="{alt_text}" width="720" height="1520"{loading}></div></div>')  # ?v= → new screenshot shows at once


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
    steps_html = "".join(
        f'<li class="how-item">{phone(k)}<div class="how-cap"><h3>{both(t_en, t_bn)}</h3><p>{both(d_en, d_bn)}</p></div></li>'
        for k, t_en, t_bn, d_en, d_bn in steps)

    # Inside the app: five more screens, no numbers (they're not steps).
    tour = [
        ("requests", "Requests with a hello", "শুভেচ্ছা সহ অনুরোধ",
         "Accept or decline. Nobody can message you until you say yes.",
         "মানবেন কি না, আপনার ইচ্ছে। আপনি রাজি না হলে কেউ মেসেজ করতে পারে না।"),
        ("chats", "Chat with your friends", "বন্ধুদের সঙ্গে চ্যাট",
         "Talk only with people who said yes to you, and you to them.",
         "শুধু তাঁদের সঙ্গে কথা, যাঁরা আপনাকে আর আপনি যাঁদের হ্যাঁ বলেছেন।"),
        ("verify", "Get photo verified", "ছবি যাচাই করুন",
         "One quick selfie earns the ✓ badge. Only our team sees it.",
         "একটা সেলফিতেই ✓ ব্যাজ। সেলফি শুধু আমাদের টিম দেখে।"),
        ("filters", "You choose who you see", "কাকে দেখবেন, আপনিই ঠিক করুন",
         "Set an age range, or meet only people of your own gender.",
         "বয়সের সীমা ঠিক করুন, বা শুধু নিজের লিঙ্গের মানুষের সঙ্গে আলাপ।"),
        ("safety", "Safety in your hands", "নিরাপত্তা আপনার হাতে",
         "Block anyone, pause your profile, read the safety tips.",
         "যে কাউকে ব্লক, প্রোফাইল পজ, নিরাপত্তার টিপস।"),
    ]
    tour_html = "".join(
        f'<li class="tour-item">{phone(k)}<h3>{both(t_en, t_bn)}</h3><p>{both(d_en, d_bn)}</p></li>'
        for k, t_en, t_bn, d_en, d_bn in tour)

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
        ("lock", "Screenshots are blocked inside the app, to protect everyone's photos and chats.",
         "সবার ছবি আর চ্যাট সুরক্ষিত রাখতে অ্যাপে স্ক্রিনশট বন্ধ।"),
        ("adult", "Adults only. A \"Looks under 18\" report hides a profile at once, until we check it.",
         "শুধু প্রাপ্তবয়স্কদের জন্য। \"১৮-র কম মনে হচ্ছে\" রিপোর্ট এলেই প্রোফাইল সঙ্গে সঙ্গে লুকোনো হয়, যতক্ষণ না আমরা যাচাই করি।"),
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
    faq_html = "".join(
        f'<details><summary>{both(q_en, q_bn)}</summary><p>{both(a_en, a_bn)}</p></details>'
        for q_en, q_bn, a_en, a_bn in faq)

    # Interests: tappable chips styled like the app's own; a few start picked. home.js updates the count.
    interests = [("Adda", "আড্ডা", 1), ("Study partner", "পড়ার সঙ্গী", 1), ("Rabindrasangeet", "রবীন্দ্রসংগীত", 0),
                 ("Pandal hopping", "ঠাকুর দেখা", 1), ("Biryani", "বিরিয়ানি", 0), ("Football", "ফুটবল", 0),
                 ("Hill trips", "পাহাড়", 0), ("Books", "বই", 0), ("Phuchka", "ফুচকা", 0), ("Films", "সিনেমা", 0),
                 ("Morning walks", "ভোরের হাঁটা", 0), ("Cricket", "ক্রিকেট", 0), ("Photography", "ছবি তোলা", 0),
                 ("Chai", "চা", 1), ("Theatre", "থিয়েটার", 0), ("Board games", "বোর্ড গেম", 0), ("Coding", "কোডিং", 0),
                 ("Trekking", "ট্রেকিং", 0)]
    chips_html = "".join(
        f'<button type="button" class="chip" aria-pressed="{"true" if on else "false"}">{both(en, bn)}</button>'
        for en, bn, on in interests)
    picked = sum(on for *_, on in interests)

    # Title and description: the words people actually search for (Bengali friendship app,
    # Kolkata, West Bengal, adda), in under ~60 and ~155 characters so Google shows them whole.
    html = f"""{head(HOME_TITLE_EN, HOME_TITLE_BN, HOME_DESCRIPTION, "", script("home.js") + home_schema(faq))}
<body class="home">
{header(on_home=True)}
<section class="hero-k">
  <div class="hero-k-text">
    <h1>{both("Friends who think like you, near you.", "মনের মতো বন্ধু, আপনার কাছেই।")}</h1>
    <p class="lede">{both(
        "A free friendship app for adults in West Bengal. Answer a short quiz, and every day Mon Mela introduces you to people whose answers match yours.",
        "পশ্চিমবঙ্গের প্রাপ্তবয়স্কদের জন্য বিনামূল্যের বন্ধুত্বের অ্যাপ। একটা ছোট কুইজের উত্তর দিন, আর প্রতিদিন মনমেলা আলাপ করিয়ে দেবে এমন মানুষের সঙ্গে, যাঁদের উত্তর আপনার সঙ্গে মেলে।")}</p>
    <div class="actions">
      {get_app_button()}
      <a class="btn btn-quiet" href="#how">{both("How it works", "কীভাবে কাজ করে")}</a>
    </div>
    <p class="hero-note">{both("For friendship, not dating. Adults 18+ only.", "বন্ধুত্বের জন্য, ডেটিংয়ের জন্য নয়। শুধু ১৮+।")}</p>
  </div>
  <div class="hero-k-art">{hero_art()}</div>
</section>

<section class="interests" aria-labelledby="int-h">
  <h2 id="int-h">{both("What do you love?", "আপনার কী ভালো লাগে?")}</h2>
  <p class="int-lede">{both("Tap a few, just like in the app.", "অ্যাপের মতোই, কয়েকটা বেছে নিন।")}</p>
  <div class="chip-board" role="group" aria-label="Interests">{chips_html}</div>
  <p class="chip-count" aria-live="polite"><span class="l" lang="en"><b class="n">{picked}</b> picked. Mon Mela suggests people whose answers match yours.</span><span class="l" lang="bn"><b class="n">{bn_num(picked)}</b>টা বেছেছেন। মনমেলা দেখায় তাঁদের, যাঁদের উত্তর আপনার সঙ্গে মেলে।</span></p>
</section>

<main class="home-main">
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

  <section class="how" aria-labelledby="how">
    <h2 id="how">{both("How it works", "কীভাবে কাজ করে")}</h2>
    <ol class="how-row">{steps_html}</ol>
    <p class="how-then">{icon("chat")}<span>{both("<b>Then connect.</b> The chat opens only when both of you say yes.",
                                                  "<b>তারপর কানেক্ট।</b> দুজনেই রাজি হলে তবেই চ্যাট খোলে।")}</span></p>
  </section>

  <section class="tour" aria-labelledby="tour">
    <h2 id="tour">{both("Inside the app", "অ্যাপের ভেতরে")}</h2>
    <ul class="tour-row">{tour_html}</ul>
  </section>

  <section class="safety" aria-labelledby="safe">
    <div class="safety-head">
      <h2 id="safe">{both("Safe by design", "শুরু থেকেই নিরাপদ")}</h2>
      <p>{both("Built first for the people who usually feel least safe on social apps.",
               "সোশ্যাল অ্যাপে যাঁরা সবচেয়ে কম নিরাপদ বোধ করেন, তাঁদের কথা ভেবেই তৈরি।")}</p>
    </div>
    <ul>{safety_html}</ul>
  </section>

  <section class="cta" aria-labelledby="cta-h">
    <div class="cta-panel">
      <div class="cta-text">
        <h2 id="cta-h">{both("Start your next adda.", "শুরু হোক নতুন আড্ডা।")}</h2>
        <p>{both("Free, in Bengali and English, for adults across West Bengal.",
                 "বিনামূল্যে, বাংলা আর ইংরেজিতে, সারা পশ্চিমবঙ্গের প্রাপ্তবয়স্কদের জন্য।")}</p>
        <div class="actions">{get_app_button("btn btn-dark")}</div>
      </div>
      <div class="cta-art" aria-hidden="true">
        {rings_stitched()}
        {phone("looking", "phone-b", alt=False)}
        {phone("picks", "phone-a", alt=False)}
      </div>
    </div>
  </section>

  <section class="faq" aria-labelledby="qa">
    <h2 id="qa">{both("Questions", "প্রশ্ন")}</h2>
    {faq_html}
  </section>
</main>
{footer()}
</body>
</html>
"""
    (ROOT / "index.html").write_text(html, encoding="utf-8")


# ------------------------------------------------------------ app download

HOME_TITLE_EN = "Mon Mela – Bengali Friendship App for Kolkata &amp; West Bengal"
HOME_TITLE_BN = "মনমেলা – কলকাতা ও পশ্চিমবঙ্গের বন্ধুত্বের অ্যাপ"
HOME_DESCRIPTION = ("Mon Mela (মনমেলা) is a free Bengali friendship app for Kolkata and West Bengal. "
                    "Meet friends who think like you and join adda meetups. Not a dating app.")


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
    # robots.txt: everything may be crawled; points search engines to the sitemap.
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")


def get_app_button(cls="btn btn-primary", short=False):
    """The site's one 'get the app' button: download page now, Google Play after launch."""
    if PLAY_URL:
        label = ("Get the app", "অ্যাপ নিন") if short else ("Get it on Google Play", "Google Play থেকে নিন")
        return f'<a class="{cls}" href="{PLAY_URL}">{both(*label)}</a>'
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

    # Google Play test: two numbered steps (shown while TEST_JOIN_URL is set)
    play_steps = ""
    if TEST_JOIN_URL:
        play_steps = f"""<ol class="play-steps">
        <li><span>{both("Join the Mon Mela testers group", "মনমেলা টেস্টার গ্রুপে যোগ দিন")}</span>
          <a class="btn btn-primary" href="{TEST_GROUP_URL}">{both("Join group", "গ্রুপে যোগ দিন")}</a></li>
        <li><span>{both("Become a tester, then install from Google Play", "টেস্টার হন, তারপর Google Play থেকে ইনস্টল করুন")}</span>
          <a class="btn btn-primary" href="{TEST_JOIN_URL}">{both("Become a tester", "টেস্টার হন")}</a></li>
      </ol>"""

    help_items = [
        ("Google Play says the app isn't available", "Google Play বলছে অ্যাপটি পাওয়া যাচ্ছে না",
         "Join the group with the same Gmail that's signed in to your phone's Play Store, then open the second link again. "
         "Right after joining it can take 15–30 minutes.",
         "ফোনের Play Store-এ যে Gmail আছে, সেটা দিয়েই গ্রুপে যোগ দিন, তারপর দ্বিতীয় লিংকটা আবার খুলুন। "
         "যোগ দেওয়ার পর ১৫–৩০ মিনিট লাগতে পারে।"),
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
  <div class="intro-inner">
    <div>
      <h1>{both("Mon Mela for your Android phone", "আপনার অ্যান্ড্রয়েড ফোনে মনমেলা")}</h1>
      <p class="lede">{both(
          "Free. Mon Mela is in testing on Google Play: join in two steps, using the same Gmail as your phone's Play Store.",
          "বিনামূল্যে। মনমেলা এখন Google Play-তে টেস্টিংয়ে: দুই ধাপে যোগ দিন, ফোনের Play Store-এ যে Gmail আছে সেটাই দিয়ে।")}</p>

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

      {play_steps}
      <div id="get"{' class="apk-alt"' if TEST_JOIN_URL else ''}>
        {('<p class="dl-meta">' + both("Can't use Google Play?", "Google Play চালাতে পারছেন না?") + '</p>') if TEST_JOIN_URL else ''}
        <a class="btn {'btn-ghost' if TEST_JOIN_URL else 'btn-primary btn-big'}" id="apk" href="{APK_FILE}" download="mon-mela.apk">{both("Download APK", "ডাউনলোড APK")}</a>
        <p class="dl-meta">{both("Android app", "অ্যান্ড্রয়েড অ্যাপ")}<span id="apk-size"></span></p>
      </div>
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
  <section class="steps" aria-labelledby="install">
    <h2 id="install">{both("Installing the APK", "APK কীভাবে ইনস্টল করবেন")}</h2>
    <ol>{steps_html}</ol>
  </section>

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
sitemap()
print("built")
