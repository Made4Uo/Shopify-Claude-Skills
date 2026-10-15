#!/usr/bin/env python3
"""Design-consistency lint for theme files you created or changed.
  python3 theme_lint.py [--tokens FILE] FILE...

Flags design values written by hand instead of coming from the theme's CSS variables or settings:
  error  color      a color literal (#hex, rgb(), hsl()) in a color property
  error  font       a font-family that isn't a var() or a setting
  error  type       a px/rem font-size that isn't built on a var()
  error  token      a custom property defined with a literal color outside the tokens file
  warn   radius     a px/rem border-radius that isn't a var()
  warn   spacing    a px/rem margin, padding or gap that isn't a var()
  warn   important  !important
Values that use var(), Liquid output ({{ ... }}), or keywords (inherit, currentColor, transparent, 0) pass.
The --tokens file (your single place for new design tokens) may define custom properties with literal values.
Checks .css and .liquid files (style tags, {% style %}/{% stylesheet %} blocks and style="" attributes).

Also checks theme JSON (templates/*.json, sections/*-group.json, config/settings_data.json) for Horizon's
color palette:
  error  palette    an opaque hex color in a section, block or global color setting; reference the palette
                    instead, e.g. "{{ settings.color_palette.color1 }}"
  warn   alpha      a hex color with transparency (#RRGGBBAA); palettes can't hold alpha, so overlays and
                    tints may keep it, but confirm it is deliberate
The same two checks run on the "default" of every color setting in a .liquid file's {% schema %}.
The palette itself ("color_palette" in config/settings_data.json) holds the only literal hex values.
Exit code 1 when there is at least one error.
"""
import json, re, sys

COLOR = re.compile(r'#[0-9a-fA-F]{3,8}\b|\b(?:rgba?|hsla?)\(')
LENGTH = re.compile(r'(?<![\w.-])-?\d*\.?\d+(?:px|rem)\b')
COLOR_PROPS = re.compile(r'^(?:color|background(?:-color)?|border(?:-(?:top|right|bottom|left|block|inline)(?:-(?:start|end))?)?(?:-color)?'
                         r'|outline(?:-color)?|fill|stroke|box-shadow|text-shadow|text-decoration(?:-color)?|caret-color'
                         r'|accent-color|column-rule(?:-color)?)$')
SPACING = re.compile(r'^(?:margin|padding)(?:-(?:top|right|bottom|left|block|inline)(?:-(?:start|end))?)?$|^(?:row-|column-)?gap$')
DECL = re.compile(r'(?:^|[;{\s"\'])(-{0,2}[a-zA-Z][\w-]*)\s*:\s*([^;{}\n]+)')
BLOCKS = re.compile(r'<style\b[^>]*>(.*?)</style>|{%-?\s*(?:style|stylesheet)\s*-?%}(.*?){%-?\s*end(?:style|stylesheet)\s*-?%}'
                    r'|\bstyle="([^"]*)"', re.S | re.I)
STRIP_LIQUID = re.compile(r'{%-?\s*(schema|comment|javascript)\s*-?%}.*?{%-?\s*end\1\s*-?%}', re.S)
KEYWORDS = {'inherit', 'initial', 'unset', 'revert', 'none', 'transparent', 'currentcolor', '0'}

def _blank(m):
    # keep line numbers stable when removing text
    return re.sub(r'[^\n]', ' ', m.group(0))

def regions(path, text):
    """(offset, css_text) pairs to check."""
    if path.endswith('.css') or path.endswith('.css.liquid'):
        return [(0, re.sub(r'/\*.*?\*/', _blank, text, flags=re.S))]
    if path.endswith('.liquid'):
        text = STRIP_LIQUID.sub(_blank, text)
        out = []
        for m in BLOCKS.finditer(text):
            g = next(i for i in (1, 2, 3) if m.group(i) is not None)
            out.append((m.start(g), re.sub(r'/\*.*?\*/', _blank, m.group(g), flags=re.S)))
        return out
    return []

def passes(value):
    v = value.strip().lower().rstrip(';').strip()
    return 'var(' in v or '{{' in v or v in KEYWORDS

HEX = re.compile(r'^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$')

def check_json(text):
    """Literal hex colors in theme JSON, reported by key path instead of line number."""
    body = re.sub(r'^\s*/\*.*?\*/', '', text, count=1, flags=re.S)   # Shopify's comment header
    try:
        data = json.loads(body)
    except ValueError as e:
        return [('-', 'error', 'json', f'does not parse: {e}')]
    found = []
    def walk(node, keys):
        if isinstance(node, dict):
            for k, v in node.items():
                if k == 'color_palette':        # the palette is where literal colors belong
                    continue
                walk(v, keys + [str(k)])
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, keys + [str(i)])
        elif isinstance(node, str) and HEX.match(node.strip()):
            where = '.'.join(keys)
            if len(node.strip()) in (5, 9):
                found.append((where, 'warn', 'alpha', f'{keys[-1]}: {node}'))
            else:
                found.append((where, 'error', 'palette', f'{keys[-1]}: {node} -> use "{{{{ settings.color_palette.<key> }}}}"'))
    walk(data, [])
    return found

SCHEMA = re.compile(r'{%-?\s*schema\s*-?%}(.*?){%-?\s*endschema\s*-?%}', re.S)

def check_schema_defaults(text):
    """Hex defaults on color settings inside a Liquid {% schema %}."""
    m = SCHEMA.search(text)
    if not m:
        return []
    try:
        schema = json.loads(m.group(1))
    except ValueError as e:
        line = text.count('\n', 0, m.start(1)) + 1
        return [(line, 'error', 'json', f'schema does not parse: {e}')]
    found = []
    def settings_lists(node):
        if isinstance(node, dict):
            for k, v in node.items():
                if k == 'settings' and isinstance(v, list):
                    yield v
                yield from settings_lists(v)
        elif isinstance(node, list):
            for v in node:
                yield from settings_lists(v)
    for settings in settings_lists(schema):
        for st in settings:
            if not isinstance(st, dict) or st.get('type') not in ('color', 'color_background'):
                continue
            default = st.get('default')
            if not isinstance(default, str):
                continue
            hexes = re.findall(r'#[0-9a-fA-F]{3,8}\b', default)
            if not hexes:
                continue
            at = text.find(default, m.start(1))
            line = text.count('\n', 0, at) + 1 if at >= 0 else text.count('\n', 0, m.start(1)) + 1
            if all(len(h) in (5, 9) for h in hexes):
                found.append((line, 'warn', 'alpha', f'{st.get("id")} default: {default}'))
            else:
                found.append((line, 'error', 'palette', f'{st.get("id")} default: {default} -> use "{{{{ settings.color_palette.<key> }}}}" or no default'))
    return found

def check(path, tokens_file=None):
    text = open(path, encoding='utf-8').read()
    if path.endswith('.json'):
        return check_json(text)
    found = check_schema_defaults(text) if path.endswith('.liquid') else []
    for base, css in regions(path, text):
        for m in DECL.finditer(css):
            prop, value = m.group(1).lower(), m.group(2).strip()
            line = text.count('\n', 0, base + m.start(1)) + 1
            raw = value.lower()
            if '!important' in raw:
                found.append((line, 'warn', 'important', f'{prop}: {value}'))
            if prop.startswith('--'):
                if COLOR.search(value) and '{{' not in value and path != tokens_file:
                    found.append((line, 'error', 'token', f'{prop}: {value}'))
                continue
            if passes(value):
                continue
            if COLOR_PROPS.match(prop) and COLOR.search(value):
                found.append((line, 'error', 'color', f'{prop}: {value}'))
            elif prop == 'font-family':
                found.append((line, 'error', 'font', f'{prop}: {value}'))
            elif prop in ('font-size', 'font') and LENGTH.search(value):
                found.append((line, 'error', 'type', f'{prop}: {value}'))
            elif prop.startswith('border') and 'radius' in prop and LENGTH.search(value):
                found.append((line, 'warn', 'radius', f'{prop}: {value}'))
            elif SPACING.match(prop) and LENGTH.search(value):
                found.append((line, 'warn', 'spacing', f'{prop}: {value}'))
    return found

if __name__ == '__main__':
    args, tokens = sys.argv[1:], None
    if '--tokens' in args:
        i = args.index('--tokens')
        tokens = args[i + 1]
        args = args[:i] + args[i + 2:]
    if not args or args[0] in ('-h', '--help'):
        print(__doc__)
        sys.exit(0)
    errors = warnings = 0
    for path in args:
        for line, level, kind, snippet in check(path, tokens):
            print(f"{path}:{line}  {level:5}  {kind:9}  {snippet}")
            errors += level == 'error'
            warnings += level == 'warn'
    print(f"\n{errors} error(s), {warnings} warning(s) in {len(args)} file(s)")
    sys.exit(1 if errors else 0)
