# Paints the home page picture: friends on a Ganga ghat, Howrah Bridge behind them, at sunset.
#
# Usage (from the site folder):   python3 _src/tools/make_hero.py            golden sunset (the one on the site)
#                                 python3 _src/tools/make_hero.py dusk       blue hour, bridge lights on
#                                 python3 _src/tools/make_hero.py morning    misty morning
# Needs: rsvg-convert (librsvg) and Pillow. Writes img/hero-ghat.webp; then run _src/build.py.
#
# Why a picture file and not inline SVG like before: this scene uses soft blurs and rippled
# reflections, which are slow to draw live on cheap phones. Painted once here, it loads as one
# small image. The kites and the stitched frame stay as live SVG on top (see art.hero_art).
import io
import pathlib
import random
import subprocess
import sys

SRC = pathlib.Path(__file__).resolve().parent.parent      # _src/
ROOT = SRC.parent                                          # the site folder
sys.path.insert(0, str(SRC))
import art  # noqa: E402  (the bridge drawing lives there)

ARCH = art.ARCH        # frame centre line
INNER = art.INNER      # what the window shows
H = 432          # horizon line
SX = 318         # sun's x
WIDTH = 1000     # pixels; shown at up to 500 px wide, so sharp on 2x screens


def mix(a, b, t):
    """Blend two #rrggbb colours: t=0 gives a, t=1 gives b."""
    pa, pb = [int(a[i:i + 2], 16) for i in (1, 3, 5)], [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02X}" for x, y in zip(pa, pb))


def grad(gid, stops, x2=0, y2=1):
    s = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops)
    return f'<linearGradient id="{gid}" x1="0" y1="0" x2="{x2}" y2="{y2}">{s}</linearGradient>'


# ---------------------------------------------------------------- people, seen from behind
TORSO = ("M-23 2C-25 -9 -17 -17 -16 -27C-16 -36 -24 -40 -22 -48C-20 -54 -10 -56 -6 -57L-5 -61H5L6 -57"
         "C10 -56 20 -54 22 -48C24 -40 16 -36 16 -27C17 -17 25 -9 23 2Z")
HAIRCAP = "M-11.2 -70C-12.4 -90 12.4 -90 11.2 -70C10.6 -64 6 -61.5 0 -61.5C-6 -61.5 -10.6 -64 -11.2 -70Z"
LONGHAIR = "M-11.2 -72C-12.6 -90 12.6 -90 11.2 -72C12.5 -58 13.5 -44 10 -33C4 -29 -4 -29 -10 -33C-13.5 -44 -12.5 -58 -11 -72Z"


def back_sit(x, y, s, cloth, skin, P, hair="short", saree=None, strap=None, arm="down", tilt=0, lower=None):
    """A friend sitting on the step with their back to us. (x, y) = middle of the seat."""
    sh = P["shade"]
    c = lambda col: mix(col, P["sil"], sh)          # everything is in shadow: the light is in front of them
    rim, hairc = P["rim"], mix("#1B1418", P["sil"], sh * .6)
    lower = lower or cloth
    g = [f'<g transform="translate({x} {y}) rotate({tilt}) scale({s})">']
    # rim light: the same outline, a touch higher, in the light's colour
    g.append(f'<g transform="translate(0 -1.3)" fill="{rim}" opacity=".9"><path d="{TORSO}"/>'
             f'<path d="{HAIRCAP}"/></g>')
    # arms resting on the step (drawn first so the body overlaps the shoulders)
    def arm_down(sign):
        return (f'<path d="M{21 * sign} -46C{27 * sign} -40 {29 * sign} -32 {29.5 * sign} -25" stroke="{c(cloth)}" stroke-width="9" fill="none" stroke-linecap="round"/>'
                f'<path d="M{29.5 * sign} -25C{30 * sign} -17 {31 * sign} -10 {32 * sign} -4" stroke="{c(skin)}" stroke-width="5.6" fill="none" stroke-linecap="round"/>'
                f'<ellipse cx="{34 * sign}" cy="-1.5" rx="5" ry="2.8" fill="{c(skin)}"/>')
    if arm in ("down", "point"):
        g.append(arm_down(-1))
    if arm == "down":
        g.append(arm_down(1))
    if arm == "point":   # right arm raised, pointing at the river
        g.append(f'<path d="M21 -46C31 -49 38 -54 43 -60" stroke="{c(cloth)}" stroke-width="9" fill="none" stroke-linecap="round"/>'
                 f'<path d="M43 -60C49 -65 55 -70 61 -75" stroke="{c(skin)}" stroke-width="5.4" fill="none" stroke-linecap="round"/>'
                 f'<path d="M61 -75l8 -5" stroke="{c(skin)}" stroke-width="2.6" stroke-linecap="round"/>'
                 f'<path d="M42 -63C49 -68 55 -73 62 -78" stroke="{rim}" stroke-width="1.1" fill="none" opacity=".8"/>')
    # seat and torso
    g.append(f'<path d="M-27 5C-29 -8 -14 -13 0 -13C14 -13 29 -8 27 5Z" fill="{c(lower)}"/>')
    g.append(f'<path d="{TORSO}" fill="{c(cloth)}"/>')
    g.append(f'<path d="M0 -50C1 -36 1 -20 0 -6" stroke="{P["sil"]}" stroke-width="1.2" fill="none" opacity=".25"/>')  # spine fold
    if saree:   # the pallu falling down the back, with its border; a bit of blouse at the other shoulder
        g.append(f'<path d="M4 -57C12 -56 20 -54 22 -48C23 -43 18 -40 17 -35L5 -41Z" fill="{c(saree)}"/>')
        g.append(f'<path d="M-22 -49L-7 -57L6 3L-15 4Z" fill="{c(mix(cloth, "#FFFFFF", .18))}"/>')
        g.append(f'<path d="M-7 -57L6 3M-22 -49L-15 4" stroke="{c(saree)}" stroke-width="2.6" fill="none"/>')
    if strap:   # cloth bag (jhola) strap across the back
        g.append(f'<path d="M15 -55L-19 -8" stroke="{c(strap)}" stroke-width="3.2"/>'
                 f'<path d="M-27 -10q8 -6 16 0v12h-16Z" fill="{c(strap)}"/>')
    # neck, head, hair
    g.append(f'<rect x="-5" y="-63" width="10" height="8" fill="{c(skin)}"/>')
    g.append(f'<ellipse cx="0" cy="-72" rx="10.6" ry="11.6" fill="{c(skin)}"/>')
    g.append(f'<circle cx="-10.6" cy="-70" r="2" fill="{c(skin)}"/><circle cx="10.6" cy="-70" r="2" fill="{c(skin)}"/>')
    if hair == "long":
        g.append(f'<path d="{LONGHAIR}" fill="{hairc}"/>')
    else:
        g.append(f'<path d="{HAIRCAP}" fill="{hairc}"/>')
    if hair == "bun":
        g.append(f'<circle cx="0" cy="-73" r="6.6" fill="{hairc}" stroke="{mix(hairc, rim, .25)}" stroke-width=".8"/>')
        g.append("".join(f'<circle cx="{dx}" cy="{dy}" r="1.5" fill="#FFF8EE" opacity=".95"/>'
                         for dx, dy in ((-6.5, -70), (-4, -66.8), (0, -65.6), (4, -66.8), (6.5, -70))))
    if hair == "braid":
        g.append(f'<path d="M0 -62C2 -52 -1 -42 1 -30" stroke="{hairc}" stroke-width="5.2" fill="none" stroke-linecap="round"/>'
                 f'<path d="M-2.2 -31h6.4l-1 5h-4.4Z" fill="{c("#C0392B")}"/>')
    # soft shading: the lower back is darker than the shoulders
    g.append(f'<path d="M-17 -24C-17 -17 -25 -9 -23 2H23C25 -9 17 -17 17 -24Z" fill="{P["sil"]}" opacity=".1" filter="url(#blur1)"/>')
    return "".join(g) + "</g>"


def shadow(x, y, s):
    """Long soft shadow falling towards us, leaning away from the sun."""
    lean = (x - SX) * .22
    return (f'<path d="M{x - 24 * s:.0f} {y + 3}L{x + 24 * s:.0f} {y + 3}L{x + 30 * s + lean:.0f} {y + 70}L{x - 30 * s + lean:.0f} {y + 70}Z" '
            f'fill="#000" opacity=".2" filter="url(#blur3)"/>')


# ---------------------------------------------------------------- things in the scene
def nouka(x, y, s, P, lantern=False):
    """Country boat with a bamboo canopy and a boatman rowing at the stern."""
    col = P["sil"]
    b = (f'<path d="M-80 -9Q-40 11 0 12Q44 12 82 -13Q62 17 0 20Q-58 20 -80 -9Z" fill="{col}"/>'
         f'<path d="M-36 12Q-34 -13 -8 -13Q16 -13 18 12Z" fill="{mix(col, P["rim"], .22)}"/>'
         f'<path d="M-28 11Q-26 -8 -8 -9M-18 11Q-17 -11 -8 -12M-8 11V-12M2 11Q1 -11 -8 -12M11 11Q9 -6 -4 -11M-34 2H17M-30 -5H13" stroke="{col}" stroke-width=".9" fill="none" opacity=".55"/>'
         f'<path d="M50 6L53 -8L51 -26" stroke="{col}" stroke-width="5.4" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
         f'<path d="M51 -25L42 -12M51 -24L62 -13" stroke="{col}" stroke-width="3.2" stroke-linecap="round"/>'
         f'<circle cx="51" cy="-33" r="5.2" fill="{col}"/><path d="M45 -37q6 -6 12 0Z" fill="{col}"/>'
         f'<path d="M34 -34L84 30" stroke="{col}" stroke-width="1.8"/>'
         f'<path d="M-78 -9Q-40 9 0 10Q44 10 80 -12" stroke="{P["rim"]}" stroke-width="1.1" fill="none" opacity=".7"/>')
    if lantern:
        b += f'<circle cx="-40" cy="-4" r="14" fill="url(#lampGlow)"/><circle cx="-40" cy="-4" r="2.4" fill="#FFE2A0"/>'
    refl = (f'<g transform="scale(1 -1) translate(0 -34)" opacity=".38" filter="url(#ripple)">'
            f'<path d="M-80 -9Q-40 11 0 12Q44 12 82 -13Q62 17 0 20Q-58 20 -80 -9Z" fill="{col}"/>'
            f'<path d="M-34 12Q-32 -15 -6 -15Q18 -15 20 12Z" fill="{col}"/><path d="M52 4L50 -30" stroke="{col}" stroke-width="5"/></g>')
    return f'<g transform="translate({x} {y}) scale({s})">{refl}{b}</g>'


def launch(x, y, s, P):
    """A small river ferry, far away."""
    col = P["haze2"]
    return (f'<g transform="translate({x} {y}) scale({s})" fill="{col}"><path d="M-26 0H26L20 7H-21Z"/>'
            f'<rect x="-16" y="-9" width="28" height="9"/><rect x="-10" y="-14" width="14" height="5"/><rect x="4" y="-20" width="3" height="8"/></g>')


def lamp(x, base, P):
    lit = P["lights"]
    col = P["sil"]
    g = ""
    if lit:
        g += f'<circle cx="{x}" cy="{base - 150}" r="74" fill="url(#lampGlow)"/>'
    g += (f'<path d="M{x - 9} {base}h18l-3 -10h-12Z" fill="{col}"/><rect x="{x - 2.6}" y="{base - 134}" width="5.2" height="126" fill="{col}"/>'
          f'<path d="M{x - 9} {base - 134}h18" stroke="{col}" stroke-width="3.4"/>'
          f'<path d="M{x - 8} {base - 136}l2 -22h12l2 22Z" fill="{"#FFE7A6" if lit else mix(P["rim"], col, .45)}" stroke="{col}" stroke-width="2.2"/>'
          f'<path d="M{x - 12} {base - 158}L{x} {base - 172}L{x + 12} {base - 158}Z" fill="{col}"/><circle cx="{x}" cy="{base - 175}" r="2.6" fill="{col}"/>'
          f'<path d="M{x + 3} {base - 130}V{base - 10}" stroke="{P["rim"]}" stroke-width="1" opacity=".6"/>')
    return g


def kash(x, y, h, lean, P):
    """Kash phool, backlit: a thin stem and a glowing feathery plume."""
    tx, ty = x + lean, y - h
    plume = mix("#FFFDF4", P["rim"], .25)
    return (f'<path d="M{x} {y}Q{x + lean * .15:.0f} {y - h * .6:.0f} {tx} {ty}" stroke="{mix("#6E8F6E", P["sil"], P["shade"])}" stroke-width="2.2" fill="none"/>'
            f'<path d="M{tx} {ty}q{lean * .5 + 11:.0f} {-h * .2:.0f} {lean * .9 + 5:.0f} {-h * .46:.0f}q{-lean * .2 - 15:.0f} {h * .2:.0f} {-lean * .9 - 5:.0f} {h * .46:.0f}Z" '
            f'fill="{plume}" opacity=".95"/>'
            f'<path d="M{tx} {ty}q{lean * .5 + 4:.0f} {-h * .2:.0f} {lean * .9 + 5:.0f} {-h * .46:.0f}" stroke="{mix(plume, P["sil"], .3)}" stroke-width="1" fill="none" opacity=".6"/>')


def banyan(P):
    """Out-of-focus banyan bough hanging in from the top left, for depth."""
    rnd = random.Random(3)
    col = mix(P["sil"], "#1F3B2C", .4)
    lit = mix(col, P["rim"], .18)
    boughs = [((-10, 150), (70, 150), (150, 112)), ((60, 150), (120, 200), (150, 250)), ((40, 148), (40, 220), (62, 290)),
              ((120, 126), (200, 80), (268, 96)), ((150, 112), (190, 150), (236, 168))]
    wood, leaves = "", ""
    for (x0, y0), (cx, cy), (x1, y1) in boughs:
        wood += f'<path d="M{x0} {y0}Q{cx} {cy} {x1} {y1}" stroke="{col}" stroke-width="5" fill="none" stroke-linecap="round"/>'
        for i in range(34):
            t = rnd.uniform(.15, 1.08)
            px = (1 - t) ** 2 * x0 + 2 * t * (1 - t) * cx + t * t * x1 + rnd.gauss(0, 13)
            py = (1 - t) ** 2 * y0 + 2 * t * (1 - t) * cy + t * t * y1 + rnd.gauss(4, 12)
            fill = lit if rnd.random() < .1 else col
            leaves += (f'<ellipse cx="{px:.0f}" cy="{py:.0f}" rx="8.5" ry="4.2" fill="{fill}" '
                       f'transform="rotate({rnd.uniform(25, 85):.0f} {px:.0f} {py:.0f})"/>')
    return f'<g filter="url(#blur1)">{wood}{leaves}</g>'


# ---------------------------------------------------------------- the scene
def scene(P):
    rnd = random.Random(11)
    sy = P["sun_y"]
    defs = (grad("sky", P["sky"]) + grad("water", P["water"])
            + f'<radialGradient id="sunGlow"><stop offset="0" stop-color="{P["glow"]}" stop-opacity=".95"/>'
              f'<stop offset=".35" stop-color="{P["glow"]}" stop-opacity=".45"/><stop offset="1" stop-color="{P["glow"]}" stop-opacity="0"/></radialGradient>'
            + '<radialGradient id="lampGlow"><stop offset="0" stop-color="#FFD98A" stop-opacity=".9"/><stop offset="1" stop-color="#FFD98A" stop-opacity="0"/></radialGradient>'
            + f'<radialGradient id="vig" cx=".5" cy=".56" r=".72"><stop offset=".55" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity="{P["vignette"]}"/></radialGradient>'
            + '<filter id="blur1"><feGaussianBlur stdDeviation="1.1"/></filter><filter id="blur3"><feGaussianBlur stdDeviation="3"/></filter>'
              '<filter id="blur8" x="-30%" y="-80%" width="160%" height="260%"><feGaussianBlur stdDeviation="8"/></filter>'
              '<filter id="ripple" x="-5%" y="-5%" width="110%" height="110%"><feTurbulence type="fractalNoise" baseFrequency="0.008 0.3" numOctaves="2" seed="4" result="n"/>'
              '<feDisplacementMap in="SourceGraphic" in2="n" scale="5" xChannelSelector="R" yChannelSelector="G"/><feGaussianBlur stdDeviation="1.3 .5"/></filter>'
            + f'<clipPath id="waterclip"><rect y="{H}" width="600" height="{720 - H}"/></clipPath>')

    b = f'<rect width="600" height="{H + 2}" fill="url(#sky)"/>'
    if P["stars"]:
        b += "".join(f'<circle cx="{rnd.uniform(40, 560):.0f}" cy="{rnd.uniform(40, 250):.0f}" r="{rnd.uniform(.6, 1.5):.1f}" fill="#fff" opacity="{rnd.uniform(.4, .95):.2f}"/>' for _ in range(46))
        b += '<path d="M452 112a26 26 0 1 0 22 40a21 21 0 1 1 -22 -40Z" fill="#FFF3D0" opacity=".95"/>'
    b += f'<circle cx="{SX}" cy="{sy}" r="230" fill="url(#sunGlow)"/>'
    if P["sun_visible"]:
        b += f'<circle cx="{SX}" cy="{sy}" r="33" fill="{P["sun"]}"/>'
    # clouds: soft dark bodies, their undersides lit by the sun
    for cx, cy, rx, ry in ((150, 250, 120, 13), (430, 215, 140, 15), (300, 300, 170, 10), (90, 330, 90, 8), (500, 335, 110, 9), (250, 170, 90, 10)):
        b += f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{P["cloud"]}" opacity="{P["cloud_op"]}" filter="url(#blur8)"/>'
        b += f'<ellipse cx="{cx + 6}" cy="{cy + ry * .7:.0f}" rx="{rx * .8:.0f}" ry="{ry * .45:.0f}" fill="{P["cloud_lit"]}" opacity="{P["cloud_op"] * .9:.2f}" filter="url(#blur8)"/>'
    # birds heading home
    for bx, by, bs in ((120, 300, 1), (140, 290, .8), (163, 296, .9), (470, 262, .8), (490, 270, .7), (96, 312, .7)):
        b += f'<path d="M{bx - 7 * bs:.1f} {by}q{3.5 * bs:.1f} {-4 * bs:.1f} {7 * bs:.1f} 0q{3.5 * bs:.1f} {-4 * bs:.1f} {7 * bs:.1f} 0" stroke="{P["bridge"]}" stroke-width="1.3" fill="none" opacity=".75"/>'

    # far bank: hazy skyline, then Howrah Bridge in two planes (far truss lighter)
    far = ""
    x = -10
    while x < 610:
        w, hgt = rnd.uniform(10, 30), rnd.uniform(5, 30) * (1.5 if rnd.random() < .12 else 1)
        far += f'<rect x="{x:.0f}" y="{H - hgt:.0f}" width="{w:.0f}" height="{hgt + 2:.0f}" fill="{P["haze"]}"/>'
        x += w + rnd.uniform(-2, 8)
    tx = -6.0
    while tx < 606:
        r = rnd.uniform(3, 9)
        far += f'<ellipse cx="{tx:.0f}" cy="{H - 2}" rx="{r * 1.5:.0f}" ry="{r:.0f}" fill="{P["haze2"]}"/>'
        tx += rnd.uniform(6, 30)
    deck, th = H - 13, 112
    far += art.bridge(-64, 676, deck - 3, th - 5, 15, P["bridge_back"], 1.8, .8)
    far += art.bridge(-70, 670, deck, th, 15, P["bridge"], 2.8, 1.05, pier_bottom=H + 6)
    far += f'<rect x="-10" y="{H - 2}" width="620" height="5" fill="{P["haze2"]}"/>'
    if P["lights"]:
        pts, _ = art._bridge_points(-70, 670, deck, th)
        far += "".join(f'<circle cx="{lx}" cy="{art._top_y(pts, lx) - 1:.1f}" r="1.5" fill="#FFE2A0"/>' for lx in range(-66, 670, 12))
        far += "".join(f'<circle cx="{lx}" cy="{deck - 2}" r="1.3" fill="#FFD08A"/>' for lx in range(-60, 670, 9))
        far += "".join(f'<rect x="{rnd.uniform(0, 600):.0f}" y="{H - rnd.uniform(4, 24):.0f}" width="2" height="2" fill="#FFD08A" opacity=".85"/>' for _ in range(60))
    b += f'<g id="far">{far}</g>'

    # the river: sky colours, the far bank mirrored and rippled, the sun's glitter path
    b += f'<rect y="{H}" width="600" height="{720 - H}" fill="url(#water)"/>'
    b += (f'<g clip-path="url(#waterclip)"><g transform="translate(0 {2 * H}) scale(1 -1)" opacity="{P["refl"]}" filter="url(#ripple)">'
          f'<use xlink:href="#far"/></g></g>')
    glit = ""
    for _ in range(150):
        t = rnd.random() ** 1.6                      # more strokes near the horizon
        y = H + 3 + t * 255
        spread = 12 + (y - H) * .42
        gx = SX + rnd.gauss(0, spread * .5)
        ln = rnd.uniform(5, 16) * (1 + (y - H) / 90)
        glit += (f'<path d="M{gx - ln / 2:.1f} {y:.1f}h{ln:.1f}" stroke="{P["glitter"]}" stroke-width="{1 + (y - H) / 95:.1f}" '
                 f'opacity="{rnd.uniform(.35, .95):.2f}" stroke-linecap="round"/>')
    b += glit
    for _ in range(70):                               # small ripples catching the sky everywhere
        y = H + 6 + rnd.random() * 260
        ln = rnd.uniform(10, 34) * (1 + (y - H) / 160)
        b += (f'<path d="M{rnd.uniform(20, 580):.0f} {y:.0f}h{ln:.0f}" stroke="{P["ripple"]}" stroke-width="{.8 + (y - H) / 170:.1f}" '
              f'opacity="{rnd.uniform(.12, .34):.2f}" stroke-linecap="round"/>')
    if P["mist"]:
        b += f'<rect x="-40" y="{H - 34}" width="680" height="60" fill="#fff" opacity="{P["mist"]}" filter="url(#blur8)"/>'
    b += launch(196, H + 9, .8, P) + nouka(410, 508, 1.0, P, lantern=P["lights"])

    # the ghat: stone steps going down to the water (far ones higher up and thinner)
    st = P["stone"]
    bands = [(590, 604, st[0]), (604, 628, st[1]), (628, 664, st[2]), (664, 724, st[3])]
    for y0, y1, col in bands:
        b += f'<rect y="{y0}" width="600" height="{y1 - y0}" fill="{col}"/>'
        b += f'<path d="M0 {y0 + .8}H600" stroke="{P["stone_edge"]}" stroke-width="1.6" opacity=".75"/>'
        b += f'<rect y="{y1 - 5}" width="600" height="5" fill="#000" opacity=".16"/>'
        joints = "".join(f"M{jx + (y0 % 37)} {y0 + 3}V{y1 - 5}" for jx in range(-20, 620, 86))
        b += f'<path d="{joints}" stroke="#000" stroke-width="1" opacity=".13"/>'
    b += f'<rect y="586" width="600" height="6" fill="{P["glitter"]}" opacity=".25" filter="url(#blur1)"/>'   # wet edge
    b += f'<ellipse cx="{SX}" cy="640" rx="210" ry="46" fill="{P["glow"]}" opacity=".16" filter="url(#blur8)"/>'  # warm light on the stone

    # four friends on the steps, backs to us, watching the river; chai cups and jhalmuri between them
    cl = P["cloth"]
    seats = [(132, 650, 1.34), (218, 652, 1.3), (304, 650, 1.32), (390, 652, 1.36)]
    b += "".join(shadow(x, y, s) for x, y, s in seats)
    b += lamp(520, 640, P)
    b += back_sit(*seats[0], cl[0], "#A86B45", P, hair="short", strap="#D9A441", arm="down", tilt=3)
    b += back_sit(*seats[1], cl[1], "#C68A5E", P, hair="bun", saree="#B5301F", arm="down", tilt=-3, lower=cl[1])
    b += back_sit(*seats[2], cl[2], "#B97A50", P, hair="braid", arm="down", tilt=2, lower="#0F5F58")
    b += back_sit(*seats[3], cl[3], "#C68A5E", P, hair="short", arm="point", tilt=-2, lower="#3A3F55")
    cup = mix("#B5643C", P["sil"], P["shade"] * .7)
    for cx in (175, 261, 347):
        b += f'<path d="M{cx - 5} 640l1.6 10h6.8l1.6 -10Z" fill="{cup}"/><ellipse cx="{cx}" cy="640" rx="5" ry="1.6" fill="{mix(cup, P["rim"], .5)}"/>'

    # foreground: kash phool, banyan leaves; then a soft vignette like a camera lens
    b += f'<g filter="url(#blur1)">' + "".join(kash(x, 722, h, l, P) for x, h, l in
                                              [(468, 104, 12), (492, 142, -8), (516, 112, 18), (540, 150, 4), (562, 104, -14), (54, 92, -10), (78, 124, 10)]) + "</g>"
    b += banyan(P)
    b += '<rect width="600" height="720" fill="url(#vig)"/>'

    return f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 600 720">
<defs><clipPath id="window"><path d="{INNER}"/></clipPath>{defs}</defs>
<g clip-path="url(#window)">{b}</g>
<path d="{ARCH}" fill="none" stroke="{art.TEAL_DEEP}" stroke-width="22"/>
</svg>"""


SUNSET = dict(
    sky=[(0, "#2F4A7C"), (.3, "#8A6798"), (.52, "#E08A6C"), (.76, "#F8B55C"), (1, "#FFE7A6")],
    water=[(0, "#FBD58A"), (.1, "#F0A56A"), (.42, "#A5677B"), (1, "#2C3357")],
    sun="#FFF4CC", sun_y=H - 40, sun_visible=True, glow="#FFD27A",
    cloud="#75588C", cloud_lit="#FFB26A", cloud_op=.55,
    haze="#B27A7E", haze2="#86546C", bridge_back="#7A4C66", bridge="#2A1D33",
    glitter="#FFF3C4", ripple="#FFD9A0", refl=.42,
    stone=["#5C4A5C", "#7A6068", "#96766F", "#6C5560"], stone_edge="#FFC98A",
    sil="#1E1626", rim="#FFC27A", shade=.5, vignette=.42,
    cloth=["#17877C", "#F0E4CC", "#F2B02C", "#E2573E"],
    stars=False, lights=False, mist=0)

DUSK = dict(
    sky=[(0, "#0A1335"), (.42, "#232F6C"), (.72, "#6B4B8C"), (.9, "#D66E6B"), (1, "#F8AB68")],
    water=[(0, "#EE9869"), (.08, "#8A5788"), (.38, "#28306B"), (1, "#0A0F2E")],
    sun="#FFD9A0", sun_y=H + 6, sun_visible=False, glow="#FF9D66",
    cloud="#1E2460", cloud_lit="#C9647B", cloud_op=.6,
    haze="#3B3A76", haze2="#22255A", bridge_back="#1D2254", bridge="#080C24",
    glitter="#FFC98A", ripple="#8C9BE0", refl=.55,
    stone=["#1A1F47", "#232A57", "#2E3668", "#1D2450"], stone_edge="#8794E0",
    sil="#070A1C", rim="#FFB877", shade=.62, vignette=.5,
    cloth=["#17877C", "#F0E4CC", "#F2B02C", "#E2573E"],
    stars=True, lights=True, mist=0)

MORNING = dict(
    sky=[(0, "#6FA6D4"), (.45, "#B5D9EC"), (.8, "#FBE8C6"), (1, "#FFD8A0")],
    water=[(0, "#FCE4BA"), (.14, "#CDE1E4"), (.5, "#8DB6C6"), (1, "#3C6B82")],
    sun="#FFFDF2", sun_y=H - 92, sun_visible=True, glow="#FFF0C0",
    cloud="#FFFFFF", cloud_lit="#FFE6BE", cloud_op=.7,
    haze="#A9C6D6", haze2="#86AABD", bridge_back="#8FB0C2", bridge="#3F627B",
    glitter="#FFFFFF", ripple="#FFFFFF", refl=.3,
    stone=["#7F8C94", "#9BA6A9", "#BBBFB9", "#8D989D"], stone_edge="#FFF6DC",
    sil="#2A3F52", rim="#FFF4D6", shade=.22, vignette=.25,
    cloth=["#17877C", "#F6ECD8", "#F2B02C", "#E2573E"],
    stars=False, lights=False, mist=.55)

if __name__ == "__main__":
    looks = {"sunset": SUNSET, "dusk": DUSK, "morning": MORNING}
    look = sys.argv[1] if len(sys.argv) > 1 else "sunset"
    if look not in looks:
        sys.exit(f"Unknown look '{look}'. Use one of: {', '.join(looks)}")
    # SVG -> PNG (transparent outside the arch) -> WebP
    png = subprocess.run(["rsvg-convert", "-w", str(WIDTH)], input=scene(looks[look]).encode("utf-8"),
                         capture_output=True, check=True).stdout
    from PIL import Image
    out = ROOT / "img" / "hero-ghat.webp"
    Image.open(io.BytesIO(png)).save(out, "WEBP", quality=82, method=6)
    print(f"{out.relative_to(ROOT)}: {look}, {out.stat().st_size // 1024} KB")
