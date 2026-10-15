#!/usr/bin/env python3
"""Logo tools for Made4Uo Shopify Theme Studio: outlined wordmarks, SVG checks and Shopify-ready exports.

  python3 brand_logo.py text     FONT "Text" [--axis wght=600 ...] [--tracking 40] [--case upper|lower|asis]
                                 [--size 100] [--out text.json]
      Shape the text with the font (kerning and ligatures via HarfBuzz) and print its outlines as one SVG
      path, moved so its tight box starts at 0,0: {"d", "width", "height", "baseline", "font", "license"}.
      --tracking is letter spacing in thousandths of the font size (40 = 0.04em). --axis pins a variable
      font axis (wght, opsz, wdth, ...). Use the "d" in your own logo SVG.

  python3 brand_logo.py wordmark FONT "Text" --fill "#2d4a2b" --out wordmark.svg [same options as text]
      A finished, outlined wordmark SVG with a tight viewBox.

  python3 brand_logo.py check    LOGO.svg [--palette "#2d4a2b" "#faf9f6" ...]
      Checks a logo is safe and self-contained: valid XML, a viewBox, no <text> (outline all lettering),
      no scripts, event handlers, external links, embedded images or foreignObject. Lists every color and
      flags colors outside --palette, strokes too thin to survive small sizes, and files over 30 KB.
      Exit code 1 on any error.

  python3 brand_logo.py export   LOGO.svg --out logo.png (--width 1200 | --height 300) [--map "#old=#new" ...]
      Transparent PNG. --map swaps colors, e.g. dark ink to white for the inverse logo.

  python3 brand_logo.py favicon  MARK.svg --out favicon.png [--size 512] [--bg "#hex"] [--pad 0.14] [--map ...]
      Square PNG for Shopify's favicon setting; also writes <out>-32.png and <out>-16.png so you can judge it
      at the size browsers show it.

  python3 brand_logo.py recolor  LOGO.svg --out INVERSE.svg --map "#old=#new" [--map ...]
      A recolored copy of an SVG, e.g. the inverse logo. Colors are matched by value (3- or 6-digit hex, rgb()).

  python3 brand_logo.py sheet    --logo LOGO.svg --inverse INVERSE.svg [--mark MARK.svg]
                                 --light "#faf9f6" --dark "#2d4a2b" --out sheet.png
      A legibility sheet: the logo at Horizon's header heights (28 px mobile, 36 px desktop) on the light
      and dark backgrounds, and the mark at 16, 32 and 64 px. Read the PNG to judge it.

Needs fontTools and uharfbuzz (text, wordmark), and cairosvg and Pillow (export, favicon, sheet):
  pip install fonttools uharfbuzz cairosvg pillow   (add --break-system-packages where pip asks for it)
Fonts: use open-licensed (SIL OFL) font files, e.g. from github.com/google/fonts; OFL lets you use
outlined lettering in a logo. Never use a font you don't have a license for.
"""
import argparse, io, json, os, re, sys
import xml.etree.ElementTree as ET

SVG_NS = 'http://www.w3.org/2000/svg'
XLINK = '{http://www.w3.org/1999/xlink}href'


# ---------- text to outlines ----------

def _parse_axes(items):
    axes = {}
    for it in items or []:
        k, _, v = it.partition('=')
        if not v:
            sys.exit(f'--axis needs tag=value, got {it!r}')
        axes[k.strip()] = float(v)
    return axes


def shape_outlines(font_path, text, axes=None, tracking=0.0, size=100.0):
    from fontTools.ttLib import TTFont
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.pens.transformPen import TransformPen
    from fontTools.pens.boundsPen import BoundsPen
    import uharfbuzz as hb

    if not text or not text.strip():
        sys.exit('the text is empty')
    font = TTFont(font_path)
    upem = font['head'].unitsPerEm
    axes = dict(axes or {})
    if 'fvar' in font:
        known = {a.axisTag: a for a in font['fvar'].axes}
        for tag in axes:
            if tag not in known:
                sys.exit(f'axis {tag} not in this font; it has {", ".join(known)}')
            a = known[tag]
            if not a.minValue <= axes[tag] <= a.maxValue:
                sys.exit(f'{tag}={axes[tag]} outside {a.minValue}..{a.maxValue}')
    elif axes:
        sys.exit('this font is not variable; drop --axis')

    blob = hb.Blob.from_file_path(font_path)
    hbfont = hb.Font(hb.Face(blob))
    if axes:
        hbfont.set_variations(axes)
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(hbfont, buf, {'kern': True, 'liga': True})
    missing = sorted({text[i.cluster] for i in buf.glyph_infos if i.codepoint == 0 and not text[i.cluster].isspace()})
    if missing:
        sys.exit(f'the font has no glyph for: {" ".join(missing)} (pick a font that covers every character)')

    glyphset = font.getGlyphSet(location=axes) if axes else font.getGlyphSet()
    order = font.getGlyphOrder()
    scale = size / upem
    track = tracking / 1000.0 * upem

    placed, x = [], 0.0
    n = len(buf.glyph_infos)
    for i, (info, pos) in enumerate(zip(buf.glyph_infos, buf.glyph_positions)):
        placed.append((order[info.codepoint], x + pos.x_offset, pos.y_offset))
        x += pos.x_advance + (track if i < n - 1 else 0)

    bounds = BoundsPen(glyphset)  # pass 1: tight box in font units (y up)
    for name, ox, oy in placed:
        glyphset[name].draw(TransformPen(bounds, (1, 0, 0, 1, ox, oy)))
    if bounds.bounds is None:
        sys.exit('the text has no visible glyphs')
    xmin, ymin, xmax, ymax = bounds.bounds

    svgpen = SVGPathPen(glyphset, ntos=lambda v: f'{v:.2f}'.rstrip('0').rstrip('.'))
    for name, ox, oy in placed:  # pass 2: scaled, y flipped, box moved to 0,0
        glyphset[name].draw(TransformPen(svgpen, (scale, 0, 0, -scale, (ox - xmin) * scale, (ymax - oy) * scale)))
    d = svgpen.getCommands()

    names = font['name']
    family = names.getDebugName(16) or names.getDebugName(1) or os.path.basename(font_path)
    license_ = names.getDebugName(13) or ''
    return {
        'd': d,
        'width': round((xmax - xmin) * scale, 3),
        'height': round((ymax - ymin) * scale, 3),
        'baseline': round(ymax * scale, 3),
        'font': family,
        'axes': axes,
        'license': ('SIL Open Font License' if 'Open Font License' in license_ else license_[:120]),
    }


def _case(text, mode):
    return text.upper() if mode == 'upper' else text.lower() if mode == 'lower' else text


def cmd_text(a):
    r = shape_outlines(a.font, _case(a.text, a.case), _parse_axes(a.axis), a.tracking, a.size)
    s = json.dumps(r, indent=1)
    if a.out:
        open(a.out, 'w').write(s)
        print(f'wrote {a.out}: {r["width"]} x {r["height"]}, font {r["font"]} ({r["license"] or "license unknown"})')
    else:
        print(s)


def cmd_wordmark(a):
    r = shape_outlines(a.font, _case(a.text, a.case), _parse_axes(a.axis), a.tracking, a.size)
    w, h = r['width'], r['height']
    label = a.title or a.text
    svg = (f'<svg xmlns="{SVG_NS}" viewBox="0 0 {w:g} {h:g}" role="img" aria-label="{_esc(label)}">'
           f'<title>{_esc(label)}</title><path fill="{a.fill}" d="{r["d"]}"/></svg>\n')
    open(a.out, 'w').write(svg)
    print(f'wrote {a.out}: viewBox 0 0 {w:g} {h:g}, font {r["font"]} ({r["license"] or "license unknown"})')
    if r['license'] != 'SIL Open Font License':
        print('note: not an OFL font; confirm the license allows use in a logo')


def _esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('"', '&quot;')


# ---------- checks ----------

COLOR_ATTRS = ('fill', 'stroke', 'stop-color', 'flood-color', 'lighting-color', 'color')
BANNED = {'script', 'foreignObject', 'image', 'text', 'tspan', 'textPath', 'iframe', 'video', 'audio'}
SHAPES = {'path', 'rect', 'circle', 'ellipse', 'polygon', 'polyline', 'line'}
NAMED = {'black': '#000000', 'white': '#ffffff', 'red': '#ff0000', 'green': '#008000', 'blue': '#0000ff'}


def _norm(c):
    c = c.strip().lower()
    if c in NAMED:
        return NAMED[c]
    if re.fullmatch(r'#[0-9a-f]{3}', c):
        return '#' + ''.join(ch * 2 for ch in c[1:])
    if re.fullmatch(r'#[0-9a-f]{6}([0-9a-f]{2})?', c):
        return c[:7]
    m = re.fullmatch(r'rgba?\(\s*(\d+)[ ,]+(\d+)[ ,]+(\d+).*\)', c)
    if m:
        return '#%02x%02x%02x' % tuple(int(x) for x in m.groups())
    return c


def _local(tag):
    return tag.split('}', 1)[-1]


def cmd_check(a):
    raw = open(a.svg, 'rb').read()
    errors, warns = [], []
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as e:
        print(f'error  xml       {e}')
        sys.exit(1)
    if _local(root.tag) != 'svg':
        errors.append('root element is not <svg>')
    vb = root.get('viewBox')
    vh = None
    if not vb:
        errors.append('no viewBox: the logo will not scale cleanly')
    else:
        try:
            vh = float(vb.replace(',', ' ').split()[3])
        except (IndexError, ValueError):
            errors.append(f'bad viewBox {vb!r}')
    colors, paths = set(), 0
    if not any(_local(el.tag) == 'title' and (el.text or '').strip() for el in root.iter()):
        errors.append('no <title> with the brand name (screen readers and image search use it)')
    # shapes that draw with the default black fill: no fill set on them or any ancestor (and no CSS rules)
    has_css = any(_local(el.tag) == 'style' for el in root.iter())
    def walk(el, fill_set, in_defs):
        name = _local(el.tag)
        own = el.get('fill') is not None or re.search(r'(^|;)\s*fill\s*:', el.get('style', '')) is not None
        fill_set = fill_set or own
        in_defs = in_defs or name in ('defs', 'clipPath', 'mask', 'symbol')
        if name in SHAPES and not fill_set and not has_css and not in_defs:
            colors.add('#000000')
        for ch in el:
            walk(ch, fill_set, in_defs)
    walk(root, False, False)
    for el in root.iter():
        name = _local(el.tag)
        if name in BANNED:
            hint = ' (outline lettering with brand_logo.py text)' if name in ('text', 'tspan', 'textPath') else ''
            errors.append(f'<{name}> not allowed in a logo{hint}')
        if name in SHAPES:
            paths += 1
        if name == 'style' and el.text:
            if re.search(r'@import|url\(\s*[\'"]?(https?:|//)', el.text):
                errors.append('<style> loads an external resource')
            for prop, val in re.findall(r'([\w-]+)\s*:\s*([^;}]+)', el.text):
                if prop in COLOR_ATTRS and val.strip() not in ('none', 'transparent', 'currentColor', 'inherit') \
                        and not val.strip().startswith('url('):
                    colors.add(_norm(val))
        for k, v in el.attrib.items():
            lk = _local(k)
            if lk.lower().startswith('on'):
                errors.append(f'event handler {lk}= on <{name}>')
            if lk == 'href' and not v.startswith('#'):
                errors.append(f'<{name}> links outside the file: {v[:60]}')
            if lk in COLOR_ATTRS and v not in ('none', 'transparent', 'currentColor', 'inherit') and not v.startswith('url('):
                colors.add(_norm(v))
            if lk == 'style':
                for prop, val in re.findall(r'([\w-]+)\s*:\s*([^;]+)', v):
                    if prop in COLOR_ATTRS and val.strip() not in ('none', 'transparent', 'currentColor', 'inherit') \
                            and not val.strip().startswith('url('):
                        colors.add(_norm(val))
            if lk == 'stroke-width' and vh:
                try:
                    if float(re.sub(r'[a-z%]+$', '', v)) / vh < 0.02:
                        warns.append(f'stroke-width {v} is under 2% of the logo height; it may vanish at header size')
                except ValueError:
                    pass
    pal = {_hex_arg(p, '--palette') for p in (a.palette or [])}
    for c in sorted(c for c in colors if pal and c not in pal):
        hint = ' (a shape with no fill draws black)' if c == '#000000' else ''
        errors.append(f'color {c} is not in the brand palette{hint}')
    if len(raw) > 30_000:
        warns.append(f'{len(raw) // 1024} KB: simplify paths; a logo SVG is usually under 30 KB')
    ratio = ''
    if vb and vh:
        vw = float(vb.replace(',', ' ').split()[2])
        ratio = f', aspect {vw / vh:.1f}:1'
        if vw / vh > 6:
            warns.append(f'aspect {vw / vh:.1f}:1 is wider than 6:1; as a header logo it gets small on phones '
                         f'({vw / vh * 28:.0f} px wide at 28 px high)')
    print(f'{a.svg}: viewBox {vb}{ratio}, {paths} shape(s), {len(raw)} bytes, colors: {", ".join(sorted(colors)) or "none"}')
    for e in errors:
        print(f'error  {e}')
    for w in warns:
        print(f'warn   {w}')
    print(f'{len(errors)} error(s), {len(warns)} warning(s)')
    sys.exit(1 if errors else 0)


# ---------- rendering ----------

COLOR_TOKEN = re.compile(r'#[0-9a-fA-F]{8}\b|#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b|rgba?\([^)]*\)', re.I)


def _hex_arg(v, flag):
    """'#abc', 'abc', '#aabbcc' -> '#aabbcc'; anything else exits with a clear message."""
    v = v.strip()
    if not v.startswith('#'):
        v = '#' + v
    n = _norm(v)
    if not re.fullmatch(r'#[0-9a-f]{6}', n):
        sys.exit(f'{flag}: {v!r} is not a hex color like #2d4a2b')
    return n


def _svg_bytes(path, maps):
    s = open(path, encoding='utf-8').read()
    table = {}
    for m in maps or []:
        old, _, new = m.partition('=')
        if not new:
            sys.exit(f'--map needs #old=#new, got {m!r}')
        table[_hex_arg(old, '--map')] = _hex_arg(new, '--map')
    if table:
        hits = [0]
        def swap(mo):
            tok = mo.group(0)
            n = _norm(tok)
            if n in table:
                hits[0] += 1
                alpha = tok[7:9] if len(tok) == 9 else ''  # keep #RRGGBBAA transparency
                return table[n] + alpha
            return tok
        s = COLOR_TOKEN.sub(swap, s)
        if not hits[0]:
            print(f'warn: --map matched no color in {path}', file=sys.stderr)
    return s.encode('utf-8')


def _render(svg_bytes, width=None, height=None):
    import cairosvg
    kw = {}
    if width:
        kw['output_width'] = int(width)
    if height:
        kw['output_height'] = int(height)
    return cairosvg.svg2png(bytestring=svg_bytes, unsafe=False, **kw)


def cmd_recolor(a):
    open(a.out, 'wb').write(_svg_bytes(a.svg, a.map))
    print(f'wrote {a.out}')


def cmd_export(a):
    if not (a.width or a.height):
        sys.exit('give --width or --height')
    png = _render(_svg_bytes(a.svg, a.map), a.width, a.height)
    open(a.out, 'wb').write(png)
    from PIL import Image
    im = Image.open(io.BytesIO(png))
    print(f'wrote {a.out}: {im.size[0]} x {im.size[1]} px, transparent background')


def _square(svg_bytes, size, pad, bg):
    from PIL import Image
    inner = int(size * (1 - 2 * pad))
    art = Image.open(io.BytesIO(_render(svg_bytes, width=inner))).convert('RGBA')
    if art.size[1] > inner:  # tall mark: fit by height instead
        art = Image.open(io.BytesIO(_render(svg_bytes, height=inner))).convert('RGBA')
    canvas = Image.new('RGBA', (size, size), bg or (0, 0, 0, 0))
    canvas.alpha_composite(art, ((size - art.size[0]) // 2, (size - art.size[1]) // 2))
    return canvas


def cmd_favicon(a):
    from PIL import Image
    img = _square(_svg_bytes(a.svg, a.map), a.size, a.pad, _hex_arg(a.bg, '--bg') if a.bg else None)
    img.save(a.out)
    stem, ext = os.path.splitext(a.out)
    for s in (32, 16):
        img.resize((s, s), Image.LANCZOS).save(f'{stem}-{s}{ext}')
    print(f'wrote {a.out} ({a.size} px) and {stem}-32{ext}, {stem}-16{ext} to judge legibility')


def cmd_sheet(a):
    from PIL import Image, ImageDraw
    a.light, a.dark = _hex_arg(a.light, '--light'), _hex_arg(a.dark, '--dark')
    if not a.inverse:
        sys.exit('give --inverse with the light-on-dark logo, so the dark band shows what shoppers will see '
                 '(make one with: recolor LOGO.svg --out INVERSE.svg --map "#dark=#light")')
    rows = []
    for svg, bg in ((a.logo, a.light), (a.inverse, a.dark)):
        for h in (28, 36):
            art = Image.open(io.BytesIO(_render(_svg_bytes(svg, None), height=h * 2))).convert('RGBA')
            art = art.resize((max(1, art.size[0] // 2), h), Image.LANCZOS)  # true 1x size, rendered sharp
            rows.append((art, bg))
    marks = []
    if a.mark:
        for s in (16, 32, 64):
            marks.append(_square(_svg_bytes(a.mark, None), s * 4, 0.08, None).resize((s, s), Image.LANCZOS))
    W = max([r[0].size[0] for r in rows] + [sum(m.size[0] for m in marks) + 24 * len(marks)]) + 48
    H = sum(r[0].size[1] + 32 for r in rows) + (96 if marks else 0)
    sheet = Image.new('RGBA', (W, H), '#ffffff')
    y = 0
    for art, bg in rows:
        h = art.size[1] + 32
        ImageDraw.Draw(sheet).rectangle([0, y, W, y + h], fill=bg)
        sheet.alpha_composite(art, (24, y + 16))
        y += h
    if marks:
        ImageDraw.Draw(sheet).rectangle([0, y, W, H], fill=a.light)
        x = 24
        for m in marks:
            sheet.alpha_composite(m, (x, y + 16 + (64 - m.size[1]) // 2))
            x += m.size[0] + 24
    sheet = sheet.resize((sheet.size[0] * 2, sheet.size[1] * 2), Image.NEAREST)  # enlarge pixels for viewing
    sheet.save(a.out)
    print(f'wrote {a.out}: header heights 28 and 36 px on {a.light} and {a.dark}'
          + (', mark at 16, 32, 64 px' if marks else '') + ' (shown at 2x, pixels enlarged)')


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='cmd', required=True)

    def text_opts(sp):
        sp.add_argument('font')
        sp.add_argument('text')
        sp.add_argument('--axis', action='append', default=[])
        sp.add_argument('--tracking', type=float, default=0.0)
        sp.add_argument('--case', choices=('upper', 'lower', 'asis'), default='asis')
        sp.add_argument('--size', type=float, default=100.0)

    t = sub.add_parser('text'); text_opts(t); t.add_argument('--out'); t.set_defaults(fn=cmd_text)
    w = sub.add_parser('wordmark'); text_opts(w)
    w.add_argument('--fill', required=True); w.add_argument('--out', required=True); w.add_argument('--title')
    w.set_defaults(fn=cmd_wordmark)
    c = sub.add_parser('check'); c.add_argument('svg'); c.add_argument('--palette', nargs='*'); c.set_defaults(fn=cmd_check)
    e = sub.add_parser('export'); e.add_argument('svg'); e.add_argument('--out', required=True)
    e.add_argument('--width', type=int); e.add_argument('--height', type=int); e.add_argument('--map', action='append')
    e.set_defaults(fn=cmd_export)
    f = sub.add_parser('favicon'); f.add_argument('svg'); f.add_argument('--out', required=True)
    f.add_argument('--size', type=int, default=512); f.add_argument('--bg'); f.add_argument('--pad', type=float, default=0.14)
    f.add_argument('--map', action='append'); f.set_defaults(fn=cmd_favicon)
    r = sub.add_parser('recolor'); r.add_argument('svg'); r.add_argument('--out', required=True)
    r.add_argument('--map', action='append', required=True); r.set_defaults(fn=cmd_recolor)
    s = sub.add_parser('sheet'); s.add_argument('--logo', required=True); s.add_argument('--inverse'); s.add_argument('--mark')
    s.add_argument('--light', required=True); s.add_argument('--dark', required=True); s.add_argument('--out', required=True)
    s.set_defaults(fn=cmd_sheet)
    a = p.parse_args()
    a.fn(a)


if __name__ == '__main__':
    main()
