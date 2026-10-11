"""Official French texts for a few vanilla strings the automatic US/FR alignment missed.
They are read from the user's FR ROM by table index (never stored in the repo).
Output: data/derived/official_extra.json  {hack_string_id: french_text}"""
import json, sys
sys.path.insert(0, 'tools')
from gen3text import decode
h = open('roms/hack.gba', 'rb').read(); fr = open('roms/fr.gba', 'rb').read()
P = lambda rom, o: int.from_bytes(rom[o:o+4], 'little') - 0x08000000
out = {}
# item descriptions: (hack item table, FR item table), stride 44, desc pointer at +20
ITEM_TARGETS = {0x3d51b4, 0x3d87ab, 0x3d8a14, 0x3d8a66, 0x3d8ebd, 0x3d925f}
for i in range(375):
    p = P(h, 0x3DB028 + 44*i + 20)
    if p in ITEM_TARGETS: out[hex(p)] = decode(fr, P(fr, 0x3D3324 + 44*i + 20))[0]
# move descriptions: hack table 0x4886E8, FR table 0x47E7DC (4-byte pointers)
MOVE_TARGETS = {0x4829c9, 0x482e45, 0x4834ed, 0x4852b8, 0x485d30, 0x48640b, 0x48854f, 0x4886a1}
for i in range(354):
    p = P(h, 0x4886E8 + 4*i)
    if p in MOVE_TARGETS: out[hex(p)] = decode(fr, P(fr, 0x47E7DC + 4*i))[0]
# ability descriptions: hack table 0x24FB08, FR table 0x249F58
for i in range(78):
    p = P(h, 0x24FB08 + 4*i)
    if p == 0x24f438: out[hex(p)] = decode(fr, P(fr, 0x249F58 + 4*i))[0]
json.dump(out, open('data/derived/official_extra.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('official extras:', len(out))
