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
Exit code 1 when there is at least one error.
"""
import re, sys

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

def check(path, tokens_file=None):
    text = open(path, encoding='utf-8').read()
    found = []
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
    if not args:
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
