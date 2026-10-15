#!/usr/bin/env python3
"""Local helper for theme files read and written through the Shopify connector.
  decode IN.jsonstr OUT     turn a copied `content` JSON string into the real file
  md5 FILE                  candidate checksums; Shopify's checksumMd5 must equal one of them
                            (Shopify stores templates/config JSON compact, without the /* */ header)
  check FILE...             JSON files must parse; .liquid files must have a parseable {% schema %} (if any)
  compact FILE              print a JSON file as compact JSON, header removed (smallest upload body)
  ratios [--set portrait|square|landscape] FILE...
                            Horizon product grids: list every product card's image_ratio, the product page
                            gallery's aspect_ratio and each grid's layout; flag "adapt", mixed ratios and
                            editorial/organic layouts (exit 1). --set rewrites all card ratios (and the
                            matching product page gallery ratio) in the given template files, keeping headers.
  In code: header, data = load(path); ...edit only the keys you need...; save(path, header, data)
"""
import hashlib, json, re, sys

_HEADER = re.compile(r'^\s*/\*.*?\*/\s*', re.S)
_SCHEMA = re.compile(r'{%-?\s*schema\s*-?%}(.*?){%-?\s*endschema\s*-?%}', re.S)

def _read(path):
    return open(path, encoding='utf-8').read()

def load(path):
    text = _read(path)
    m = _HEADER.match(text)
    header = m.group(0) if m else ''
    return header, json.loads(text[len(header):])

def save(path, header, data):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(header + json.dumps(data, indent=2, ensure_ascii=False) + '\n')

def compact(data, ascii_only=False):
    return json.dumps(data, separators=(',', ':'), ensure_ascii=ascii_only)

def md5s(path):
    """Candidate checksums; Shopify's value should equal one of them."""
    sums = {hashlib.md5(open(path, 'rb').read()).hexdigest()}
    if path.endswith('.json'):
        _, data = load(path)
        sums |= {hashlib.md5(compact(data, a).encode('utf-8')).hexdigest() for a in (False, True)}
    return sorted(sums)

def check(path):
    if path.endswith('.json'):
        load(path)
    elif path.endswith('.liquid'):
        m = _SCHEMA.search(_read(path))
        if m:
            json.loads(m.group(1))

# Horizon: product card image ratio -> the product page gallery's matching aspect_ratio value
_MEDIA_FOR = {'portrait': '1/1.25', 'square': '1'}
_GRID_SECTIONS = ('product-list', 'main-collection', 'search-results', 'product-recommendations')
_VARIED_LAYOUTS = ('editorial', 'organic')

def ratio_nodes(data):
    """(path, kind, settings) for every product card gallery, product media gallery and product grid section."""
    out = []
    def walk(node, path):
        if isinstance(node, dict):
            t, st = node.get('type'), node.get('settings')
            if isinstance(st, dict):
                if t == '_product-card-gallery':
                    out.append((path, 'card', st))
                elif t == '_product-media-gallery':
                    out.append((path, 'media', st))
                elif t in _GRID_SECTIONS:
                    out.append((path, 'grid', st))
            for k, v in node.items():
                walk(v, path if k in ('sections', 'blocks', 'settings') else f'{path}/{k}')
    walk(data, '')
    return out

def ratios(paths, set_to=None):
    """Report (and with set_to, rewrite) product image ratios so every grid matches. Returns problem count."""
    seen, problems, grid_sizes = {}, 0, {}
    for p in paths:
        try:
            header, data = load(p)
        except FileNotFoundError:
            sys.exit(f'no such file: {p}')
        except ValueError as e:
            sys.exit(f'{p} is not valid JSON: {e}')
        changed = False
        for path, kind, st in ratio_nodes(data):
            if kind == 'card':
                if set_to and st.get('image_ratio') != set_to:
                    st['image_ratio'] = set_to; changed = True
                val = st.get('image_ratio', 'portrait')  # Horizon's default for the block
                seen.setdefault(val, []).append(f'{p}:{path}')
                print(f'{p}:{path}  product card image_ratio = {val}')
            elif kind == 'media':
                if set_to in _MEDIA_FOR and st.get('aspect_ratio') != _MEDIA_FOR[set_to]:
                    st['aspect_ratio'] = _MEDIA_FOR[set_to]; changed = True
                val = st.get('aspect_ratio', 'adapt')
                print(f'{p}:{path}  product page gallery aspect_ratio = {val}')
                if val == 'adapt':
                    problems += 1
                    print('  ! the product page gallery keeps each photo\'s own shape; set aspect_ratio to match the cards '
                          '("1/1.25" for portrait, "1" for square, "2/1" nearest to landscape)')
            else:
                layout = st.get('layout_type', 'grid')
                sizes = {k: st[k] for k in ('product_card_size', 'mobile_product_card_size', 'mobile_card_size', 'columns') if k in st}
                print(f'{p}:{path}  grid layout = {layout} {sizes}')
                if layout in _VARIED_LAYOUTS:
                    problems += 1
                    print(f'  ! layout "{layout}" gives cards different sizes; use "grid" (or "carousel") for even cards')
                if 'product_card_size' in st or 'mobile_product_card_size' in st:
                    grid_sizes[f'{p}:{path}'] = (st.get('product_card_size', 'medium'), st.get('mobile_product_card_size', 'small'))
        if changed:
            save(p, header, data)
            print(f'  updated {p}')
    if 'adapt' in seen:
        problems += 1
        print('! "adapt" keeps each photo\'s own shape, so grids go uneven; choose portrait, square or landscape')
    if len(seen) > 1:
        problems += 1
        print(f'! product cards use different ratios: {", ".join(sorted(seen))}')
    if len(set(grid_sizes.values())) > 1:
        problems += 1
        print('! collection and search grids use different card sizes: '
              + '; '.join(f'{k} {v[0]}/{v[1]} mobile' for k, v in grid_sizes.items()))
    if not seen:
        print('note: no product cards found in these files')
    if set_to == 'landscape':
        print('note: the product page gallery has no 16:9 option; set its aspect_ratio by hand ("2/1" is the nearest)')
    print(f'{problems} problem(s)' + (' left to fix by hand' if set_to and problems else ''))
    return problems

if __name__ == '__main__':
    a = sys.argv[1:]
    cmd = a[0] if a else ''
    if cmd == 'decode' and len(a) == 3:
        with open(a[2], 'w', encoding='utf-8', newline='') as f:
            f.write(json.loads(_read(a[1])))
        print(f"wrote {a[2]}")
    elif cmd == 'md5' and len(a) == 2:
        print(' '.join(md5s(a[1])))
    elif cmd == 'check' and len(a) > 1:
        for p in a[1:]:
            try:
                check(p)
            except Exception as e:
                print(f"INVALID {p}: {e}"); sys.exit(1)
        print(f"OK {len(a) - 1} file(s)")
    elif cmd == 'compact' and len(a) == 2:
        print(compact(load(a[1])[1]))
    elif cmd == 'ratios' and len(a) > 1:
        set_to = None
        if '--set' in a:
            i = a.index('--set')
            set_to = a[i + 1] if i + 1 < len(a) else ''
            if set_to not in ('portrait', 'square', 'landscape'):
                sys.exit('--set takes portrait, square or landscape')
            a = a[:i] + a[i + 2:]
        if len(a) < 2:
            sys.exit('ratios needs at least one template file')
        sys.exit(1 if ratios(a[1:], set_to) else 0)
    else:
        print(__doc__)
