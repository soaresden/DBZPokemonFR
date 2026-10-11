"""Smoke test in a headless mGBA (Linux/WSL: pip install mgba pillow).
Boots roms/hack_fr.gba to the title screen, then replays saved states and stores screenshots in tests/out/.
    python tests/smoke.py"""
import os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT)
ROM = 'roms/hack_fr.gba'; OUT = 'tests/out'; os.makedirs(OUT, exist_ok=True)
EMU = [sys.executable, 'tools/emu.py', ROM]
try:
    import mgba.core  # noqa
except ImportError:
    sys.exit('mgba non installé (pip install mgba) — tester à la main dans mGBA')

def emu(prefix, script, state=None):
    args = EMU + [f'{OUT}/{prefix}', script] + ([state] if state else [])
    subprocess.run(args, check=True, capture_output=True)

from PIL import Image
emu('boot', 'w2400,s')
px = Image.open(f'{OUT}/boot_01.png').convert('RGB').getpixel((10, 2))
ok = px[0] > 200 and px[1] < 150
print('boot écran titre :', 'OK' if ok else 'ÉCHEC', px)
# scenarios from saved states (bedroom, route before Brief's event, start of the rival battle)
emu('route_brief', 'up*16,w60,a,w200,' + ','.join(['w250,s,a,w60'] * 5), 'tests/states/w7.bin')
emu('rival_battle', ','.join(['a,w200'] * 6) + ',s,' + ','.join(['a,w160,s'] * 10), 'tests/states/w13.bin')
print(f'captures dans {OUT}/ : vérifier route_brief_* (dialogue de Brief en FR) et rival_battle_* (« VEGETA ennemi utilise … »)')
sys.exit(0 if ok else 1)
