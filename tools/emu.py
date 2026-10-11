"""Headless mGBA runner: python3 tools/emu.py rom out_prefix script
script: comma-separated steps like  w300 (wait frames), a, b, start, select, up/down/left/right (press 8 frames), s (screenshot)"""
import sys, mgba.core, mgba.image, mgba.log
mgba.log.silence()
rom, prefix, script = sys.argv[1], sys.argv[2], sys.argv[3]
state_in = sys.argv[4] if len(sys.argv) > 4 and sys.argv[4] != '-' else None
state_out = sys.argv[5] if len(sys.argv) > 5 else None
core = mgba.core.load_path(rom)
w, h = core.desired_video_dimensions()
img = mgba.image.Image(w, h)
core.set_video_buffer(img)
core.reset()
if state_in:
    core.load_raw_state(open(state_in, 'rb').read())
KEYS = {'a': 0, 'b': 1, 'select': 2, 'start': 3, 'right': 4, 'left': 5, 'up': 6, 'down': 7, 'r': 8, 'l': 9}
shot = 0
def frames(n):
    for _ in range(n): core.run_frame()
for step in script.split(','):
    step = step.strip()
    if not step: continue
    if step[0] == 'w' and step[1:].isdigit():
        frames(int(step[1:]))
    elif step == 's':
        shot += 1
        img.to_pil().convert('RGB').save(f'{prefix}_{shot:02d}.png')
    elif '*' in step and step.split('*')[0] in KEYS:
        k, n = step.split('*'); core.set_keys(KEYS[k]); frames(int(n)); core.clear_keys(KEYS[k]); frames(4)
    elif step in KEYS:
        core.set_keys(KEYS[step]); frames(8); core.clear_keys(KEYS[step]); frames(8)
    else:
        raise SystemExit('bad step ' + step)
if state_out:
    st = core.save_raw_state()
    open(state_out, 'wb').write(bytes(st))
print('done', shot, 'screenshots')
