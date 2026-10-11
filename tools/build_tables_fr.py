"""Build data/derived/table_translations.json: French names for the fixed-width tables.
Vanilla entries (unchanged by the hack) take the official French name from the FR ROM (read by tables.py);
entries changed by the hack go through data/glossary.json (unknown proper nouns are kept as-is)."""
import json, sys
sys.path.insert(0, 'tools')
from gen3text import encode

t = json.load(open('data/derived/tables.json', encoding='utf-8')); g = json.load(open('data/glossary.json', encoding='utf-8'))
maps = {'pokemon': g['characters'], 'moves': g['moves'], 'abilities': g['abilities'], 'items': g['game_terms'],
        'classes': g['classes'], 'trainers': g['trainers'], 'dexcat': g['dexcat'], 'types': {}}
out, issues = {}, []
for name, tb in t.items():
    width = tb['width']; new = [None] * len(tb['us'])
    for i, (u, f, h) in enumerate(zip(tb['us'], tb['fr'], tb['hack'])):
        if h is None: continue
        if u == h:
            new[i] = None if (name == 'trainers' or not f) else f
        else:
            new[i] = maps[name].get(h) or maps[name].get(h.strip()) or h
        if new[i] is not None and len(encode(new[i], terminate=False)) > width:
            issues.append((name, i, new[i])); new[i] = None
    out[name] = new
json.dump(out, open('data/derived/table_translations.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('tables built', {k: sum(x is not None for x in v) for k, v in out.items()}, 'too long:', issues)
