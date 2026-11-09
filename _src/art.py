# Code-drawn Bengal illustrations for the website (inline SVG), in a kantha-stitch style:
#   hero_art()        - an arched window: our logo's two rings setting over Howrah Bridge,
#                       two friends on the ghat flying kites whose strings cross (a "pyanch")
#   rings_stitched()  - the logo's two rings with running stitches, for the download panel
#   alpana_tile()     - one repeat of the alpana border used above the footer
# Plain SVG shapes: sharp at any size, a few KB.

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


def victoria_memorial(x, ground, s, fill):
    """Victoria Memorial silhouette: wide base, central dome with the angel, corner domes. x = left edge."""
    def r(rx, ry, w, h):
        return f'<rect x="{_f(x + rx * s)}" y="{_f(ground - ry * s)}" width="{_f(w * s)}" height="{_f(h * s)}"/>'
    dome = (f'<path d="M{_f(x + 60 * s)} {_f(ground - 72 * s)}'
            f'Q{_f(x + 80 * s)} {_f(ground - 128 * s)} {_f(x + 100 * s)} {_f(ground - 72 * s)}Z"/>')
    corner = "".join(
        f'<rect x="{_f(x + cx * s)}" y="{_f(ground - 50 * s)}" width="{_f(14 * s)}" height="{_f(18 * s)}"/>'
        f'<path d="M{_f(x + cx * s)} {_f(ground - 50 * s)}Q{_f(x + (cx + 7) * s)} {_f(ground - 64 * s)} '
        f'{_f(x + (cx + 14) * s)} {_f(ground - 50 * s)}Z"/>' for cx in (8, 138))
    angel = (f'<rect x="{_f(x + 78 * s)}" y="{_f(ground - 136 * s)}" width="{_f(4 * s)}" height="{_f(12 * s)}"/>'
             f'<circle cx="{_f(x + 80 * s)}" cy="{_f(ground - 139 * s)}" r="{_f(3 * s)}"/>'
             f'<path d="M{_f(x + 80 * s)} {_f(ground - 137 * s)}l{_f(7 * s)} {_f(-5 * s)}l{_f(-3 * s)} {_f(7 * s)}Z"/>')
    return (f'<g fill="{fill}">{r(0, 32, 160, 32)}{r(28, 52, 104, 22)}{r(56, 74, 48, 24)}'
            f'{dome}{corner}{angel}</g>')


def shahid_minar(x, ground, s, fill):
    """Shahid Minar: tall column with a small dome on top. x = centre."""
    return (f'<g fill="{fill}">'
            f'<rect x="{_f(x - 11 * s)}" y="{_f(ground - 12 * s)}" width="{_f(22 * s)}" height="{_f(12 * s)}"/>'
            f'<rect x="{_f(x - 4 * s)}" y="{_f(ground - 140 * s)}" width="{_f(8 * s)}" height="{_f(130 * s)}"/>'
            f'<rect x="{_f(x - 7 * s)}" y="{_f(ground - 143 * s)}" width="{_f(14 * s)}" height="{_f(5 * s)}"/>'
            f'<rect x="{_f(x - 5 * s)}" y="{_f(ground - 152 * s)}" width="{_f(10 * s)}" height="{_f(9 * s)}"/>'
            f'<path d="M{_f(x - 5 * s)} {_f(ground - 152 * s)}Q{_f(x)} {_f(ground - 162 * s)} '
            f'{_f(x + 5 * s)} {_f(ground - 152 * s)}Z"/>'
            f'<rect x="{_f(x - 0.8 * s)}" y="{_f(ground - 170 * s)}" width="{_f(1.6 * s)}" height="{_f(10 * s)}"/>'
            f'</g>')


def buildings(spec, ground, fill):
    """Plain blocks: spec = [(x, width, height), ...]."""
    return f'<g fill="{fill}">' + "".join(
        f'<rect x="{_f(x)}" y="{_f(ground - h)}" width="{_f(w)}" height="{_f(h)}"/>' for x, w, h in spec) + "</g>"


# ---------------------------------------------------------------- hero

STITCH = 'stroke-dasharray="8 6" stroke-linecap="round"'   # kantha running stitch


def kite(cx, cy, angle, left, right):
    """Diamond kite (ghuri): two-colour halves, bamboo spine and bow, small tail."""
    return (f'<g transform="translate({cx} {cy}) rotate({angle})">'
            f'<path d="M0 -44L-34 0L0 44Z" fill="{left}"/><path d="M0 -44L34 0L0 44Z" fill="{right}"/>'
            f'<path d="M0 -44L34 0L0 44L-34 0Z" fill="none" stroke="#6B5236" stroke-width="1.6" stroke-linejoin="round"/>'
            f'<path d="M0 -44V44M-34 0Q0 -12 34 0" stroke="#6B5236" stroke-width="1.4" fill="none"/>'
            f'<path d="M0 44l-8 13h16Z" fill="{left}"/></g>')


def _boat(x, y):
    """Country boat with a canopy and a boatman standing at the back."""
    return (f'<g transform="translate({x} {y})">'
            f'<path d="M-60 0Q0 20 60 0L53 9Q0 26 -53 9Z" fill="{TEAL_DEEP}"/>'
            f'<path d="M-32 1Q-10 -24 14 3Z" fill="#B9822B"/>'
            f'<path d="M35 2V-24" stroke="{INK}" stroke-width="3.2" stroke-linecap="round"/>'
            f'<circle cx="35" cy="-30" r="4.5" fill="{INK}"/>'
            f'<path d="M18 27L52 -42" stroke="{INK}" stroke-width="1.6"/>'
            f'<path d="M-52 18Q0 32 52 18" stroke="#9FCBC2" stroke-width="2" fill="none" {STITCH}/></g>')


def _friends():
    """Two friends from behind (drawn around x 209-295, seat line y 576): he wears a teal kurta with a
    jhola strap, she a red-bordered (laal paar) saree with a flower in her bun; a clay chai cup."""
    return (f'<g transform="rotate(4 230 576)">'
            f'<path d="M209 576C209 549 215 536 230 533C245 536 251 549 251 576Z" fill="{TEAL}"/>'
            f'<path d="M215 543L247 574" stroke="#E59A1C" stroke-width="3.2"/>'
            f'<rect x="226" y="526" width="8" height="9" fill="#8A5A3C"/>'
            f'<circle cx="230" cy="520" r="11.5" fill="{INK}"/>'
            f'<path d="M222 513q6-6 14-2" stroke="#3E5050" stroke-width="1.6" fill="none" stroke-linecap="round"/></g>'
            f'<g transform="rotate(-5 276 576)">'
            f'<path d="M257 576C257 551 262 539 276 536C290 539 295 551 295 576Z" fill="#F7EFE2"/>'
            f'<path d="M257.6 570H294.4V576H257Z" fill="#C0392B"/>'
            f'<path d="M265 540Q280 552 293 566" stroke="#C0392B" stroke-width="3.2" fill="none"/>'
            f'<path d="M268 524Q268 548 277 556Q286 548 285 524Z" fill="{INK}"/>'
            f'<circle cx="276" cy="523" r="10.5" fill="{INK}"/>'
            f'<circle cx="283" cy="514" r="5" fill="{INK}"/>'
            f'<circle cx="287.5" cy="512" r="1.8" fill="#fff"/><circle cx="286" cy="516.5" r="1.6" fill="#fff"/></g>'
            f'<path d="M309 576l2-10h9l2 10Z" fill="#B5643C"/>'
            f'<path d="M313 562q-3-4 0-8M318 562q-3-4 0-8" stroke="#9DB3AF" stroke-width="1.3" fill="none" stroke-linecap="round"/>')


def hero_art():
    """Arched window (kantha-stitched frame) onto the Hooghly at sunset."""
    deck = 486                                   # bridge deck = horizon
    rl, rr, ry, rad = 252, 348, 420, 118         # the logo's two rings, setting
    arch = "M24 708V300A276 276 0 0 1 576 300V708Z"          # frame centre line
    inner = "M35 697V300A265 265 0 0 1 565 300V697Z"          # what the window shows

    far = buildings([(372, 20, 46), (396, 26, 60), (424, 18, 84), (446, 30, 64), (480, 22, 110),
                     (506, 30, 88), (540, 24, 120), (568, 22, 70)], deck, "#CFE5E0")
    near = buildings([(150, 28, 24), (300, 36, 22), (452, 40, 30), (520, 44, 38)], deck, "#B7D8D1")
    trees = "".join(f'<circle cx="{x + (x * 7) % 9}" cy="{deck - 3}" r="{8 + (x * 13) % 7}"/>' for x in range(0, 600, 16))
    waves = [(70, 522, 46), (420, 514, 60), (500, 560, 44), (100, 590, 34), (330, 612, 40), (60, 628, 30), (520, 624, 36)]
    wave_d = "".join(f"M{x} {y}h{w}" for x, y, w in waves)
    refl_d = "".join(f"M{300 - (150 - k * 16) / 2:.0f} {500 + k * 12}h{150 - k * 16}" for k in range(8))
    lights = "".join(f'<circle cx="{x}" cy="{deck - 6}" r="1.9"/>' for x in range(22, 590, 36))
    taxi = (f'<g transform="translate(-142 34)"><rect x="292" y="437" width="30" height="10" rx="2.5" fill="{MARIGOLD}"/>'
            f'<rect x="298" y="431" width="16" height="7" rx="2" fill="{MARIGOLD}"/>'
            f'<rect x="300" y="432.5" width="5" height="4" fill="#FDF1D2"/><rect x="307" y="432.5" width="5" height="4" fill="#FDF1D2"/>'
            f'<circle cx="299" cy="448" r="2.6" fill="{INK}"/><circle cx="315" cy="448" r="2.6" fill="{INK}"/></g>')
    bus = (f'<g transform="translate(-142 34)"><rect x="548" y="430" width="44" height="17" rx="3" fill="#4F9E94"/>'
           f'<path d="M553 435h34" stroke="#E3F4F1" stroke-width="3" stroke-dasharray="5 3"/>'
           f'<circle cx="556" cy="448" r="2.8" fill="{INK}"/><circle cx="584" cy="448" r="2.8" fill="{INK}"/></g>')
    lamp = (f'<g transform="translate(-32 64)"><circle cx="404" cy="478" r="34" fill="url(#lamp-glow)"/>'
            f'<rect x="398" y="568" width="12" height="8" rx="1" fill="{TEAL_DEEP}"/>'
            f'<rect x="402" y="488" width="4" height="82" fill="{TEAL_DEEP}"/>'
            f'<path d="M396 488h16" stroke="{TEAL_DEEP}" stroke-width="3"/>'
            f'<rect x="397" y="470" width="14" height="17" rx="2" fill="#FCE3A1" stroke="{TEAL_DEEP}" stroke-width="2"/>'
            f'<path d="M393 471L404 461L415 471Z" fill="{TEAL_DEEP}"/><circle cx="404" cy="458" r="2.5" fill="{TEAL_DEEP}"/></g>')
    # Kites: he (left) flies the right-hand kite, she flies the left one, so the strings cross.
    kites = kite(172, 152, -14, "#C0392B", "#FBF3E6") + kite(420, 128, 12, "#0F766E", MARIGOLD)
    strings = ('<path d="M214 600Q150 320 411 171M240 604Q300 380 182 195" stroke="#2F3B3B" '
               'stroke-width="1.1" fill="none" opacity=".6"/>')

    return f"""<svg class="hero-art" viewBox="0 0 600 720" aria-hidden="true">
<defs>
  <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#FFF8EA"/><stop offset=".62" stop-color="#FCE8BF"/><stop offset="1" stop-color="#F8D18C"/></linearGradient>
  <linearGradient id="river" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#C6E3DC"/><stop offset="1" stop-color="#E8F4F1"/></linearGradient>
  <radialGradient id="lamp-glow"><stop offset="0" stop-color="#FFD978" stop-opacity=".75"/>
    <stop offset="1" stop-color="#FFD978" stop-opacity="0"/></radialGradient>
  <clipPath id="window"><path d="{inner}"/></clipPath>
  <clipPath id="above-water"><rect width="600" height="{deck}"/></clipPath>
  <clipPath id="ring-left"><circle cx="{rl}" cy="{ry}" r="{rad}"/></clipPath>
</defs>
<g clip-path="url(#window)">
  <rect width="600" height="{deck}" fill="url(#sky)"/>
  {kites}
  <g clip-path="url(#above-water)">
    <g class="sun sun-left"><circle cx="{rl}" cy="{ry}" r="{rad}" fill="#FDEAC0"/>
      <circle cx="{rl}" cy="{ry}" r="{rad - 15}" fill="none" stroke="#E9A93A" stroke-width="2.4" {STITCH}/></g>
    <g class="sun sun-right"><circle cx="{rr}" cy="{ry}" r="{rad}" fill="#FDEAC0"/>
      <circle cx="{rr}" cy="{ry}" r="{rad - 15}" fill="none" stroke="#E9A93A" stroke-width="2.4" {STITCH}/></g>
    <g class="sun-lens"><circle cx="{rr}" cy="{ry}" r="{rad}" fill="{MARIGOLD}" clip-path="url(#ring-left)"/></g>
    <g class="sun sun-left"><circle cx="{rl}" cy="{ry}" r="{rad}" fill="none" stroke="#fff" stroke-width="9"/></g>
    <g class="sun sun-right"><circle cx="{rr}" cy="{ry}" r="{rad}" fill="none" stroke="#fff" stroke-width="9"/></g>
    {far}
    {victoria_memorial(40, deck, 0.8, "#B7D8D1")}
    {shahid_minar(212, deck, 0.85, "#A9CFC8")}
    {near}
    <g fill="#A9CFC0">{trees}</g>
  </g>
  <rect y="{deck}" width="600" height="{720 - deck}" fill="url(#river)"/>
  <path d="{refl_d}" stroke="{MARIGOLD}" stroke-width="4" {STITCH} opacity=".85"/>
  <path d="{wave_d}" stroke="#86BFB4" stroke-width="2.4" {STITCH}/>
  {bridge(-50, 662, deck - 9, 196, 20, "#7DB0A8", 2.6, 1.1)}
  {taxi}{bus}
  {bridge(-60, 660, deck, 204, 20, TEAL_DEEP, 4, 1.5, pier_bottom=535)}
  <g fill="#FFD36E">{lights}</g>
  {_boat(470, 600)}
  <rect y="640" width="440" height="40" fill="#EADFC9"/><rect y="676" width="480" height="40" fill="#DECDAF"/>
  <path d="M0 640H440M0 676H480" stroke="#C8B48F" stroke-width="2" {STITCH}/>
  {lamp}
  {strings}
  <g transform="translate(-30 64)">{_friends()}</g>
</g>
<path d="{arch}" fill="none" stroke="{TEAL_DEEP}" stroke-width="22"/>
<path d="{arch}" fill="none" stroke="{MARIGOLD}" stroke-width="3" stroke-dasharray="10 9" stroke-linecap="round"/>
</svg>"""


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
