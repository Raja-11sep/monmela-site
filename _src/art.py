# Hand-drawn (code-drawn) Kolkata illustrations for the website, as inline SVG.
#   hero_art()        - two suns (our logo's rings) setting behind Howrah Bridge, two friends on the ghat
#   skyline_footer()  - dotted Kolkata skyline above the footer
#   rings_art()       - two halftone rings for the "Download" panel
# Everything is plain SVG shapes, so it stays sharp at any size and weighs a few KB.

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

def hero_art():
    """Sunset over the Hooghly: the logo's two rings as two suns, Howrah Bridge, two friends on the ghat."""
    deck = 452                       # bridge deck = horizon
    sun_l, sun_r, sun_y, sun_r_ = 392, 512, 330, 140

    # Far skyline (behind the bridge), lightest teal
    far = buildings([(340, 26, 48), (372, 18, 62), (396, 30, 40), (520, 22, 56), (548, 30, 44),
                     (586, 16, 70), (606, 26, 52), (700, 22, 120), (728, 30, 96), (764, 20, 150),
                     (790, 28, 112), (824, 18, 136), (848, 34, 84), (884, 16, 60)], deck, "#CFE5E0")
    near = buildings([(250, 34, 30), (440, 40, 26), (628, 30, 34), (690, 46, 40), (742, 38, 54),
                      (790, 50, 36), (846, 54, 46)], deck, "#B7D8D1")

    trees = "".join(f'<circle cx="{x + (x * 7) % 9}" cy="{deck - 3}" r="{9 + (x * 13) % 7}"/>'
                    for x in range(0, 900, 17))
    clumps = "".join(f'<circle cx="{x}" cy="{y}" r="{r}"/>' for x, y, r in
                     [(70, 430, 22), (96, 438, 18), (48, 440, 16), (842, 432, 20), (870, 426, 24), (892, 440, 16)])
    clouds = ('<path d="M268 268h96M292 284h52M560 236h112M598 252h64" stroke="#FDF6E4" '
              'stroke-width="9" stroke-linecap="round"/>')

    # River: wave dashes + broken reflection of the suns
    waves = [(70, 492, 30), (160, 515, 22), (600, 488, 36), (780, 505, 26), (720, 600, 40),
             (110, 548, 18), (835, 570, 30), (560, 618, 24), (430, 600, 18), (640, 560, 20)]
    wave_d = "".join(f"M{x} {y}h{w}" for x, y, w in waves)
    refl = []
    for k in range(9):
        y = 468 + k * 13
        w = 170 - k * 17
        gap = 10 + k * 3
        cx = (sun_l + sun_r) / 2
        refl.append(f'M{_f(cx - w / 2)} {y}h{_f(w / 2 - gap / 2)}m{_f(gap)} 0h{_f(w / 2 - gap / 2)}')
    refl_d = "".join(refl)

    # Vehicles on the deck (drawn before the truss, so the lattice passes in front)
    taxi = (f'<g class="taxi"><rect x="292" y="437" width="30" height="10" rx="2.5" fill="{MARIGOLD}"/>'
            f'<rect x="298" y="431" width="16" height="7" rx="2" fill="{MARIGOLD}"/>'
            f'<rect x="300" y="432.5" width="5" height="4" fill="#FDF1D2"/><rect x="307" y="432.5" width="5" height="4" fill="#FDF1D2"/>'
            f'<circle cx="299" cy="448" r="2.6" fill="{INK}"/><circle cx="315" cy="448" r="2.6" fill="{INK}"/></g>')
    bus = (f'<rect x="548" y="430" width="44" height="17" rx="3" fill="#4F9E94"/>'
           f'<path d="M553 435h34" stroke="#E3F4F1" stroke-width="3" stroke-dasharray="5 3"/>'
           f'<circle cx="556" cy="448" r="2.8" fill="{INK}"/><circle cx="584" cy="448" r="2.8" fill="{INK}"/>')

    # Country boat with a canopy and a boatman; two small sails far away
    boat = (f'<g class="boat"><path d="M640 548Q700 568 760 548L753 557Q700 574 647 557Z" fill="{TEAL_DEEP}"/>'
            f'<path d="M668 549Q690 524 714 551Z" fill="#B9822B"/>'
            f'<path d="M735 550V524" stroke="{INK}" stroke-width="3.2" stroke-linecap="round"/>'
            f'<circle cx="735" cy="518" r="4.5" fill="{INK}"/>'
            f'<path d="M718 575L752 506" stroke="{INK}" stroke-width="1.6"/>'
            f'<path d="M648 566Q700 580 752 566" stroke="#9FCBC2" stroke-width="2" fill="none"/></g>')
    far_boats = ''.join(
        f'<g transform="translate({x} {y}) scale({k})" opacity=".55">'
        f'<path d="M-12 0q12 5 24 0l-2 4q-10 4-20 0z" fill="{TEAL_DEEP}"/>'
        f'<path d="M0 -1V-17l10 16z" fill="#B9822B"/></g>' for x, y, k in [(128, 474, 1), (822, 480, .8), (562, 466, .6)])

    # Ghat: sandstone steps, two columns (Prinsep Ghat feel) and a heritage lamp post
    joints = "".join(f"M{x} 576v24" for x in range(40, 430, 64)) + "".join(f"M{x} 600v22" for x in range(72, 470, 64))
    ghat = ('<g class="ghat">'
            '<rect x="14" y="478" width="14" height="98" fill="#EADFC9"/><rect x="48" y="478" width="14" height="98" fill="#EADFC9"/>'
            '<rect x="6" y="468" width="64" height="12" fill="#E0D2B6"/><path d="M6 468L38 450L70 468Z" fill="#E0D2B6"/>'
            '<rect x="0" y="576" width="430" height="64" fill="#EADFC9"/>'
            '<rect x="0" y="600" width="470" height="40" fill="#DECDAF"/>'
            '<rect x="0" y="622" width="510" height="18" fill="#CFBB98"/>'
            f'<path d="M0 576H430M0 600H470M0 622H510{joints}" stroke="#CDB997" stroke-width="1.5"/></g>')
    lamp = (f'<g class="lamp"><circle cx="404" cy="478" r="34" fill="url(#lamp-glow)"/>'
            f'<rect x="398" y="568" width="12" height="8" rx="1" fill="{TEAL_DEEP}"/>'
            f'<rect x="402" y="488" width="4" height="82" fill="{TEAL_DEEP}"/>'
            f'<path d="M396 488h16" stroke="{TEAL_DEEP}" stroke-width="3"/>'
            f'<rect x="397" y="470" width="14" height="17" rx="2" fill="#FCE3A1" stroke="{TEAL_DEEP}" stroke-width="2"/>'
            f'<path d="M393 471L404 461L415 471Z" fill="{TEAL_DEEP}"/><circle cx="404" cy="458" r="2.5" fill="{TEAL_DEEP}"/></g>')

    # Two friends from behind, leaning in a little: he has a jhola bag strap, she wears a
    # red-bordered (laal paar) saree with a flower in her bun. A clay chai cup (bhar) with steam.
    friends = (f'<g class="friends">'
               f'<g transform="rotate(4 230 576)">'
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
               f'<path d="M313 562q-3-4 0-8M318 562q-3-4 0-8" stroke="#9DB3AF" stroke-width="1.3" fill="none" '
               f'stroke-linecap="round"/></g>')

    birds = "".join(f'<path d="M{x} {y}q{_f(6 * s)} {_f(-6 * s)} {_f(12 * s)} 0q{_f(6 * s)} {_f(-6 * s)} {_f(12 * s)} 0"/>'
                    for x, y, s in [(250, 150, 1), (282, 172, .8), (612, 120, 1.1), (650, 146, .8), (580, 168, .7)])
    lights = "".join(f'<circle cx="{x}" cy="{deck - 6}" r="1.9"/>' for x in range(76, 850, 38))
    front_bridge = bridge(40, 860, deck, 220, 20.5, TEAL_DEEP, 4, 1.5, pier_bottom=500)
    river_h = 640 - deck

    return f"""<svg class="hero-art" viewBox="0 0 900 640" aria-hidden="true" preserveAspectRatio="xMidYMax meet">
<defs>
  <pattern id="dots-sun" width="8" height="8" patternUnits="userSpaceOnUse">
    <circle cx="2" cy="2" r="1.8" fill="{MARIGOLD}"/><circle cx="6" cy="6" r="1.8" fill="{MARIGOLD}"/></pattern>
  <pattern id="dots-far" width="6" height="6" patternUnits="userSpaceOnUse">
    <circle cx="1.5" cy="1.5" r="1.1" fill="#9CC9C1"/></pattern>
  <pattern id="ripple" width="10" height="5" patternUnits="userSpaceOnUse">
    <rect width="10" height="2.6" fill="#fff"/></pattern>
  <linearGradient id="sun-base" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#FDF1D2"/><stop offset="1" stop-color="#F8CB6C"/></linearGradient>
  <linearGradient id="dot-fade" x1="0" y1="0" x2="0" y2="1">
    <stop offset=".15" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#fff" stop-opacity="1"/></linearGradient>
  <mask id="sun-dot-mask"><rect x="0" y="180" width="900" height="280" fill="url(#dot-fade)"/></mask>
  <radialGradient id="sky-glow" gradientUnits="userSpaceOnUse" cx="452" cy="440" r="430">
    <stop offset="0" stop-color="#F7BE55" stop-opacity=".5"/><stop offset=".45" stop-color="#FAD995" stop-opacity=".22"/>
    <stop offset="1" stop-color="#FBF8F3" stop-opacity="0"/></radialGradient>
  <radialGradient id="water-glow" gradientUnits="userSpaceOnUse" cx="452" cy="{deck + 14}" r="210" gradientTransform="matrix(1 0 0 .22 0 {(deck + 14) * .78})">
    <stop offset="0" stop-color="#F7BE55" stop-opacity=".55"/><stop offset="1" stop-color="#F7BE55" stop-opacity="0"/></radialGradient>
  <radialGradient id="lamp-glow"><stop offset="0" stop-color="#FFD978" stop-opacity=".75"/>
    <stop offset="1" stop-color="#FFD978" stop-opacity="0"/></radialGradient>
  <linearGradient id="river" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#C3E1DA"/><stop offset="1" stop-color="#E8F4F1"/></linearGradient>
  <pattern id="dots-river" width="7" height="7" patternUnits="userSpaceOnUse">
    <circle cx="2" cy="2" r="1.3" fill="#A9D3CA"/></pattern>
  <linearGradient id="river-fade" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#fff"/><stop offset=".7" stop-color="#fff" stop-opacity="0"/></linearGradient>
  <mask id="river-dot-mask"><rect x="0" y="{deck}" width="900" height="{river_h}" fill="url(#river-fade)"/></mask>
  <mask id="ripple-mask"><rect x="0" y="{deck}" width="900" height="{river_h}" fill="url(#ripple)"/></mask>
  <clipPath id="above-water"><rect x="0" y="0" width="900" height="{deck}"/></clipPath>
  <clipPath id="below-water"><rect x="0" y="{deck + 3}" width="900" height="{river_h}"/></clipPath>
  <clipPath id="sun-left-clip"><circle cx="{sun_l}" cy="{sun_y}" r="{sun_r_}"/></clipPath>
  <clipPath id="painted">
    <circle cx="{sun_l}" cy="{sun_y}" r="{sun_r_}"/><circle cx="{sun_r}" cy="{sun_y}" r="{sun_r_}"/>
    <rect x="0" y="{deck}" width="900" height="{river_h}"/></clipPath>
  <filter id="grain" filterUnits="userSpaceOnUse" x="0" y="0" width="900" height="640">
    <feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="7" stitchTiles="stitch"/>
    <feColorMatrix values="0 0 0 0 .06  0 0 0 0 .2  0 0 0 0 .19  3 0 0 0 -1.62"/>
  </filter>
</defs>
<rect width="900" height="{deck}" fill="url(#sky-glow)"/>
<g class="birds" stroke="{INK}" stroke-width="2" fill="none" stroke-linecap="round">{birds}</g>
<g clip-path="url(#above-water)">
  <g class="sun sun-left">
    <circle cx="{sun_l}" cy="{sun_y}" r="{sun_r_}" fill="url(#sun-base)"/>
    <circle cx="{sun_l}" cy="{sun_y}" r="{sun_r_}" fill="url(#dots-sun)" mask="url(#sun-dot-mask)" opacity=".65"/>
  </g>
  <g class="sun sun-right">
    <circle cx="{sun_r}" cy="{sun_y}" r="{sun_r_}" fill="url(#sun-base)"/>
    <circle cx="{sun_r}" cy="{sun_y}" r="{sun_r_}" fill="url(#dots-sun)" mask="url(#sun-dot-mask)" opacity=".65"/>
  </g>
  <g class="sun-lens"><circle cx="{sun_r}" cy="{sun_y}" r="{sun_r_}" fill="{MARIGOLD}" clip-path="url(#sun-left-clip)"/></g>
  {far}
  <g>{far.replace('fill="#CFE5E0"', 'fill="url(#dots-far)"')}</g>
  {victoria_memorial(64, deck, 0.95, "#B7D8D1")}
  {shahid_minar(322, deck, 0.95, "#A9CFC8")}
  {clouds}
  {near}
  <g fill="#A9CFC0">{trees}</g>
  <g fill="#86B9A6">{clumps}</g>
</g>
<rect x="0" y="{deck}" width="900" height="{river_h}" fill="url(#river)"/>
<rect x="0" y="{deck}" width="900" height="{river_h}" fill="url(#dots-river)" mask="url(#river-dot-mask)"/>
<rect x="0" y="{deck}" width="900" height="{river_h}" fill="url(#water-glow)"/>
<g clip-path="url(#below-water)" mask="url(#ripple-mask)" opacity=".2">
  <g transform="matrix(1 0 0 -.55 0 {deck * 1.55})">{front_bridge}</g></g>
<path d="{refl_d}" stroke="{MARIGOLD}" stroke-width="4" stroke-linecap="round" opacity=".85"/>
<path d="{wave_d}" stroke="#A3CFC7" stroke-width="2.4" stroke-linecap="round"/>
{far_boats}
{bridge(54, 874, deck - 9, 212, 20.5, "#7DB0A8", 2.6, 1.1)}
{taxi}{bus}
{front_bridge}
<g fill="#FFD36E">{lights}</g>
{boat}
{ghat}
{lamp}
{friends}
<rect class="grain" width="900" height="640" filter="url(#grain)" clip-path="url(#painted)" opacity=".5"/>
</svg>"""


# ---------------------------------------------------------------- footer skyline

def skyline_footer():
    """Kolkata skyline in dots: Victoria Memorial, Shahid Minar, a tram, Howrah Bridge, Biswa Bangla Gate."""
    g = 196  # ground line
    blocks = buildings([(300, 40, 54), (346, 26, 80), (378, 34, 46), (470, 30, 96), (506, 44, 62),
                        (556, 26, 110), (590, 38, 70), (760, 34, 58), (800, 24, 84), (830, 40, 50),
                        (1380, 30, 70), (1520, 26, 150), (1552, 36, 120), (1594, 6, 40)], g, "#fff")
    tram = (f'<g><rect x="636" y="{g - 40}" width="104" height="34" rx="6" fill="#fff"/>'
            f'<path d="M688 {g - 40}l-14 -18h28" stroke="#fff" stroke-width="3" fill="none"/>'
            + "".join(f'<rect x="{646 + i * 18}" y="{g - 33}" width="11" height="12" rx="2" fill="#000"/>' for i in range(5))
            + f'<circle cx="658" cy="{g - 3}" r="5" fill="#fff"/><circle cx="718" cy="{g - 3}" r="5" fill="#fff"/></g>')
    gate = (f'<g stroke="#fff" fill="none"><circle cx="1420" cy="{g - 110}" r="38" stroke-width="12"/>'
            f'<path d="M1392 {g}L1406 {g - 76}M1448 {g}L1434 {g - 76}" stroke-width="7"/></g>')
    return f"""<svg class="skyline" viewBox="0 0 1600 200" preserveAspectRatio="xMidYMax slice" aria-hidden="true">
<defs>
  <pattern id="dots-foot" width="6" height="6" patternUnits="userSpaceOnUse">
    <circle cx="3" cy="3" r="1.5" fill="#8FB5AE"/></pattern>
  <mask id="skyline-mask" maskUnits="userSpaceOnUse" x="0" y="0" width="1600" height="200">
    <rect width="1600" height="200" fill="#000"/>
    {victoria_memorial(120, g, 1.3, "#fff")}
    {shahid_minar(430, g, 1.05, "#fff")}
    {blocks}
    {tram}
    {bridge(880, 1340, g - 4, 150, 23, "#fff", 5, 2.6)}
    {gate}
    <rect x="0" y="{g - 2}" width="1600" height="6" fill="#fff"/>
  </mask>
</defs>
<rect width="1600" height="200" fill="url(#dots-foot)" mask="url(#skyline-mask)"/>
</svg>"""


def rings_art():
    """Two overlapping halftone rings (the logo), for the dark download panel."""
    return f"""<svg class="rings-art" viewBox="0 0 400 300" aria-hidden="true">
<defs>
  <pattern id="dots-ring" width="9" height="9" patternUnits="userSpaceOnUse">
    <circle cx="4.5" cy="4.5" r="2" fill="{MARIGOLD}"/></pattern>
  <clipPath id="ring-left-clip"><circle cx="160" cy="150" r="120"/></clipPath>
</defs>
<circle cx="160" cy="150" r="120" fill="url(#dots-ring)" opacity=".45"/>
<circle cx="250" cy="150" r="120" fill="url(#dots-ring)" opacity=".45"/>
<circle cx="250" cy="150" r="120" fill="{MARIGOLD}" clip-path="url(#ring-left-clip)"/>
</svg>"""
