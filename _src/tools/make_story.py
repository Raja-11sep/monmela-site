# Paints the six pictures of the home page story ("A story of friendship"), in the same style
# and with the same four friends as the hero picture (make_hero.py):
#   Arjun  - teal kurta, short hair, jhola strap     Riya  - cream saree with a red border, bun
#   Nasrin - marigold kurti, braid                    Debu  - red-orange shirt, short hair
# Everyone is seen from behind, like in the hero picture: the scenes stay about the moment and
# the place, and nobody's face has to be drawn.
#
# Usage (from the site folder):  python3 _src/tools/make_story.py      → img/story-1.webp … story-6.webp
# Needs rsvg-convert and Pillow (same as make_hero.py). Then run _src/build.py.
import io
import pathlib
import random
import subprocess
import sys

TOOLS = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(TOOLS.parent))
import make_hero as hero  # noqa: E402  (people, lamps, the ghat scene)
from make_hero import back_sit, grad, mix  # noqa: E402

ROOT = TOOLS.parent.parent
W, H = 600, 720           # same canvas as the hero picture (shown at 5:6)
OUT_WIDTH = 1000

# The four friends: clothes, skin, hair (same as the hero picture)
ARJUN = dict(cloth="#17877C", skin="#A86B45", hair="short", strap="#D9A441")
RIYA = dict(cloth="#F0E4CC", skin="#C68A5E", hair="bun", saree="#B5301F")
NASRIN = dict(cloth="#F2B02C", skin="#B97A50", hair="braid", lower="#0F5F58")
DEBU = dict(cloth="#E2573E", skin="#C68A5E", hair="short", lower="#3A3F55")

FILTERS = ('<filter id="blur1"><feGaussianBlur stdDeviation="1.1"/></filter>'
           '<filter id="blur3"><feGaussianBlur stdDeviation="3"/></filter>'
           '<filter id="blur8" x="-30%" y="-80%" width="160%" height="260%"><feGaussianBlur stdDeviation="8"/></filter>'
           '<filter id="blur16" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="16"/></filter>')


def glow(gid, colour, peak=.9):
    return (f'<radialGradient id="{gid}"><stop offset="0" stop-color="{colour}" stop-opacity="{peak}"/>'
            f'<stop offset=".4" stop-color="{colour}" stop-opacity="{peak * .4:.2f}"/>'
            f'<stop offset="1" stop-color="{colour}" stop-opacity="0"/></radialGradient>')


def vignette(strength):
    return (f'<radialGradient id="vig" cx=".5" cy=".55" r=".75"><stop offset=".55" stop-color="#000" stop-opacity="0"/>'
            f'<stop offset="1" stop-color="#000" stop-opacity="{strength}"/></radialGradient>')


def sit(x, y, s, who, P, **kw):
    """One of the friends sitting, back to us."""
    args = dict(who)
    args.update(kw)
    cloth, skin = args.pop("cloth"), args.pop("skin")
    return back_sit(x, y, s, cloth, skin, P, **args)


def stand(x, y, s, who, P, **kw):
    """One of the friends standing, back to us; (x, y) = between the feet."""
    args = dict(who)
    args.update(kw)
    c = lambda col: mix(col, P["sil"], P["shade"])
    lower = args.get("lower") or args["cloth"]
    if args.get("saree"):      # saree: the pleats fall to the ankles
        legs = (f'<path d="M-24 -76C-26 -50 -22 -20 -19 -3H19C22 -20 26 -50 24 -76Z" fill="{c(args["cloth"])}"/>'
                f'<path d="M-19 -6H19" stroke="{c(args["saree"])}" stroke-width="5"/>'
                f'<path d="M-6 -70V-6M4 -70V-6" stroke="{P["sil"]}" stroke-width="1" opacity=".22"/>')
    else:
        legs = (f'<path d="M-17 -78L-15 -4H-3L-1 -70Z" fill="{c(lower)}"/><path d="M17 -78L15 -4H3L1 -70Z" fill="{c(lower)}"/>'
                f'<path d="M-1 -74V-6" stroke="{P["sil"]}" stroke-width="1.2" opacity=".3"/>')
    feet = f'<ellipse cx="-9" cy="-2" rx="8" ry="3.4" fill="{P["sil"]}"/><ellipse cx="9" cy="-2" rx="8" ry="3.4" fill="{P["sil"]}"/>'
    cloth, skin = args.pop("cloth"), args.pop("skin")
    upper = back_sit(0, -74, 1, cloth, skin, P, **args)
    return f'<g transform="translate({x} {y}) scale({s})">{legs}{feet}{upper}</g>'


def ground_shadow(x, y, rx, op=.35):
    return f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{rx * .16:.1f}" fill="#000" opacity="{op}" filter="url(#blur3)"/>'


def string_lights(points, rnd, colours=("#FFD98A", "#FFB86B", "#FFE9B8"), r=3.2, halo=11):
    """Bulbs on a wire through `points` (a smooth curve, 2 bulbs per segment)."""
    path = "M" + " ".join(f"{x} {y}" for x, y in points[:1]) + "".join(
        f"Q{(x0 + x1) / 2:.0f} {max(y0, y1) + 16:.0f} {x1} {y1}" for (x0, y0), (x1, y1) in zip(points, points[1:]))
    out = [f'<path d="{path}" stroke="#120E1A" stroke-width="1.4" fill="none" opacity=".8"/>']
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        for t in (.3, .7):
            bx = x0 + (x1 - x0) * t
            by = y0 + (y1 - y0) * t + 16 * 4 * t * (1 - t) * .9
            col = rnd.choice(colours)
            out.append(f'<circle cx="{bx:.0f}" cy="{by + 4:.0f}" r="{halo}" fill="{col}" opacity=".22" filter="url(#blur3)"/>'
                       f'<circle cx="{bx:.0f}" cy="{by + 4:.0f}" r="{r}" fill="{col}"/>')
    return "".join(out)


def svg(defs, body, vig=.45):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {H}">'
            f'<defs>{FILTERS}{vignette(vig)}{defs}</defs>{body}<rect width="{W}" height="{H}" fill="url(#vig)"/></svg>')


def skyline(rnd, y_base, colour, lit, count_lit=.3, hmin=60, hmax=210, x0=-10, x1=610):
    """Rows of city blocks with a few lit windows."""
    out, x = [], x0
    while x < x1:
        w = rnd.uniform(26, 70)
        h = rnd.uniform(hmin, hmax)
        out.append(f'<rect x="{x:.0f}" y="{y_base - h:.0f}" width="{w:.0f}" height="{h + 4:.0f}" fill="{colour}"/>')
        if rnd.random() < .25:   # water tank or antenna on the roof
            out.append(f'<rect x="{x + w * .3:.0f}" y="{y_base - h - 10:.0f}" width="{w * .25:.0f}" height="10" fill="{colour}"/>')
        for wy in range(int(y_base - h + 10), int(y_base - 8), 14):
            for wx in range(int(x + 6), int(x + w - 8), 11):
                if rnd.random() < count_lit:
                    out.append(f'<rect x="{wx}" y="{wy}" width="5" height="7" fill="{lit}" opacity="{rnd.uniform(.55, 1):.2f}"/>')
        x += w + rnd.uniform(1, 6)
    return "".join(out)


# ---------------------------------------------------------------- 1. a new city (night, alone)
def new_city():
    rnd = random.Random(21)
    P = dict(sil="#05071A", rim="#8FA8FF", shade=.62)
    defs = (grad("sky1", [(0, "#070D33"), (.55, "#1E2766"), (.85, "#4B3C7E"), (1, "#7A4E86")])
            + grad("wall1", [(0, "#131736"), (1, "#0A0C22")])
            + glow("moon", "#DCE4FF", .6) + glow("phone", "#9AD8FF", .55) + glow("lampoff", "#FFD58A", .35))
    b = f'<rect width="{W}" height="{H}" fill="url(#wall1)"/>'
    # the window: night sky, moon, the city
    win = f'<rect x="70" y="70" width="460" height="470" fill="url(#sky1)"/>'
    win += "".join(f'<circle cx="{rnd.uniform(80, 520):.0f}" cy="{rnd.uniform(80, 300):.0f}" r="{rnd.uniform(.6, 1.4):.1f}" '
                   f'fill="#fff" opacity="{rnd.uniform(.3, .9):.2f}"/>' for _ in range(40))
    win += '<circle cx="430" cy="150" r="60" fill="url(#moon)"/><circle cx="430" cy="150" r="17" fill="#EEF1FF"/>'
    win += skyline(rnd, 470, "#232A63", "#7F8BD8", .12, 90, 230)            # far towers, cool
    win += skyline(rnd, 540, "#141945", "#FFD58A", .28, 40, 150)            # near blocks, warm windows
    # the flyover and its traffic
    win += '<path d="M70 470Q300 452 530 466" stroke="#0E1236" stroke-width="10" fill="none"/>'
    win += "".join(f'<circle cx="{70 + i * 23 + rnd.uniform(-4, 4):.0f}" cy="{468 - 8 * __import__("math").sin(i / 3):.0f}" '
                   f'r="1.8" fill="{rnd.choice(["#FFE6A6", "#FF7A6A"])}"/>' for i in range(20))
    b += f'<clipPath id="pane"><rect x="70" y="70" width="460" height="470"/></clipPath><g clip-path="url(#pane)">{win}</g>'
    # window frame and bars
    fr = "#0B0D26"
    b += (f'<path d="M62 62H538V548H62Z M78 78V532H522V78Z" fill="{fr}" fill-rule="evenodd"/>'
          f'<rect x="294" y="70" width="12" height="470" fill="{fr}"/><rect x="70" y="300" width="460" height="10" fill="{fr}"/>')
    b += "".join(f'<rect x="{x}" y="78" width="3" height="454" fill="{fr}" opacity=".85"/>' for x in (184, 412))
    b += '<path d="M78 300H522" stroke="#8FA8FF" stroke-width="1" opacity=".25"/>'
    # the sill, a cup, a sleeping lamp
    b += (f'<rect x="40" y="540" width="520" height="22" fill="#1C1E42"/><rect x="40" y="540" width="520" height="2.5" fill="#8FA8FF" opacity=".45"/>'
          f'<rect x="0" y="562" width="{W}" height="{H - 562}" fill="#0B0C22"/>')
    b += ('<path d="M452 520l3 20h18l3 -20Z" fill="#5B4B66"/><ellipse cx="464" cy="520" rx="12" ry="3" fill="#7B6A86"/>'
          '<path d="M460 512q-6 -10 2 -18q6 -8 -1 -16" stroke="#C9D3FF" stroke-width="1.6" fill="none" opacity=".35"/>')
    b += ('<circle cx="120" cy="470" r="60" fill="url(#lampoff)"/><path d="M104 538h32l-6 -8h-20Z" fill="#26213A"/>'
          '<rect x="118" y="470" width="4" height="62" fill="#26213A"/><path d="M98 478l10 -30h24l10 30Z" fill="#3A3150"/>')
    # Arjun at the window, the phone's glow in his lap
    b += ground_shadow(300, 712, 140, .5)
    b += '<circle cx="300" cy="650" r="140" fill="url(#phone)"/>'
    b += sit(300, 712, 2.45, ARJUN, P, arm="down", tilt=2)
    return svg(defs, b, .55)


# ---------------------------------------------------------------- 2. a hello (the phone on the sill)
def hand_wave(cx, cy, s, fill="#F5B023", line="#B97E0C"):
    """The 👋 hand, drawn (an emoji font can't be relied on in the renderer)."""
    fingers = "".join(f'<rect x="{x}" y="{y}" width="11" height="{h}" rx="5.5" transform="rotate({a} {x + 5} {y + h})" '
                      f'fill="{fill}" stroke="{line}" stroke-width="1.6"/>'
                      for x, y, h, a in ((-20, -46, 36, -14), (-8, -52, 40, -5), (4, -50, 38, 4), (15, -42, 32, 13)))
    return (f'<g transform="translate({cx} {cy}) rotate(-18) scale({s})">{fingers}'
            f'<path d="M-22 -16C-24 6 -14 24 4 25C20 25 28 14 27 -4L25 -18Z" fill="{fill}" stroke="{line}" stroke-width="1.6"/>'
            f'<path d="M24 -8C32 -16 40 -20 44 -14C47 -9 38 -2 28 8" fill="{fill}" stroke="{line}" stroke-width="1.6"/>'
            f'<path d="M-36 -40q-8 10 -6 22M-46 -46q-12 16 -9 32M40 -56q10 4 14 14M48 -66q14 6 18 22" stroke="{fill}" '
            f'stroke-width="3" fill="none" stroke-linecap="round" opacity=".85"/></g>')


def a_hello():
    rnd = random.Random(5)
    defs = (grad("bg2", [(0, "#0E1440"), (.6, "#2A2468"), (1, "#3E2A5E")])
            + glow("screen", "#BFF1E8", .55) + glow("bok", "#FFD58A", .8))
    b = f'<rect width="{W}" height="{H}" fill="url(#bg2)"/>'
    # the city behind, out of focus: soft lights
    for _ in range(46):
        col = rnd.choice(["#FFD58A", "#FFB86B", "#8FA8FF", "#FFE9B8", "#FF8A6A"])
        r = rnd.uniform(8, 30)
        b += f'<circle cx="{rnd.uniform(0, W):.0f}" cy="{rnd.uniform(40, 470):.0f}" r="{r:.0f}" fill="{col}" opacity="{rnd.uniform(.12, .38):.2f}" filter="url(#blur3)"/>'
    b += '<rect y="520" width="600" height="200" fill="#120F2C"/><rect y="520" width="600" height="3" fill="#8FA8FF" opacity=".35"/>'
    # the phone standing on the sill, slightly turned
    ph = '<g transform="translate(300 330) rotate(-5)">'
    ph += '<circle cx="0" cy="40" r="260" fill="url(#screen)"/>'
    ph += '<rect x="-112" y="-200" width="224" height="440" rx="34" fill="#0F1E1C"/><rect x="-104" y="-192" width="208" height="424" rx="27" fill="#FFFBF3"/>'
    ph += '<rect x="-104" y="-192" width="208" height="58" rx="27" fill="#0F766E"/><rect x="-104" y="-160" width="208" height="26" fill="#0F766E"/>'
    ph += '<rect x="-84" y="-172" width="70" height="11" rx="5.5" fill="#FFF6E5" opacity=".9"/><circle cx="76" cy="-166" r="7" fill="#FFF6E5" opacity=".8"/>'
    # a suggestion card: photo (soft shapes), match chip, shared answers
    ph += '<rect x="-88" y="-118" width="176" height="200" rx="18" fill="#DCEDE8"/>'
    ph += '<rect x="-88" y="-118" width="176" height="150" rx="18" fill="#9CC9C0"/><rect x="-88" y="2" width="176" height="30" fill="#9CC9C0"/>'
    ph += '<circle cx="-12" cy="-58" r="26" fill="#6E9F98"/><path d="M-62 32C-58 -6 -36 -20 -12 -20C14 -20 36 -6 40 32Z" fill="#6E9F98"/>'
    ph += '<rect x="22" y="-108" width="56" height="20" rx="10" fill="#F5B023"/>'
    ph += '<rect x="-76" y="44" width="62" height="16" rx="8" fill="#FFFBF3"/><rect x="-8" y="44" width="50" height="16" rx="8" fill="#FFFBF3"/>'
    ph += '<rect x="-76" y="66" width="80" height="16" rx="8" fill="#FFFBF3"/>'
    # the wave button, and the reply coming in
    ph += '<circle cx="0" cy="150" r="44" fill="#FFF1CC" stroke="#F5B023" stroke-width="3"/>' + hand_wave(2, 166, .78)
    ph += '<rect x="-96" y="206" width="192" height="24" rx="12" fill="#0F766E" opacity=".12"/>'
    ph += '</g>'
    b += ph
    # a bhaar of cha beside it
    b += ('<path d="M452 498l4 28h28l4 -28Z" fill="#A9583A"/><ellipse cx="470" cy="498" rx="18" ry="4.5" fill="#C9744E"/>'
          '<ellipse cx="470" cy="499" rx="14" ry="3" fill="#6B3A22"/>'
          '<path d="M466 488q-7 -12 2 -22q7 -9 -1 -20" stroke="#FFF3E0" stroke-width="2" fill="none" opacity=".35"/>')
    b += '<ellipse cx="300" cy="578" rx="150" ry="14" fill="#000" opacity=".35" filter="url(#blur3)"/>'
    return svg(defs, b, .5)


# ---------------------------------------------------------------- 3. the first adda (para tea stall, blue hour)
def first_adda():
    rnd = random.Random(8)
    P = dict(sil="#160F1C", rim="#FFC27A", shade=.55)
    defs = (grad("sky3", [(0, "#1D2E63"), (.5, "#5A4E86"), (.85, "#C9786E"), (1, "#F0A070")])
            + grad("road3", [(0, "#2A2234"), (1, "#120D18")])
            + glow("bulb", "#FFD27A", .95) + glow("warm", "#FFB45A", .5))
    b = f'<rect width="{W}" height="{H}" fill="url(#sky3)"/>'
    # old para houses on both sides, with balconies and tram wires
    b += skyline(rnd, 420, "#3A3466", "#FFD58A", .18, 120, 260)
    b += '<path d="M0 120Q300 150 600 112M0 140Q300 172 600 132" stroke="#120E1A" stroke-width="1.4" fill="none" opacity=".7"/>'
    # the stall: tin roof, wooden back, shelves of jars, kettle on the clay oven
    b += '<rect x="96" y="238" width="408" height="330" fill="#3B2419"/>'
    b += '<path d="M70 236L530 236L506 206L94 206Z" fill="#6E6A7A"/>'
    b += "".join(f'<path d="M{x} 236L{x + 6} 206" stroke="#4A4656" stroke-width="2"/>' for x in range(86, 520, 14))
    b += '<rect x="70" y="236" width="460" height="7" fill="#3E3A48"/>'
    b += '<circle cx="300" cy="300" r="190" fill="url(#warm)"/>'
    for sy in (300, 352):   # shelves with glass jars of biscuits
        b += f'<rect x="120" y="{sy}" width="360" height="5" fill="#5E3A26"/>'
        x = 132
        while x < 466:
            w = rnd.uniform(20, 30)
            col = rnd.choice(["#E7B860", "#D98B4A", "#F1D9A0", "#C46A4A", "#E9C27A"])
            b += (f'<rect x="{x:.0f}" y="{sy - 30}" width="{w:.0f}" height="30" rx="4" fill="#CFE6E4" opacity=".5"/>'
                  f'<rect x="{x + 3:.0f}" y="{sy - 20}" width="{w - 6:.0f}" height="18" rx="3" fill="{col}"/>'
                  f'<rect x="{x - 1:.0f}" y="{sy - 34}" width="{w + 2:.0f}" height="6" rx="2" fill="#B53E2A"/>')
            x += w + rnd.uniform(4, 9)
    b += '<path d="M300 243V272" stroke="#1A1218" stroke-width="2"/><circle cx="300" cy="282" r="70" fill="url(#bulb)"/><circle cx="300" cy="280" r="8" fill="#FFF2C6"/>'
    # the stall-keeper behind the counter, against the light
    b += '<g fill="#22161E"><circle cx="410" cy="386" r="17"/><path d="M380 470C380 420 392 404 410 404C428 404 440 420 440 470Z"/></g>'
    b += '<path d="M396 378a17 17 0 0 1 28 0" stroke="#FFC27A" stroke-width="2" fill="none" opacity=".7"/>'
    # the clay oven and the kettle, steaming
    b += ('<path d="M150 470l8 -46h60l8 46Z" fill="#8A4A2C"/><path d="M170 424q18 -14 36 0" fill="#2A1A14"/>'
          '<path d="M168 410q4 -26 28 -26q24 0 28 26Z" fill="#B9B7C4"/><path d="M224 398l22 -12" stroke="#B9B7C4" stroke-width="5" stroke-linecap="round"/>'
          '<path d="M186 380q-10 -20 4 -36q12 -16 -2 -34M204 378q-8 -18 4 -30" stroke="#FFF3E0" stroke-width="3" fill="none" opacity=".35" filter="url(#blur1)"/>')
    # the counter front
    b += '<rect x="96" y="470" width="408" height="98" fill="#5A3622"/>'
    b += "".join(f'<path d="M96 {y}H504" stroke="#3B2419" stroke-width="2"/>' for y in (494, 518, 542))
    b += '<rect x="96" y="470" width="408" height="5" fill="#FFC27A" opacity=".55"/>'
    # string lights along the roof edge
    b += string_lights([(78, 246), (190, 248), (300, 250), (410, 248), (522, 246)], rnd)
    # the road, warm light spilling on it
    b += '<rect y="568" width="600" height="152" fill="url(#road3)"/><ellipse cx="300" cy="580" rx="260" ry="34" fill="#FFB45A" opacity=".18" filter="url(#blur8)"/>'
    # the bench and three friends on it, bhaar cups between them
    b += '<rect x="120" y="652" width="360" height="12" rx="3" fill="#4A2E1E"/><rect x="140" y="664" width="10" height="56" fill="#2E1C12"/><rect x="450" y="664" width="10" height="56" fill="#2E1C12"/>'
    b += ground_shadow(300, 714, 190, .45)
    b += sit(206, 652, 1.3, ARJUN, P, tilt=3)
    b += sit(300, 654, 1.27, RIYA, P, tilt=-2)
    b += sit(394, 652, 1.3, DEBU, P, tilt=-3)
    for cx in (253, 347):
        b += f'<path d="M{cx - 6} 640l2 12h8l2 -12Z" fill="#8A4A2C"/><ellipse cx="{cx}" cy="640" rx="6" ry="1.8" fill="#C9744E"/>'
    return svg(defs, b, .45)


# ---------------------------------------------------------------- 4. Boi Mela (winter afternoon, golden haze)
def boi_mela():
    rnd = random.Random(13)
    P = dict(sil="#3A2418", rim="#FFE2A8", shade=.32)
    defs = (grad("sky4", [(0, "#F2C98A"), (.6, "#F6DDAE"), (1, "#E9C08A")]) + grad("ground4", [(0, "#D6AE7A"), (1, "#B98D5E")])
            + glow("sun4", "#FFF4D6", .9))
    b = f'<rect width="{W}" height="{H}" fill="url(#sky4)"/><circle cx="470" cy="160" r="170" fill="url(#sun4)"/>'
    # hazy trees on the Maidan, and the fair's big gate with its banner and flags
    for tx, ty, tr in ((40, 300, 70), (110, 280, 58), (560, 300, 66), (500, 320, 50)):
        b += f'<circle cx="{tx}" cy="{ty}" r="{tr}" fill="#C9A06E" opacity=".45" filter="url(#blur3)"/>'
    gate = ('<g opacity=".72">'
            '<rect x="150" y="150" width="26" height="220" fill="#B5301F"/><rect x="304" y="150" width="26" height="220" fill="#B5301F"/>'
            '<path d="M140 156Q240 70 340 156V176Q240 96 140 176Z" fill="#D9A441"/>'
            '<rect x="176" y="182" width="128" height="40" rx="6" fill="#F0E4CC"/>'
            '<rect x="190" y="194" width="100" height="6" rx="3" fill="#B5301F" opacity=".7"/><rect x="206" y="206" width="68" height="5" rx="2.5" fill="#17877C" opacity=".7"/>'
            '<path d="M140 156L132 140M340 156L348 140M240 92V70" stroke="#6A4A34" stroke-width="2"/>'
            '<path d="M240 70l16 6l-16 6Z" fill="#17877C"/><path d="M132 140l-12 4l12 4Z" fill="#F2B02C"/><path d="M348 140l12 4l-12 4Z" fill="#F2B02C"/>'
            + "".join(f'<circle cx="{x}" cy="{y}" r="2.4" fill="#FFF1C4"/>' for x, y in ((160, 150), (190, 126), (220, 112), (260, 112), (290, 126), (320, 150)))
            + '</g>')
    b += gate
    for kx, ky, ka, col in ((420, 110, 12, "#17877C"), (520, 70, -10, "#E2573E")):   # winter kites over the Maidan
        b += (f'<g transform="translate({kx} {ky}) rotate({ka}) scale(.32)" opacity=".8"><path d="M0 -44L-34 0L0 44Z" fill="{col}"/>'
              f'<path d="M0 -44L34 0L0 44Z" fill="#F0E4CC"/></g>'
              f'<path d="M{kx} {ky + 14}Q{kx - 30} {ky + 120} {kx - 90} {ky + 260}" stroke="#6A4A34" stroke-width=".7" fill="none" opacity=".5"/>')
    # rows of stalls fading into the dust, bunting between them
    for row, (y, s, op) in enumerate(((360, .55, .45), (420, .8, .7))):
        x = -30 + row * 20
        while x < 640:
            col = rnd.choice(["#C9785A", "#4E8C86", "#D9A441", "#7A5C8E", "#B5301F", "#2F6F8C"])
            w = 90 * s
            b += (f'<g opacity="{op}"><path d="M{x} {y}l{w / 2:.0f} {-34 * s:.0f}l{w / 2:.0f} {34 * s:.0f}Z" fill="{col}"/>'
                  f'<rect x="{x + 4}" y="{y}" width="{w - 8:.0f}" height="{56 * s:.0f}" fill="{mix(col, "#FFFFFF", .35)}"/>'
                  f'<rect x="{x + 12}" y="{y + 18 * s:.0f}" width="{w - 24:.0f}" height="{30 * s:.0f}" fill="{mix(col, "#3A2418", .3)}"/></g>')
            x += w + rnd.uniform(6, 18)
    for y0 in (300, 336):
        pts = [(x, y0 + (x % 120) * .05) for x in range(-20, 640, 110)]
        for (x0, ya), (x1, yb) in zip(pts, pts[1:]):
            b += f'<path d="M{x0} {ya}Q{(x0 + x1) / 2} {ya + 14} {x1} {yb}" stroke="#6A4A34" stroke-width="1" fill="none" opacity=".6"/>'
            for t in (.2, .4, .6, .8):
                fx = x0 + (x1 - x0) * t
                fy = ya + (yb - ya) * t + 14 * 4 * t * (1 - t) * .5
                col = rnd.choice(["#B5301F", "#F2B02C", "#17877C", "#F0E4CC", "#2F6F8C"])
                b += f'<path d="M{fx - 6:.0f} {fy:.0f}h12l-6 12Z" fill="{col}" opacity=".9"/>'
    # the crowd far off, soft in the haze
    for _ in range(26):
        x = rnd.uniform(0, 600)
        h = rnd.uniform(46, 62)
        b += (f'<g fill="#9B7552" opacity="{rnd.uniform(.35, .6):.2f}"><circle cx="{x:.0f}" cy="{470 - h:.0f}" r="6"/>'
              f'<rect x="{x - 8:.0f}" y="{476 - h:.0f}" width="16" height="{h - 8:.0f}" rx="6"/></g>')
    b += '<rect y="470" width="600" height="250" fill="url(#ground4)"/>'
    # the near stall: a striped awning and tables of books
    b += '<path d="M330 448L600 448L600 392L360 392Z" fill="#17877C"/>'
    b += "".join(f'<path d="M{x} 448L{x + 6} 392" stroke="#F0E4CC" stroke-width="10" opacity=".9"/>' for x in range(372, 600, 34))
    b += '<rect x="340" y="448" width="260" height="10" fill="#0F5F58"/><rect x="350" y="458" width="10" height="120" fill="#5A3622"/>'
    x = 360
    while x < 598:   # stacks of books on the table
        y = 528
        for _ in range(rnd.randint(2, 5)):
            w = rnd.uniform(26, 40)
            col = rnd.choice(["#B5301F", "#2F6F8C", "#F2B02C", "#4E8C86", "#7A5C8E", "#F0E4CC", "#2A1D33"])
            b += f'<rect x="{x:.0f}" y="{y - 9:.0f}" width="{w:.0f}" height="9" fill="{col}"/><rect x="{x:.0f}" y="{y - 9:.0f}" width="{w:.0f}" height="1.6" fill="#FFFFFF" opacity=".35"/>'
            y -= 9
        x += rnd.uniform(34, 44)
    b += '<rect x="352" y="528" width="248" height="12" fill="#6B4A30"/><rect x="352" y="540" width="248" height="40" fill="#F0E4CC" opacity=".85"/>'
    # dust in the low sun
    b += "".join(f'<circle cx="{rnd.uniform(0, 600):.0f}" cy="{rnd.uniform(120, 620):.0f}" r="{rnd.uniform(.8, 2.2):.1f}" fill="#FFF6DC" '
                 f'opacity="{rnd.uniform(.3, .8):.2f}"/>' for _ in range(70))
    # the four friends at the stall, books in hand
    b += ground_shadow(300, 712, 210, .25)
    b += stand(150, 714, 1.16, NASRIN, P, tilt=2)
    b += stand(236, 716, 1.18, ARJUN, P, tilt=-1)
    b += stand(326, 714, 1.14, RIYA, P, tilt=1)
    b += stand(414, 716, 1.2, DEBU, P, arm="point", tilt=-2)
    b += '<g transform="translate(196 590) rotate(-8)"><rect width="18" height="26" fill="#B5301F"/><rect x="3" y="3" width="18" height="26" fill="#2F6F8C"/></g>'
    return svg(defs, b, .3)


# ---------------------------------------------------------------- 5. a night at the mela
def mela_night():
    import math
    rnd = random.Random(17)
    P = dict(sil="#08081C", rim="#FFB877", shade=.6)
    defs = (grad("sky5", [(0, "#070C2E"), (.55, "#1E2163"), (.85, "#5A3478"), (1, "#8C3F72")])
            + grad("ground5", [(0, "#2A1A33"), (1, "#0D0A18")]) + glow("wheel", "#FFB45A", .45) + glow("stallg", "#FFD27A", .7))
    b = f'<rect width="{W}" height="{H}" fill="url(#sky5)"/>'
    b += "".join(f'<circle cx="{rnd.uniform(0, 600):.0f}" cy="{rnd.uniform(20, 260):.0f}" r="{rnd.uniform(.6, 1.5):.1f}" fill="#fff" '
                 f'opacity="{rnd.uniform(.3, .9):.2f}"/>' for _ in range(50))
    # the nagordola (giant wheel), lit
    cx, cy, R = 330, 300, 178
    b += f'<circle cx="{cx}" cy="{cy}" r="{R + 90}" fill="url(#wheel)"/>'
    b += f'<path d="M{cx} {cy}L{cx - 120} 600M{cx} {cy}L{cx + 120} 600" stroke="#2A2148" stroke-width="10"/>'
    b += f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="#3A2E5E" stroke-width="5"/><circle cx="{cx}" cy="{cy}" r="{R - 14}" fill="none" stroke="#3A2E5E" stroke-width="2"/>'
    for i in range(16):
        a = i * math.pi / 8
        x, y = cx + R * math.cos(a), cy + R * math.sin(a)
        b += f'<path d="M{cx} {cy}L{x:.0f} {y:.0f}" stroke="#3A2E5E" stroke-width="1.6"/>'
        col = ["#E2573E", "#F2B02C", "#17877C", "#F0E4CC"][i % 4]
        b += (f'<path d="M{x:.0f} {y:.0f}v8" stroke="#3A2E5E" stroke-width="2"/>'
              f'<path d="M{x - 13:.0f} {y + 8:.0f}h26l-4 18h-18Z" fill="{col}"/><rect x="{x - 15:.0f}" y="{y + 6:.0f}" width="30" height="4" rx="2" fill="{mix(col, "#000000", .3)}"/>')
    for i in range(48):
        a = i * math.pi / 24
        x, y = cx + R * math.cos(a), cy + R * math.sin(a)
        b += f'<circle cx="{x:.0f}" cy="{y:.0f}" r="2.6" fill="{["#FFE29A", "#FF9A6A", "#9AF0E0"][i % 3]}"/>'
    b += f'<circle cx="{cx}" cy="{cy}" r="16" fill="#F2B02C"/><circle cx="{cx}" cy="{cy}" r="7" fill="#FFE9B8"/>'
    # stalls glowing along the bottom
    b += f'<rect y="560" width="600" height="160" fill="url(#ground5)"/>'
    x = -10
    while x < 610:
        w = rnd.uniform(70, 110)
        col = rnd.choice(["#B5301F", "#17877C", "#7A3C8E", "#D9A441"])
        b += (f'<circle cx="{x + w / 2:.0f}" cy="560" r="{w * .8:.0f}" fill="url(#stallg)" opacity=".55"/>'
              f'<path d="M{x:.0f} 520h{w:.0f}l-8 -22h{-w + 16:.0f}Z" fill="{col}"/>'
              f'<rect x="{x + 6:.0f}" y="520" width="{w - 12:.0f}" height="52" fill="#3A2440"/>'
              f'<rect x="{x + 10:.0f}" y="528" width="{w - 20:.0f}" height="26" fill="#FFD27A" opacity=".75"/>')
        x += w + rnd.uniform(4, 14)
    # balloon seller on the right
    bx, by = 520, 600
    for i in range(9):
        ex, ey = bx + rnd.uniform(-34, 34), by - 150 + rnd.uniform(-34, 30)
        col = rnd.choice(["#E2573E", "#F2B02C", "#17877C", "#F0E4CC", "#9A5CC8", "#3FA0D8"])
        b += f'<path d="M{bx} {by - 60}L{ex:.0f} {ey + 18:.0f}" stroke="#D8CFE8" stroke-width=".8" opacity=".6"/><ellipse cx="{ex:.0f}" cy="{ey:.0f}" rx="13" ry="16" fill="{col}"/>'
    b += f'<g fill="#120E22"><circle cx="{bx}" cy="{by - 52}" r="8"/><rect x="{bx - 10}" y="{by - 44}" width="20" height="54" rx="7"/></g>'
    # the crowd between
    for _ in range(22):
        x = rnd.uniform(0, 600)
        h = rnd.uniform(58, 76)
        b += f'<g fill="#140F26"><circle cx="{x:.0f}" cy="{628 - h:.0f}" r="8"/><rect x="{x - 10:.0f}" y="{636 - h:.0f}" width="20" height="{h - 8:.0f}" rx="8"/></g>'
    # lights strung across the top
    b += string_lights([(-20, 40), (120, 56), (260, 48), (400, 60), (540, 44), (640, 58)], rnd, r=3.6, halo=13)
    # the four friends in front, looking up at the wheel
    b += ground_shadow(300, 714, 220, .4)
    b += stand(160, 716, 1.24, RIYA, P, tilt=-2)
    b += stand(252, 718, 1.26, ARJUN, P, tilt=1)
    b += stand(344, 716, 1.22, NASRIN, P, tilt=-1)
    b += stand(436, 718, 1.28, DEBU, P, arm="point", tilt=3)
    return svg(defs, b, .5)


# ---------------------------------------------------------------- 6. evenings at the ghat (the hero picture, full frame)
def ghat():
    s = hero.scene(hero.SUNSET)
    # The hero version is cut to an arch with a frame; here it fills the whole frame.
    s = s.replace('<g clip-path="url(#window)">', "<g>", 1)
    return s.split(f'<path d="{hero.ARCH}"')[0] + "</svg>"


SCENES = [new_city, a_hello, first_adda, boi_mela, mela_night, ghat]

if __name__ == "__main__":
    from PIL import Image
    only = {int(a) for a in sys.argv[1:]} or set(range(1, 7))
    for n, make in enumerate(SCENES, 1):
        if n not in only:
            continue
        png = subprocess.run(["rsvg-convert", "-w", str(OUT_WIDTH)], input=make().encode("utf-8"),
                             capture_output=True, check=True).stdout
        out = ROOT / "img" / f"story-{n}.webp"
        Image.open(io.BytesIO(png)).convert("RGB").save(out, "WEBP", quality=80, method=6)
        print(f"{out.relative_to(ROOT)}: {out.stat().st_size // 1024} KB")
