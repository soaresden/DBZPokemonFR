"""One-command build of the French patch.

    python build.py            full build: roms/us.gba + roms/fr.gba + roms/hack.ips  ->  patch/*.ips
    python build.py --fast     skip extraction/alignment (reuse data/derived), only re-insert text + patch
    python build.py --no-check skip the translation checker (not recommended)

Inputs (not in the repo, see roms/README.md):
    roms/us.gba    Pokemon FireRed USA v1.0 (BPRE)  - base ROM the hack patch applies to
    roms/fr.gba    Pokemon Rouge Feu France (BPRF)   - source of the official French texts
    roms/hack.ips  Dragon Ball Z Team Training V8 (English hack patch)
Outputs:
    roms/hack.gba      English hack (us + hack.ips)
    roms/hack_fr.gba   French hack
    patch/DBZ-Team-Training-V8-FR.ips   patch to apply on roms/us.gba
"""
import os, sys, subprocess, time

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, 'tools'))
ENV = dict(os.environ, PYTHONUTF8='1', PYTHONIOENCODING='utf-8')
PATCH = 'patch/DBZ-Team-Training-V8-FR.ips'


def run(*args, quiet=True):
    t = time.time()
    r = subprocess.run([sys.executable, *args], env=ENV, capture_output=True, text=True, encoding='utf-8')
    if r.returncode:
        print(r.stdout[-3000:]); print(r.stderr[-3000:]); sys.exit(f'FAILED: {" ".join(args)}')
    last = [l for l in r.stdout.strip().splitlines() if l.strip()]
    print(f'  {args[0]:<28} {time.time() - t:5.1f}s  {last[-1][:110] if (last and quiet) else ""}')
    if not quiet: print(r.stdout)


def check_roms():
    need = {'roms/us.gba': b'BPRE', 'roms/fr.gba': b'BPRF'}
    for p, code in need.items():
        if not os.path.exists(p): sys.exit(f'missing {p} (see roms/README.md)')
        if open(p, 'rb').read()[0xAC:0xB0] != code: sys.exit(f'{p}: game code is not {code.decode()}')
    if not os.path.exists('roms/hack.ips'): sys.exit('missing roms/hack.ips (see roms/README.md)')


def main():
    fast = '--fast' in sys.argv
    check_roms()
    os.makedirs('data/derived', exist_ok=True); os.makedirs('patch', exist_ok=True)
    from ips import apply_ips, make_ips
    us = open('roms/us.gba', 'rb').read()
    print('[1] apply English hack patch')
    hack = bytes(apply_ips(bytearray(us), open('roms/hack.ips', 'rb').read()))
    open('roms/hack.gba', 'wb').write(hack)
    if not fast:
        print('[2] extract texts')
        for n in ('us', 'fr', 'hack'):
            run('tools/extract.py', f'roms/{n}.gba', f'data/derived/{n}.json')
        print('[3] align US <-> official FR')
        run('tools/align.py'); run('tools/refine_align.py')
        print('[4] classify hack strings (vanilla / hack-specific)')
        run('tools/classify.py')
        print('[5] fixed tables (names) + official extras')
        run('tools/tables.py'); run('tools/build_tables_fr.py'); run('tools/official_extras.py')
    if '--no-check' not in sys.argv:
        print('[6] check translations')
        run('tools/check_translations.py')
    print('[7] insert French text + code patches')
    run('tools/insert.py')
    print('[8] make IPS')
    fr = open('roms/hack_fr.gba', 'rb').read()
    p = make_ips(us, fr)
    assert bytes(apply_ips(bytearray(us), p)) == fr, 'IPS round-trip failed'
    open(PATCH, 'wb').write(p)
    print(f'  -> {PATCH} ({len(p):,} bytes), round-trip OK')


if __name__ == '__main__':
    main()
