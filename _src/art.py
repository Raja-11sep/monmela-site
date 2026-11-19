# Code-drawn Bengal illustrations for the website (SVG), in a kantha-stitch style:
#   hero_art()        - the live part of the home page picture: two kites and the stitched arch
#                       frame, on top of the painted ghat scene (tools/make_hero.py paints that)
#   bridge()          - Howrah Bridge truss, used by tools/make_hero.py
#   rings_stitched()  - the logo's two rings with running stitches, for the download panel
#   alpana_tile()     - one repeat of the alpana border used above the footer
#   festoon()         - a mela's string of lights, hung across the top of dusk sections

TEAL_DEEP = "#0F4C47"
TEAL = "#115E59"
MARIGOLD = "#F5B023"
INK = "#1C2626"


def _f(v):
    """Short number for SVG (1 decimal, no trailing .0)."""
    s = f"{v:.1f}"
    return s[:-2] if s.endswith(".0") else s


def _bridge_points(x0, x1, deck, tower_h):
    """Top chord of a Howrah-style cantilever bridge: low at the ends, peaks at the two towers,
    dips to the suspended span in the middle. Returns (points, tower_xs)."""
    span = x1 - x0
    tl, tr = x0 + 0.23 * span, x0 + 0.77 * span
    pts = [(x0, deck - 0.14 * tower_h), (tl, deck - tower_h),
           (x0 + 0.40 * span, deck - 0.45 * tower_h), (x0 + 0.50 * span, deck - 0.49 * tower_h),
           (x0 + 0.60 * span, deck - 0.45 * tower_h), (tr, deck - tower_h), (x1, deck - 0.14 * tower_h)]
    return pts, (tl, tr)


def _top_y(pts, x):
    """Height of the top chord at x (straight lines between the points)."""
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        if ax <= x <= bx:
            return ay + (by - ay) * (x - ax) / (bx - ax)
    return pts[-1][1]


def bridge(x0, x1, deck, tower_h, step, color, chord_w, web_w, pier_bottom=None):
    """Truss lines (verticals + alternating diagonals), top chord, deck and towers."""
    pts, towers = _bridge_points(x0, x1, deck, tower_h)
    web = []
    xs = [x0 + i * step for i in range(int((x1 - x0) / step) + 1)]
    for i, x in enumerate(xs):
        web.append(f"M{_f(x)} {_f(deck)}V{_f(_top_y(pts, x))}")
        if i + 1 < len(xs):
            nx = xs[i + 1]
            if i % 2 == 0:
                web.append(f"M{_f(x)} {_f(deck)}L{_f(nx)} {_f(_top_y(pts, nx))}")
            else:
                web.append(f"M{_f(x)} {_f(_top_y(pts, x))}L{_f(nx)} {_f(deck)}")
    chord = "M" + "L".join(f"{_f(x)} {_f(y)}" for x, y in pts)
    out = [f'<path d="{"".join(web)}" stroke="{color}" stroke-width="{web_w}" fill="none"/>',
           f'<path d="{chord}" stroke="{color}" stroke-width="{chord_w}" fill="none" stroke-linejoin="round"/>',
           f'<path d="M{_f(x0 - step)} {_f(deck)}H{_f(x1 + step)}" stroke="{color}" stroke-width="{chord_w * 1.4}"/>']
    for tx in towers:
        out.append(f'<path d="M{_f(tx)} {_f(deck - tower_h - chord_w * 3)}V{_f(deck)}" '
                   f'stroke="{color}" stroke-width="{chord_w * 1.6}"/>')
        if pier_bottom:
            out.append(f'<rect x="{_f(tx - chord_w * 2.5)}" y="{_f(deck)}" width="{_f(chord_w * 5)}" '
                       f'height="{_f(pier_bottom - deck)}" fill="{color}"/>')
    return "".join(out)


# ---------------------------------------------------------------- hero

STITCH = 'stroke-dasharray="8 6" stroke-linecap="round"'   # kantha running stitch


# The Mon Mela mark: two rings, marigold where they meet (top bar, link preview)
LOGO = """<svg viewBox="0 0 48 48" aria-hidden="true"><circle cx="24" cy="24" r="24" fill="#fff"/>
<circle cx="19" cy="24" r="9" fill="none" stroke="#0F766E" stroke-width="3.2"/>
<circle cx="29" cy="24" r="9" fill="none" stroke="#0F766E" stroke-width="3.2"/>
<path d="M24 16.6a9 9 0 0 1 0 14.8a9 9 0 0 1 0-14.8z" fill="#F5B023"/></svg>"""

ARCH = "M24 708V300A276 276 0 0 1 576 300V708Z"     # frame centre line
INNER = "M35 697V300A265 265 0 0 1 565 300V697Z"    # what the window shows


def kite(cx, cy, angle, left, right, s=1.0):
    """Diamond kite (ghuri): two-colour halves, bamboo spine and bow, small tail."""
    return (f'<g transform="translate({cx} {cy}) rotate({angle}) scale({s})">'
            f'<path d="M0 -44L-34 0L0 44Z" fill="{left}"/><path d="M0 -44L34 0L0 44Z" fill="{right}"/>'
            f'<path d="M0 -44L34 0L0 44L-34 0Z" fill="none" stroke="#3B2A22" stroke-width="1.6" stroke-linejoin="round"/>'
            f'<path d="M0 -44V44M-34 0Q0 -12 34 0" stroke="#3B2A22" stroke-width="1.4" fill="none"/>'
            f'<path d="M0 44l-8 13h16Z" fill="{left}"/></g>')


def hero_art(img_src):
    """The home page picture: the painted ghat scene (img/hero-ghat.webp, made by
    tools/make_hero.py) with two live things on top: kites that sway on their strings (CSS,
    see .kite in style.css) and the kantha-stitched frame, which stays sharp at any size."""
    string = 'stroke="#2A1D33" stroke-width=".8" fill="none" opacity=".5"'
    return f"""<div class="hero-art">
<img src="{img_src}" width="1000" height="1200" decoding="async" fetchpriority="high"
     alt="Four friends sitting on a ghat of the Ganga at sunset, looking at Howrah Bridge">
<svg viewBox="0 0 600 720" aria-hidden="true">
<defs><clipPath id="hero-window"><path d="{INNER}"/></clipPath></defs>
<g clip-path="url(#hero-window)">
  <g class="kite kite-a"><path d="M398 166Q420 330 610 470" {string}/>{kite(404, 142, 14, "#0F766E", MARIGOLD, .52)}</g>
  <g class="kite kite-b"><path d="M246 246Q200 350 -10 480" {string}/>{kite(250, 225, -16, "#C0392B", "#FBF3E6", .44)}</g>
</g>
<path class="frame" d="{ARCH}" fill="none" stroke="{TEAL_DEEP}" stroke-width="22"/>
<path class="stitch" d="{ARCH}" fill="none" stroke="{MARIGOLD}" stroke-width="3" stroke-dasharray="10 9" stroke-linecap="round"/>
</svg>
</div>"""


def rings_stitched():
    """The logo's two rings with a running stitch, for the download panel."""
    return f"""<svg class="rings-art" viewBox="0 0 420 300" aria-hidden="true">
<defs><clipPath id="cta-ring-left"><circle cx="160" cy="150" r="118"/></clipPath></defs>
<circle cx="260" cy="150" r="118" fill="{MARIGOLD}" clip-path="url(#cta-ring-left)" opacity=".9"/>
<g fill="none" stroke="{TEAL}" stroke-width="10"><circle cx="160" cy="150" r="118"/><circle cx="260" cy="150" r="118"/></g>
<g fill="none" stroke="{TEAL}" stroke-width="2.4" {STITCH} opacity=".55">
  <circle cx="160" cy="150" r="100"/><circle cx="260" cy="150" r="100"/></g>
</svg>"""


def alpana_tile():
    """One 120 x 56 repeat of an alpana border (rice-paste floor art): dotted edges, a lotus, leaves."""
    c = "#F6E9CC"
    dots = "".join(f'<circle cx="{x}" cy="{y}" r="1.5"/>' for y in (5, 51) for x in range(4, 120, 8))
    petal = "M0 0C6 -6 6 -14 0 -20C-6 -14 -6 -6 0 0Z"
    lotus = "".join(f'<path d="{petal}" transform="translate(60 37) rotate({a})"/>' for a in (-70, -35, 0, 35, 70))
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 56" width="120" height="56">
<g fill="{c}">{dots}<circle cx="60" cy="37" r="2.6"/><circle cx="36" cy="28" r="1.8"/><circle cx="84" cy="28" r="1.8"/>
<circle cx="0" cy="28" r="2.2"/><circle cx="120" cy="28" r="2.2"/></g>
<g fill="none" stroke="{c}" stroke-width="1.5" stroke-linejoin="round">
<path d="M0 11H120M0 45H120"/>{lotus}
<path d="M8 28q9 -9 18 0q-9 9 -18 0zM94 28q9 -9 18 0q-9 9 -18 0z"/></g>
</svg>
"""


def festoon(swags=4, per_swag=9, width=1600):
    """A string of mela lights: `swags` dips of wire across `width`, bulbs hanging from each.
    The SVG is wide and anchored to the top centre; narrow screens crop the sides (no stretching).
    Each bulb carries --i (its order), so CSS can switch them on one after another."""
    sag, top = 46, 6
    seg = width / swags
    colours = [MARIGOLD, "#FFE7B3", "#E2553A", MARIGOLD, "#FFE7B3", "#7FD8CC"]
    # One soft halo per colour: the bulb's colour fading out to nothing.
    gid = {c: f"fg{n}" for n, c in enumerate(dict.fromkeys(colours))}
    defs = "".join(f'<radialGradient id="{g}"><stop offset="0" stop-color="{c}" stop-opacity=".75"/>'
                   f'<stop offset="1" stop-color="{c}" stop-opacity="0"/></radialGradient>' for c, g in gid.items())
    wire, bulbs, i = [], [], 0
    for k in range(swags):
        x0, x1 = k * seg, (k + 1) * seg
        cx = (x0 + x1) / 2
        # Quadratic curve through the middle at depth `sag`: control point at 2*sag.
        wire.append(f"M{_f(x0)} {top}Q{_f(cx)} {top + 2 * sag} {_f(x1)} {top}")
        for j in range(1, per_swag + 1):
            t = j / (per_swag + 1)
            x = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t ** 2 * x1
            y = (1 - t) ** 2 * top + 2 * (1 - t) * t * (top + 2 * sag) + t ** 2 * top
            c = colours[i % len(colours)]
            bulbs.append(
                f'<g class="bulb" style="--i:{i}" transform="translate({_f(x)} {_f(y)})">'
                f'<circle class="glow" cy="13" r="20" fill="url(#{gid[c]})"/>'
                f'<rect x="-2.6" y="0" width="5.2" height="5" rx="1" fill="#2B2420"/>'
                f'<ellipse cy="12" rx="5.4" ry="7" fill="{c}"/></g>')
            i += 1
    return (f'<svg class="festoon" viewBox="0 0 {width} 120" preserveAspectRatio="xMidYMin slice" aria-hidden="true">'
            f'<defs>{defs}</defs>'
            f'<path d="{"".join(wire)}" fill="none" stroke="#06221F" stroke-width="2"/>'
            f'{"".join(bulbs)}</svg>')
