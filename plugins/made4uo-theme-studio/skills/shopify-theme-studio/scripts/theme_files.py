#!/usr/bin/env python3
"""Local helper for theme files read and written through the Shopify connector.
  decode IN.jsonstr OUT     turn a copied `content` JSON string into the real file
  md5 FILE                  candidate checksums; Shopify's checksumMd5 must equal one of them
                            (Shopify stores templates/config JSON compact, without the /* */ header)
  check FILE...             JSON files must parse; .liquid files must have a parseable {% schema %} (if any)
  compact FILE              print a JSON file as compact JSON, header removed (smallest upload body)
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
    else:
        print(__doc__)
