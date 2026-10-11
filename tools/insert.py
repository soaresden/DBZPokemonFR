"""Reinsert French text into the hacked ROM: in place when it fits (and nothing else points inside it),
otherwise in free space with repointing of trusted references. Then apply fixed tables and code patches."""
import json, re, sys, os, bisect
OUT = os.environ.get("OUT", "roms/hack_fr.gba")
sys.path.insert(0, 'tools')
from gen3text import encode, decode
from refs import trusted as _trusted
from extract import extract
import battle_suffix

rom = bytearray(open('roms/hack.gba', 'rb').read())
orig = bytes(rom)
cl = json.load(open('data/derived/hack_classified.json', encoding='utf-8'))
tr = json.load(open('data/translations.json', encoding='utf-8'))
for _k, _v in json.load(open('data/derived/official_extra.json', encoding='utf-8')).items(): tr.setdefault(_k, _v)
tt = json.load(open('data/derived/table_translations.json', encoding='utf-8'))
tables = json.load(open('data/derived/tables.json', encoding='utf-8'))
nested = json.load(open('data/nested_translations.json', encoding='utf-8'))
trusted = lambda r: _trusted(orig, r)

# ---- free space allocator (large 0xFF runs in the hack's upper area)
runs = sorted((m.start(), m.end()) for m in re.finditer(rb'\xff{4096,}', orig))
free_ptr = [[a + 16, b - 16] for a, b in runs if a >= 0x800000]
def alloc(n):
    for r in free_ptr:
        if r[1] - r[0] >= n + 1:
            a = r[0]; r[0] += n + 1
            return a
    raise RuntimeError('out of free space')

# ---- every pointer target that has at least one trusted reference (used to detect nested strings)
raw = extract(orig, min_len=1)
targets = sorted(a for a, v in raw.items() if any(trusted(r) for r in v['refs']))
def has_inner_target(a, end):
    i = bisect.bisect_right(targets, a)
    return i < len(targets) and targets[i] < end - 1

rejected, log = [], []
stats = {'inplace': 0, 'relocated': 0, 'forced_reloc': 0, 'skipped_same': 0, 'no_text': 0, 'nested': 0}

def relocate(k, a, data, refs):
    na = alloc(len(data))
    rom[na:na + len(data)] = data
    ptr = (na | 0x08000000).to_bytes(4, 'little'); old = (a | 0x08000000).to_bytes(4, 'little')
    for r in refs:
        assert orig[r:r+4] == old, (k, hex(r))
        if not trusted(r):
            rejected.append((hex(r), k)); continue
        rom[r:r+4] = ptr
    log.append((k, hex(na), len(refs)))

for k, e in cl.items():
    a = int(k, 16); end = e['end']
    new = tr.get(k, e.get('fr'))
    if new is None:
        stats['no_text'] += 1; continue
    if new == e['text']:
        stats['skipped_same'] += 1; continue
    data = encode(new)
    assert orig[a:end] == encode(e['text']), k
    if len(data) <= end - a and not has_inner_target(a, end):
        rom[a:end] = data + b'\xff' * (end - a - len(data))
        stats['inplace'] += 1
    else:
        if len(data) <= end - a: stats['forced_reloc'] += 1
        relocate(k, a, data, e['refs'])
        stats['relocated'] += 1

# ---- strings that start inside another string (hack remnants): always relocated
for k, e in nested.items():
    relocate(k, int(k, 16), encode(e['fr']), e['refs'])
    stats['nested'] += 1

# ---- fixed tables
tstats = {}
for name, entries in tt.items():
    v = tables[name]; off, stride, foff, flen = v['us_off'], v['stride'], v['field_off'], v['width'] + 1
    n = 0
    for i, txt in enumerate(entries):
        if txt is None or txt == v['hack'][i]: continue
        b = encode(txt); assert len(b) <= flen, (name, i, txt)
        pos = off + i * stride + foff
        rom[pos:pos + flen] = b + b'\x00' * (flen - len(b))
        n += 1
    tstats[name] = n

# ---- code patches
bs = battle_suffix.patch(rom, orig, alloc)

open(OUT, 'wb').write(rom)
print(stats); print(tstats); print('battle suffix patch:', bs)
print('free space left:', sum(r[1] - r[0] for r in free_ptr), '| rejected refs:', len(rejected))
json.dump(log, open('data/derived/relocations.json', 'w', encoding='utf-8'), indent=0)
json.dump(rejected, open('data/derived/rejected_refs.json', 'w', encoding='utf-8'), indent=0)
