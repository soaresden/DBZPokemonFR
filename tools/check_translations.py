"""Validate data/translations.json (+ nested) against the English hack strings.
Checks: control codes preserved, encodable characters, no accented capitals, line widths, box structure.
Exit code 1 if any error.  Usage: python tools/check_translations.py [--all]"""
import json, sys
sys.path.insert(0, 'tools')
from validate import check

cl = json.load(open('data/derived/hack_classified.json', encoding='utf-8'))
tr = json.load(open('data/translations.json', encoding='utf-8'))
nested = json.load(open('data/nested_translations.json', encoding='utf-8'))

ITEM0, ITEMN, ITEMS = 0x3DB028, 375, 44
MOVED0, MOVEDN = 0x4886E8, 354
ABD0, ABDN = 0x24FB08, 78

def context(refs):
    for r in refs:
        if ITEM0 <= r < ITEM0 + ITEMN * ITEMS and (r - ITEM0) % ITEMS == 20:
            return "Description de l'objet (séparées par \\n)"
        if MOVED0 <= r < MOVED0 + MOVEDN * 4 and (r - MOVED0) % 4 == 0:
            return "Description de l'attaque (séparées par \\n)"
        if ABD0 <= r < ABD0 + ABDN * 4 and (r - ABD0) % 4 == 0:
            return "Description de la capacité spéciale (séparées par \\n)"
    return ''

src, out, unknown = [], [], []
for k, fr in tr.items():
    e = cl.get(k)
    if e is None: unknown.append(k); continue
    src.append({'id': k, 'en': e['text'], 'contexte': context(e['refs'])}); out.append({'id': k, 'fr': fr})
for k, e in nested.items():
    src.append({'id': k, 'en': e['text']}); out.append({'id': k, 'fr': e['fr']})

errs = check(src, out)
for e in errs[: (None if '--all' in sys.argv else 40)]: print(e)
untranslated = [k for k, e in cl.items() if e['kind'] == 'hack' and k not in tr]
print(f'{len(out)} translations checked, {len(errs)} errors, {len(unknown)} ids not in ROM, '
      f'{len(untranslated)} hack strings untranslated')
sys.exit(1 if errs else 0)
