"""Validate a translated batch: python3 tools/validate.py batches/batch_01.json batches/out_01.json"""
import json, re, sys
sys.path.insert(0, 'tools')
from gen3text import encode

CTRL = re.compile(r'\[FD [0-9A-F]{2}\]|\[FC(?: [0-9A-F]{2})+\]')
MAXLINE = 35

def check(src, out):
    errors = []
    src_by_id = {e['id']: e for e in src}
    out_ids = [o['id'] for o in out]
    if out_ids != [e['id'] for e in src]:
        missing = [e['id'] for e in src if e['id'] not in set(out_ids)]
        extra = [i for i in out_ids if i not in src_by_id]
        errors.append(('*', f'ids mismatch: missing {missing[:5]} extra {extra[:5]}'))
    for o in out:
        i = o['id']; fr = o.get('fr')
        if i not in src_by_id: continue
        en = src_by_id[i]['en']
        if not isinstance(fr, str) or not fr.strip():
            errors.append((i, 'empty')); continue
        if fr == en:
            continue  # verbatim copy (binary garbage / untranslatable fragment): nothing to check
        # INSTRUCTIONS.md rule 6: fixed boxes (item/move/ability descriptions) use \n only, no scrolling
        ctx = src_by_id[i].get('contexte', ''); addr = int(i, 16)
        # fixed boxes never scroll: a source containing \\l or \\p is a normal dialogue even in 0x44-0x49 regions
        scrolls = '\\l' in en or '\\p' in en
        fixed_box = not scrolls and ('séparées par \\n' in ctx or 0x440000 <= addr < 0x490000)
        max_lines = max(3, en.count('\\n') + 1); maxline = MAXLINE
        if scrolls: pass
        elif 0x440000 <= addr < 0x460000: max_lines, maxline = 3, 43          # Pokédex entries
        elif 0x480000 <= addr < 0x490000 or 'attaque' in ctx: max_lines, maxline = 4, 21   # move descriptions
        elif 'objet' in ctx: max_lines, maxline = 4, 44
        elif 'capacité' in ctx: max_lines, maxline = 1, 27
        def well_formed(t):
            st = 0
            for sg in re.split(r'(\\[nlp])', t):
                if sg == '\\p': st = 0
                elif sg == '\\n':
                    if st != 0: return False
                    st = 1
                elif sg == '\\l':
                    if st == 0: return False
                    st = 2
            return True
        if sorted(CTRL.findall(en)) != sorted(CTRL.findall(fr)):
            errors.append((i, f'control codes differ: en {CTRL.findall(en)} fr {CTRL.findall(fr)}'))
        try:
            encode(fr)
        except ValueError as ex:
            errors.append((i, str(ex)))
        if re.search(r'[ÀÂÄÉÈÊËÎÏÔÖÙÛÜÇ]', re.sub('[' + re.escape(''.join(set(en))) + ']', '', fr) if en else fr):
            errors.append((i, 'accented uppercase'))
        if re.search(r'(\\[nlp]){2}', fr):
            errors.append((i, 'consecutive line codes'))
        if fixed_box:
            if re.search(r'\\[lp]', fr):
                errors.append((i, 'fixed box: only \\n allowed'))
            if fr.count('\\n') + 1 > max_lines:
                errors.append((i, f'fixed box: more than {max_lines} lines'))
        elif well_formed(en):
            # structure: after start or \p, first break must be \n; then \l only
            segs = re.split(r'(\\[nlp])', fr)
            state = 0  # 0 first line, 1 second line, 2 scrolling
            for s in segs:
                if s == '\\p': state = 0
                elif s == '\\n':
                    if state != 0: errors.append((i, '\\n not on first line of box'));
                    state = 1
                elif s == '\\l':
                    if state == 0: errors.append((i, '\\l used before \\n'))
                    state = 2
        for line in re.split(r'\\[nlp]', fr):
            plain = re.sub(r'\[[^\]]*\]', '', line)
            if len(plain) > maxline:
                errors.append((i, f'line too long ({len(plain)}): {plain[:40]}'))
        if not en.endswith(('\\p', '\\n', '\\l')) and fr.endswith(('\\p', '\\n', '\\l')):
            errors.append((i, 'trailing line code not in source'))
        if en.endswith('\\p') and not fr.endswith('\\p'):
            errors.append((i, 'source ends with \\p, translation must too'))
    return errors

if __name__ == '__main__':
    src = json.load(open(sys.argv[1], encoding='utf-8')); out = json.load(open(sys.argv[2], encoding='utf-8'))
    errs = check(src, out)
    for e in errs: print(e)
    print(f'{len(errs)} errors, {len(out)} entries')
    sys.exit(1 if errs else 0)
