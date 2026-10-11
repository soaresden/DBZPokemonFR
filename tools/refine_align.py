"""Refine US/FR alignment using pointer-position deltas (script code is identical between languages,
so within a block the ref delta is constant)."""
import json, bisect
import re
CTRL2 = re.compile(r'\[FD [0-9A-F]{2}\]|\[FC(?: [0-9A-F]{2})+\]')
def sig(t): return tuple(CTRL2.findall(t))

us = json.load(open('data/derived/us.json', encoding='utf-8')); fr = json.load(open('data/derived/fr.json', encoding='utf-8'))
al = json.load(open('data/derived/align_us_fr.json', encoding='utf-8'))

# index FR strings by ref position
fr_by_ref = {}
for k, v in fr.items():
    for r in v['refs']:
        fr_by_ref[r] = int(k, 16)

pairs = sorted((int(a, 16), int(b, 16)) for a, b in al.items())
def delta(a, b):
    return min(fr[hex(b)]['refs']) - min(us[hex(a)]['refs'])

deltas = [delta(a, b) for a, b in pairs]
anchors = []  # (us_addr, fr_addr, delta)
for i, (a, b) in enumerate(pairs):
    d = deltas[i]
    if (i > 0 and deltas[i-1] == d) or (i + 1 < len(pairs) and deltas[i+1] == d):
        anchors.append((a, b, d))
print('anchors', len(anchors), 'of', len(pairs))
# anchors keyed by ref position
ref_anchors = sorted((r, d) for a, b, d in anchors for r in us[hex(a)]['refs'])
ref_pos = [r for r, _ in ref_anchors]

final = {}
claimed = set()
for a, b, d in anchors:
    final[a] = b; claimed.add(b)
unmatched = []
todo = [(int(k, 16), v) for k, v in us.items() if int(k, 16) not in final]
for strict in (True, False):
    rest = []
    for a, v in todo:
        k = hex(a)
        # candidate deltas ordered by anchor proximity
        cands = []
        for r in v['refs']:
            i = bisect.bisect_left(ref_pos, r)
            for j in range(max(0, i-6), min(len(ref_anchors), i+6)):
                cands.append((abs(ref_anchors[j][0] - r), ref_anchors[j][1]))
        cands.sort()
        found = None
        seen = set()
        for _, d in cands:
            if d in seen: continue
            seen.add(d)
            for r in v['refs']:
                b = fr_by_ref.get(r + d)
                if b is None or b in claimed: continue
                if strict and sig(us[k]['text']) != sig(fr[hex(b)]['text']): continue
                found = b; break
            if found is not None: break
        if found is None: rest.append((a, v))
        else: final[a] = found; claimed.add(found)
    todo = rest
unmatched = [a for a, _ in todo]

# a FR string should not be claimed by two US strings unless identical refs; check
from collections import Counter
c = Counter(final.values())
dups = [b for b, n in c.items() if n > 1]
print('matched', len(final), 'unmatched', len(unmatched), 'fr dup targets', len(dups))
json.dump({hex(a): hex(b) for a, b in sorted(final.items())}, open('data/derived/align_us_fr.json', 'w', encoding='utf-8'), indent=0)
json.dump([hex(a) for a in sorted(unmatched)], open('data/derived/unmatched_us.json', 'w', encoding='utf-8'), indent=0)
for a in unmatched[:60]:
    if a < 0x170000: continue
    print(hex(a), len(us[hex(a)]['refs']), repr(us[hex(a)]['text'][:60]))
