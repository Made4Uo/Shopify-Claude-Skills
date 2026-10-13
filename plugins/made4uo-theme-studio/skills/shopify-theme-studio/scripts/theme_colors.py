#!/usr/bin/env python3
"""Color helper for storefront themes. Colors may be #rgb, #rrggbb or rgb()/rgba() strings.
  contrast C1 C2 ...                 WCAG ratio for every pair, with a verdict
  fix FG BG [GOAL]                   shift FG toward black/white until it reaches GOAL (default 4.5)
  tint HEX AMOUNT                    mix HEX toward white (0-1), e.g. derive a light neutral
  describe C1 C2 ...                 lightness / saturation / hue family of each color, in words
  compare --ours C... --vs NAME C... [--vs NAME C...]
                                     how close our colors sit to each competitor's (CIEDE2000)
  image FILE [N]                     the N most common colors in a screenshot (estimates)
  offpalette --palette C... --found C...
                                     which rendered colors don't belong to the palette (dE00 > 5 from every
                                     palette color and from pure black and white)
"""
import itertools, math, re, sys

# ---------- parsing ----------
def _rgb(c):
    c = c.strip()
    m = re.match(r'rgba?\(\s*([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)', c)
    if m:
        return [round(float(v)) for v in m.groups()]
    h = c.lstrip('#')
    if len(h) == 3:
        h = ''.join(ch * 2 for ch in h)
    return [int(h[i:i + 2], 16) for i in (0, 2, 4)]

def hexify(c):
    return '#' + ''.join(f'{v:02x}' for v in _rgb(c))

# ---------- WCAG contrast ----------
def _lin_wcag(c):
    c /= 255
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

def lum(c):
    r, g, b = _rgb(c)
    return 0.2126 * _lin_wcag(r) + 0.7152 * _lin_wcag(g) + 0.0722 * _lin_wcag(b)

def ratio(a, b):
    hi, lo = sorted((lum(a), lum(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)

def mix(c, target, t):
    a, b = _rgb(c), _rgb(target)
    return '#' + ''.join(f"{round(x * (1 - t) + y * t):02x}" for x, y in zip(a, b))

def fix(fg, bg, goal=4.5):
    toward = '#000000' if lum(fg) <= lum(bg) else '#ffffff'
    for step in range(101):
        c = mix(fg, toward, step / 100)
        if ratio(c, bg) >= goal:
            return c
    return None

def verdict(r):
    return 'AA body text' if r >= 4.5 else 'large text / UI only' if r >= 3 else 'decorative only'

# ---------- CIELAB / CIEDE2000 ----------
def lab(c):
    def lin(v):
        v /= 255
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(v) for v in _rgb(c))
    x = (0.4124564 * r + 0.3575761 * g + 0.1804375 * b) / 0.95047
    y = 0.2126729 * r + 0.7151522 * g + 0.0721750 * b
    z = (0.0193339 * r + 0.1191920 * g + 0.9503041 * b) / 1.08883
    f = lambda t: t ** (1 / 3) if t > (6 / 29) ** 3 else t / (3 * (6 / 29) ** 2) + 4 / 29
    return 116 * f(y) - 16, 500 * (f(x) - f(y)), 200 * (f(y) - f(z))

def lch(c):
    L, a, b = lab(c)
    return L, math.hypot(a, b), math.degrees(math.atan2(b, a)) % 360

def de2000(lab1, lab2):
    L1, a1, b1 = lab1
    L2, a2, b2 = lab2
    cbar = (math.hypot(a1, b1) + math.hypot(a2, b2)) / 2
    g = 0.5 * (1 - math.sqrt(cbar ** 7 / (cbar ** 7 + 25 ** 7)))
    a1p, a2p = (1 + g) * a1, (1 + g) * a2
    c1p, c2p = math.hypot(a1p, b1), math.hypot(a2p, b2)
    h1p = math.degrees(math.atan2(b1, a1p)) % 360 if (a1p or b1) else 0.0
    h2p = math.degrees(math.atan2(b2, a2p)) % 360 if (a2p or b2) else 0.0
    dlp, dcp = L2 - L1, c2p - c1p
    if c1p * c2p == 0:
        dhp = 0.0
    else:
        dhp = h2p - h1p
        if dhp > 180:
            dhp -= 360
        elif dhp < -180:
            dhp += 360
    dHp = 2 * math.sqrt(c1p * c2p) * math.sin(math.radians(dhp / 2))
    lbar, cbarp = (L1 + L2) / 2, (c1p + c2p) / 2
    if c1p * c2p == 0:
        hbar = h1p + h2p
    elif abs(h1p - h2p) <= 180:
        hbar = (h1p + h2p) / 2
    elif h1p + h2p < 360:
        hbar = (h1p + h2p + 360) / 2
    else:
        hbar = (h1p + h2p - 360) / 2
    t = (1 - 0.17 * math.cos(math.radians(hbar - 30)) + 0.24 * math.cos(math.radians(2 * hbar))
         + 0.32 * math.cos(math.radians(3 * hbar + 6)) - 0.20 * math.cos(math.radians(4 * hbar - 63)))
    dtheta = 30 * math.exp(-(((hbar - 275) / 25) ** 2))
    rc = 2 * math.sqrt(cbarp ** 7 / (cbarp ** 7 + 25 ** 7))
    sl = 1 + 0.015 * (lbar - 50) ** 2 / math.sqrt(20 + (lbar - 50) ** 2)
    sc = 1 + 0.045 * cbarp
    sh = 1 + 0.015 * cbarp * t
    rt = -math.sin(math.radians(2 * dtheta)) * rc
    return math.sqrt((dlp / sl) ** 2 + (dcp / sc) ** 2 + (dHp / sh) ** 2 + rt * (dcp / sc) * (dHp / sh))

def distance(c1, c2):
    return de2000(lab(c1), lab(c2))

# ---------- words ----------
_HUES = [(30, 'pink/rose'), (55, 'red/terracotta'), (80, 'orange/amber'), (110, 'yellow/mustard'),
         (165, 'green'), (235, 'teal/cyan'), (315, 'blue'), (345, 'purple/plum'), (361, 'pink/rose')]

def is_neutral(c):
    return lch(c)[1] < 10

def describe(c):
    L, C, h = lch(c)
    light = ('very dark' if L < 25 else 'dark' if L < 45 else 'mid' if L < 65
             else 'light' if L < 85 else 'very light')
    if C < 10:
        _, a, b = lab(c)
        tone = 'warm ' if b > 3 else 'cool ' if b < -3 else ''
        return f"{light} {tone}neutral"
    sat = 'muted' if C < 25 else 'moderate' if C < 50 else 'vivid'
    family = next(name for limit, name in _HUES if h < limit)
    if family == 'pink/rose' and L < 45:
        family = 'wine/burgundy'
    return f"{light} {sat} {family}"

def label(d):
    return ('same color' if d < 5 else 'same family' if d < 10 else 'related' if d < 20 else 'distinct')

# ---------- commands ----------
def cmd_compare(args):
    ours, rivals, cur = [], {}, None
    it = iter(args)
    for tok in it:
        if tok == '--ours':
            cur = ours
        elif tok == '--vs':
            name = next(it)
            rivals[name] = cur = []
        else:
            cur.append(hexify(tok))
    print("Neutrals (backgrounds, text) are expected to overlap and are not flagged.")
    clashes = []
    for name, theirs in rivals.items():
        their_accents = [t for t in theirs if not is_neutral(t)]
        print(f"\nvs {name}:")
        for o in ours:
            pool = theirs if is_neutral(o) else their_accents or theirs
            near = min(pool, key=lambda t: distance(o, t))
            d = distance(o, near)
            flag = ''
            if not is_neutral(o) and d < 10:
                flag = '  <-- too close: this accent would read as theirs'
                if name not in clashes:
                    clashes.append(name)
            print(f"  {o} ({describe(o)}) nearest {near} ({describe(near)}): dE00 {d:.1f} {label(d)}{flag}")
    print("\nRESULT:", f"accent too close to: {', '.join(clashes)}" if clashes
          else "no accent sits within dE00 10 of a competitor accent")

def cmd_offpalette(args):
    palette, found, cur = [], [], None
    for tok in args:
        if tok == '--palette':
            cur = palette
        elif tok == '--found':
            cur = found
        else:
            cur.append(hexify(tok))
    allowed = palette + ['#ffffff', '#000000']
    stray = 0
    for c in dict.fromkeys(found):
        near = min(allowed, key=lambda p: distance(c, p))
        d = distance(c, near)
        ok = d <= 5
        stray += not ok
        print(f"{c} ({describe(c)})  nearest {near}  dE00 {d:.1f}  {'in palette' if ok else '<-- off palette'}")
    print("\nRESULT:", f"{stray} color(s) off palette" if stray else "every color belongs to the palette")

def cmd_image(path, n=8):
    from PIL import Image
    im = Image.open(path).convert('RGB')
    im.thumbnail((400, 400))
    q = im.quantize(colors=n, method=Image.Quantize.MEDIANCUT)
    pal = q.getpalette()
    counts = sorted(q.getcolors(), reverse=True)
    total = sum(c for c, _ in counts)
    for count, idx in counts:
        hx = '#' + ''.join(f'{v:02x}' for v in pal[idx * 3: idx * 3 + 3])
        print(f"{hx}  {100 * count / total:5.1f}%  {describe(hx)}")

if __name__ == '__main__':
    a = sys.argv[1:]
    cmd, rest = (a[0], a[1:]) if a else ('', [])
    if cmd == 'contrast' and len(rest) >= 2:
        for x, y in itertools.combinations(rest, 2):
            r = ratio(x, y)
            print(f"{hexify(x)} / {hexify(y)}: {r:.2f}:1  {verdict(r)}")
    elif cmd == 'fix' and len(rest) >= 2:
        goal = float(rest[2]) if len(rest) > 2 else 4.5
        c = fix(rest[0], rest[1], goal)
        print(f"{c}  {ratio(c, rest[1]):.2f}:1 on {hexify(rest[1])}" if c else 'unreachable')
    elif cmd == 'tint' and len(rest) == 2:
        print(mix(rest[0], '#ffffff', float(rest[1])))
    elif cmd == 'describe' and rest:
        for c in rest:
            print(f"{hexify(c)}  {describe(c)}")
    elif cmd == 'compare' and '--ours' in rest and '--vs' in rest:
        cmd_compare(rest)
    elif cmd == 'offpalette' and '--palette' in rest and '--found' in rest:
        cmd_offpalette(rest)
    elif cmd == 'image' and rest:
        cmd_image(rest[0], int(rest[1]) if len(rest) > 1 else 8)
    else:
        print(__doc__)
