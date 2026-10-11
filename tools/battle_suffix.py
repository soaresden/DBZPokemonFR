"""French battle-name suffix: "VEGETA ennemi" / "GOKU sauvage" instead of the US prefix "Foe VEGETA".

The US engine copies a prefix ("Foe " for trainers, "" for wild) before the enemy nickname.
We redirect the prefix pointers to two distinct empty strings (sentinels), then hook the
shared nickname tail so that, when a sentinel is seen, the nickname is copied first and the
French suffix is handed to the main copy loop.

The machine code is stored pre-assembled in battle_suffix_template.json (no ARM assembler needed
to build). Run `python tools/battle_suffix.py` to regenerate the template (needs arm-none-eabi-as).
"""
import os, subprocess, tempfile, sys, json
sys.path.insert(0, os.path.dirname(__file__))
from gen3text import encode

GetMonData, StringGetEnd10, StringAppend = 0x0803FBE9, 0x08008D29, 0x08008DA5
gBattleTypeFlags = 0x02022B4C
FOE_LITS = [0xd7b7c, 0xd7ca4, 0xd7d18, 0xd7d8c, 0xd7e00, 0xd7e74, 0xd82c0]
WILD_LITS = [0xd7b78, 0xd7ca0, 0xd7d14, 0xd7d88, 0xd7dfc, 0xd7e70, 0xd82bc]
CASE8_FOE_LIT = 0xd8554
TEMPLATE = os.path.join(os.path.dirname(__file__), 'battle_suffix_template.json')
MARKERS = {'E_FOE': 0x0EE10001, 'E_WILD': 0x0EE10002, 'SUF_FOE': 0x0EE10003, 'SUF_WILD': 0x0EE10004}


def asm_source(E_FOE, E_WILD, SUF_FOE, SUF_WILD):
    """THUMB source; the four arguments are full 0x08xxxxxx addresses."""
    return f"""
    .syntax unified
    .thumb
    .text
    .align 2
stub7:                          @ entered from 0xd82aa: r0 = enemy mon, r4 = prefix end
    movs r1, #2
    mov r2, sp
    ldr r3, =0x{GetMonData:08x}
    bl call_r3
    ldr r0, =0x{E_FOE:08x}
    cmp r4, r0
    beq s7_foe
    ldr r0, =0x{E_WILD:08x}
    cmp r4, r0
    beq s7_wild
    ldr r0, =0x080d82e5        @ original continuation (StringGetEnd10, r4=sp, main loop)
    bx r0
s7_foe:
    ldr r4, =0x{SUF_FOE:08x}
    b s7_common
s7_wild:
    ldr r4, =0x{SUF_WILD:08x}
s7_common:
    mov r0, sp
    ldr r3, =0x{StringGetEnd10:08x}
    bl call_r3
    mov r1, sp
s7_loop:
    ldrb r0, [r1]
    cmp r0, #0xff
    beq s7_done
    mov r2, r8
    strb r0, [r2, r6]
    adds r6, #1
    adds r1, #1
    b s7_loop
s7_done:
    ldr r0, =0x080d8383        @ main copy loop copies the suffix (r4)
    bx r0

stub8:                          @ entered from 0xd856c: r0 = enemy mon, r6 = dst
    movs r1, #2
    mov r2, sp
    ldr r3, =0x{GetMonData:08x}
    bl call_r3
    mov r0, sp
    ldr r3, =0x{StringGetEnd10:08x}
    bl call_r3
    adds r0, r6, #0
    mov r1, sp
    ldr r3, =0x{StringAppend:08x}
    bl call_r3
    ldr r0, =0x{gBattleTypeFlags:08x}
    ldr r0, [r0]
    movs r1, #8
    ands r0, r1
    ldr r1, =0x{SUF_WILD:08x}
    beq s8_app
    ldr r1, =0x{SUF_FOE:08x}
s8_app:
    adds r0, r6, #0
    ldr r3, =0x{StringAppend:08x}
    bl call_r3
    ldr r0, =0x080d86af
    bx r0

call_r3:
    bx r3
    .ltorg
"""


def _run_as(src, d):
    open(f'{d}/a.s', 'w').write(src)
    subprocess.run(['arm-none-eabi-as', '-mthumb', '-mcpu=arm7tdmi', f'{d}/a.s', '-o', f'{d}/a.o'], check=True)


def assemble(src):
    with tempfile.TemporaryDirectory() as d:
        _run_as(src, d)
        subprocess.run(['arm-none-eabi-objcopy', '-O', 'binary', '-j', '.text', f'{d}/a.o', f'{d}/a.bin'], check=True)
        return open(f'{d}/a.bin', 'rb').read()


def find_symbol(src, name):
    with tempfile.TemporaryDirectory() as d:
        _run_as(src, d)
        out = subprocess.run(['arm-none-eabi-nm', f'{d}/a.o'], capture_output=True, text=True, check=True).stdout
        for line in out.splitlines():
            parts = line.split()
            if parts[-1] == name: return int(parts[0], 16)
    raise KeyError(name)


def make_template():
    """Assemble once with marker constants and store bytes + stub8 offset."""
    src = asm_source(*MARKERS.values())
    code = assemble(src); off8 = find_symbol(src, 'stub8')
    for name, m in MARKERS.items():
        assert code.count(m.to_bytes(4, 'little')) >= 1, name
    json.dump({'code': code.hex(), 'stub8': off8}, open(TEMPLATE, 'w'), indent=1)
    return code, off8


def build_code(e_foe, e_wild, suf_foe, suf_wild):
    t = json.load(open(TEMPLATE))
    code = bytes.fromhex(t['code'])
    for m, val in zip(MARKERS.values(), (e_foe, e_wild, suf_foe, suf_wild)):
        code = code.replace(m.to_bytes(4, 'little'), val.to_bytes(4, 'little'))
    return code, t['stub8']


def patch(rom, orig, alloc):
    def expect(pos, hexbytes):
        assert orig[pos:pos + len(hexbytes) // 2].hex() == hexbytes, (hex(pos), orig[pos:pos+8].hex())
    expect(0xd82aa, '02216a46')          # movs r1,#2 ; mov r2,sp   (then bl GetMonData ; b)
    expect(0xd856c, '02216a46')          # same sequence in the StringAppend-based variant
    for L in FOE_LITS + [CASE8_FOE_LIT]: assert int.from_bytes(orig[L:L+4], 'little') == 0x083FD55B
    for L in WILD_LITS: assert int.from_bytes(orig[L:L+4], 'little') == 0x083FD555

    suf_foe, suf_wild = encode(' ennemi'), encode(' sauvage')
    data = b'\xff\xff' + suf_foe + suf_wild
    base = alloc(len(data) + 400)
    base = (base + 3) & ~3
    E_FOE, E_WILD = base, base + 1
    SUF_FOE = base + 2; SUF_WILD = SUF_FOE + len(suf_foe)
    code_at = (base + len(data) + 3) & ~3
    A = lambda x: 0x08000000 | x
    code, stub8_off = build_code(A(E_FOE), A(E_WILD), A(SUF_FOE), A(SUF_WILD))
    assert code_at + len(code) <= base + len(data) + 400
    rom[base:base + len(data)] = data
    rom[code_at:code_at + len(code)] = code
    for L in FOE_LITS + [CASE8_FOE_LIT]: rom[L:L+4] = A(E_FOE).to_bytes(4, 'little')
    for L in WILD_LITS: rom[L:L+4] = A(E_WILD).to_bytes(4, 'little')
    # hook 1 (0xd82aa..0xd82b3): nop ; ldr r1,[pc,#0] ; bx r1 ; .word stub7|1
    rom[0xd82aa:0xd82b4] = bytes.fromhex('c046' '0049' '0847') + A(code_at | 1).to_bytes(4, 'little')
    # hook 2 (0xd856c..0xd8573): ldr r1,[pc,#0] ; bx r1 ; .word stub8|1
    rom[0xd856c:0xd8574] = bytes.fromhex('0049' '0847') + A((code_at + stub8_off) | 1).to_bytes(4, 'little')
    return {'data': hex(base), 'code': hex(code_at), 'stub8': hex(code_at + stub8_off), 'code_len': len(code)}


if __name__ == '__main__':
    code, off8 = make_template()
    print('template written:', len(code), 'bytes, stub8 at +%d' % off8)
