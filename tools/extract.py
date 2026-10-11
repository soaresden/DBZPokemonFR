"""Extract all pointer-referenced strings from a Gen 3 ROM."""
import sys, json, struct
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from gen3text import decode, is_texty

def scan_pointers(rom: bytes):
    """Yield (position, target) for every byte-aligned 0x08xxxxxx pointer into the ROM."""
    n = len(rom)
    # fast path: find all 0x08/0x09 bytes and check preceding 3 bytes
    i = rom.find(b'\x08', 3)
    while i != -1:
        tgt = int.from_bytes(rom[i-3:i], 'little')
        if tgt < n:
            yield i - 3, tgt
        i = rom.find(b'\x08', i + 1)

def extract(rom: bytes, min_len=1):
    strings = {}   # target -> {'text':..., 'end':..., 'refs':[...]}
    cache = {}
    for pos, tgt in scan_pointers(rom):
        if tgt in cache:
            r = cache[tgt]
        else:
            txt, end = decode(rom, tgt)
            r = None
            if txt is not None and len(txt) >= min_len and is_texty(txt):
                r = {'text': txt, 'end': end}
            cache[tgt] = r
        if r is None: continue
        s = strings.setdefault(tgt, {'text': r['text'], 'end': r['end'], 'refs': []})
        s['refs'].append(pos)
    return strings

def resolve_overlaps(rom: bytes, strings: dict):
    """Drop strings that start inside another string (false pointers)."""
    items = sorted(strings.items())
    kept = []
    for a, v in items:
        if kept and a < kept[-1][1]['end']:
            la, lv = kept[-1]
            l_ok = la == 0 or rom[la-1] in (0xFF, 0x00)
            n_ok = rom[a-1] in (0xFF, 0x00)
            if n_ok and not l_ok and len(v['refs']) >= len(lv['refs']):
                kept[-1] = (a, v)
            continue
        kept.append((a, v))
    return dict(kept)

if __name__ == '__main__':
    rom = open(sys.argv[1], 'rb').read()
    s = resolve_overlaps(rom, extract(rom))
    json.dump({hex(k): v for k, v in sorted(s.items())}, open(sys.argv[2], 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print(len(s), 'strings')

