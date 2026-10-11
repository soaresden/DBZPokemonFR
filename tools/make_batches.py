"""Build translation batches for hack-specific pointer strings."""
import json, os, re
cl = json.load(open('data/derived/hack_classified.json', encoding='utf-8')); us = json.load(open('data/derived/us.json', encoding='utf-8')); fr = json.load(open('data/derived/fr.json', encoding='utf-8'))
al = json.load(open('data/derived/align_us_fr.json', encoding='utf-8')); t = json.load(open('data/derived/tables.json', encoding='utf-8')); tt = json.load(open('data/derived/table_translations.json', encoding='utf-8'))

ITEM0, ITEMN, ITEMS = 0x3DB028, 375, 44
MOVED0, MOVEDN = 0x4886E8, 354
DEX0, DEXN, DEXS = 0x44E850, 412, 36
ABD0, ABDN = 0x24FB08, 78

def context(refs):
    for r in refs:
        if ITEM0 <= r < ITEM0 + ITEMN * ITEMS and (r - ITEM0) % ITEMS == 20:
            i = (r - ITEM0) // ITEMS; return f"Description de l'objet « {tt['items'][i] or t['items']['hack'][i]} » (menu sac : max 3 lignes de ~28 caractères, séparées par \\n)"
        if MOVED0 <= r < MOVED0 + MOVEDN * 4 and (r - MOVED0) % 4 == 0:
            i = (r - MOVED0) // 4 + 1; return f"Description de l'attaque « {tt['moves'][i] or t['moves']['hack'][i]} » (résumé : max 3 lignes de ~20 caractères, séparées par \\n)"
        if DEX0 <= r < DEX0 + DEXN * DEXS and (r - DEX0) % DEXS == 12:
            i = (r - DEX0) // DEXS; return f"Entrée Pokédex/Scouter de « {tt['pokemon'][i] or t['pokemon']['hack'][i]} » (max 4 lignes de ~40 caractères, séparées par \\n)"
        if ABD0 <= r < ABD0 + ABDN * 4 and (r - ABD0) % 4 == 0:
            i = (r - ABD0) // 4; return f"Description de la capacité spéciale « {tt['abilities'][i] or t['abilities']['hack'][i]} » (1 ligne, max ~24 caractères)"
    return None

items = []
for k, e in cl.items():
    a = int(k, 16)
    if e['kind'] == 'hack' or (e['kind'].endswith('_nofr') and a >= 0x170000 and a < 0x1C6000 and len(e['text']) >= 4):
        it = {'id': k, 'en': e['text']}
        c = context(e['refs'])
        if c: it['contexte'] = c
        if 'ref_us' in e:
            it['en_vanilla'] = us[e['ref_us']]['text']
            b = al.get(e['ref_us'])
            if b: it['fr_vanilla'] = fr[b]['text']
        items.append((a, it))
items.sort()
os.makedirs('batches', exist_ok=True)
SIZE = 90
n = 0
for i in range(0, len(items), SIZE):
    n += 1
    json.dump([it for _, it in items[i:i+SIZE]], open(f'batches/batch_{n:02d}.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(items), 'items in', n, 'batches')
