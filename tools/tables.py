"""Fixed-width text tables: compare hack vs US vanilla, and pull FR equivalents."""
import json, sys
sys.path.insert(0, 'tools')
from gen3text import decode

TABLES = {
    # name: (us_off, fr_off, count, stride, field_off, field_len)
    'pokemon': (0x245EE0, 0x2402EC, 412, 11, 0, 11),
    'moves': (0x247094, 0x2414A0, 355, 13, 0, 13),
    'abilities': (0x24FC40, 0x24A090, 78, 13, 0, 13),
    'types': (0x24F1A0, 0x2495AC, 18, 7, 0, 7),
    'items': (0x3DB028, 0x3D3324, 375, 44, 0, 14),
    'classes': (0x23E558, 0x238964, 107, 13, 0, 13),
    'dexcat': (0x44E850, 0x447F70, 412, 36, 0, 12),
    'trainers': (0x23EAC8, None, 743, 40, 4, 12),
}

def read_table(rom, off, count, stride, foff, flen):
    out = []
    for i in range(count):
        a = off + i * stride + foff
        raw = rom[a:a + flen]
        t, _ = decode(raw, 0, flen + 1)
        if t is None:
            t = None
        out.append(t)
    return out

if __name__ == '__main__':
    us = open('roms/us.gba', 'rb').read(); fr = open('roms/fr.gba', 'rb').read(); hk = open('roms/hack.gba', 'rb').read()
    result = {}
    for name, (uo, fo, n, st, fo2, fl) in TABLES.items():
        U = read_table(us, uo, n, st, fo2, fl); H = read_table(hk, uo, n, st, fo2, fl)
        F = read_table(fr, fo, n, st, fo2, fl) if fo else [None] * n
        changed = [i for i in range(n) if U[i] != H[i]]
        print(f'{name}: {len(changed)}/{n} changed by hack; sample FR: {F[1]!r} {F[2]!r}')
        result[name] = {'us': U, 'fr': F, 'hack': H, 'changed': changed, 'width': fl - 1,
                        'us_off': uo, 'stride': st, 'field_off': fo2}
    json.dump(result, open('data/derived/tables.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
