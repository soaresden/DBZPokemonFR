"""Classify hack strings: unchanged vanilla (reuse official FR) vs hack-specific (translate)."""
import json, re, sys, difflib
from collections import defaultdict
sys.path.insert(0, 'tools')
from gen3text import decode

us = json.load(open('data/derived/us.json', encoding='utf-8')); fr = json.load(open('data/derived/fr.json', encoding='utf-8'))
hk = json.load(open('data/derived/hack.json', encoding='utf-8')); al = json.load(open('data/derived/align_us_fr.json', encoding='utf-8'))

us_by_text = defaultdict(list)
for k, v in us.items(): us_by_text[v['text']].append(k)

def fr_of(us_key):
    b = al.get(us_key)
    return fr[b]['text'] if b else None

def words(t):
    return set(re.findall(r'[A-Za-z]{3,}', t.lower()))

# inverted index for fuzzy lookup
idx = defaultdict(set)
for k, v in us.items():
    for w in words(v['text']): idx[w].add(k)

def closest_vanilla(text, exclude_same=True):
    ws = words(text)
    if not ws: return None, 0
    cnt = defaultdict(int)
    for w in ws:
        if len(idx[w]) > 400: continue
        for k in idx[w]: cnt[k] += 1
    best = sorted(cnt.items(), key=lambda x: -x[1])[:8]
    bk, br = None, 0
    for k, _ in best:
        r = difflib.SequenceMatcher(None, text, us[k]['text']).ratio()
        if r > br: bk, br = k, r
    return bk, br

result = {}
stats = defaultdict(int)
for k, v in hk.items():
    t = v['text']
    entry = {'text': t, 'end': v['end'], 'refs': v['refs']}
    if k in us and us[k]['text'] == t:
        entry['kind'] = 'vanilla_same_addr'; entry['us'] = k
    elif t in us_by_text:
        entry['kind'] = 'vanilla_relocated'; entry['us'] = us_by_text[t][0]
    else:
        entry['kind'] = 'hack'
        # reference: same address vanilla string if similar, else fuzzy
        ref = None; ratio = 0
        if k in us:
            ratio = difflib.SequenceMatcher(None, t, us[k]['text']).ratio(); ref = k
        if ratio < 0.6:
            bk, br = closest_vanilla(t)
            if br > ratio: ref, ratio = bk, br
        if ref and ratio >= 0.45:
            entry['ref_us'] = ref; entry['ref_ratio'] = round(ratio, 2)
    if entry['kind'] != 'hack':
        f = fr_of(entry['us'])
        if f is None:
            entry['kind'] += '_nofr'
        else:
            entry['fr'] = f
    stats[entry['kind']] += 1
    result[k] = entry

json.dump(result, open('data/derived/hack_classified.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
for k, n in stats.items(): print(k, n)
hs = [e for e in result.values() if e['kind'] == 'hack']
print('hack strings to translate:', len(hs), 'chars', sum(len(e['text']) for e in hs),
      'words', sum(len(e['text'].split()) for e in hs), 'with ref', sum(1 for e in hs if 'ref_us' in e))
