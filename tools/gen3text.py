"""Gen 3 (FireRed) international text codec."""
import re

CHARS = {
    0x00: ' ', 0x01: 'À', 0x02: 'Á', 0x03: 'Â', 0x04: 'Ç', 0x05: 'È', 0x06: 'É', 0x07: 'Ê', 0x08: 'Ë',
    0x09: 'Ì', 0x0B: 'Î', 0x0C: 'Ï', 0x0D: 'Ò', 0x0E: 'Ó', 0x0F: 'Ô', 0x10: 'Œ', 0x11: 'Ù', 0x12: 'Ú',
    0x13: 'Û', 0x14: 'Ñ', 0x15: 'ß', 0x16: 'à', 0x17: 'á', 0x19: 'ç', 0x1A: 'è', 0x1B: 'é', 0x1C: 'ê',
    0x1D: 'ë', 0x1E: 'ì', 0x20: 'î', 0x21: 'ï', 0x22: 'ò', 0x23: 'ó', 0x24: 'ô', 0x25: 'œ', 0x26: 'ù',
    0x27: 'ú', 0x28: 'û', 0x29: 'ñ', 0x2A: 'º', 0x2B: 'ª', 0x2C: '[er]', 0x2D: '&', 0x2E: '+',
    0x34: '[Lv]', 0x35: '=', 0x36: ';', 0x51: '¿', 0x52: '¡', 0x53: '[PK]', 0x54: '[MN]', 0x55: '[PO]',
    0x56: '[Ke]', 0x57: '[BL]', 0x58: '[OC]', 0x59: '[K]', 0x5A: 'Í', 0x5B: '%', 0x5C: '(', 0x5D: ')',
    0x68: 'â', 0x6F: 'í', 0x79: '[U]', 0x7A: '[D]', 0x7B: '[L]', 0x7C: '[R]', 0x7D: '*', 0x84: '[e]',
    0x85: '<', 0x86: '>', 0xA0: '[re]',
    0xAB: '!', 0xAC: '?', 0xAD: '.', 0xAE: '-', 0xAF: '·', 0xB0: '…', 0xB1: '“', 0xB2: '”', 0xB3: '‘',
    0xB4: "'", 0xB5: '♂', 0xB6: '♀', 0xB7: '$', 0xB8: ',', 0xB9: '×', 0xBA: '/', 0xEF: '▶', 0xF0: ':',
    0xF1: 'Ä', 0xF2: 'Ö', 0xF3: 'Ü', 0xF4: 'ä', 0xF5: 'ö', 0xF6: 'ü', 0xF7: '[UP]', 0xF8: '[DOWN]', 0xF9: '[LEFT]',
}
for i, c in enumerate('0123456789'):
    CHARS[0xA1 + i] = c
for i, c in enumerate('ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
    CHARS[0xBB + i] = c
for i, c in enumerate('abcdefghijklmnopqrstuvwxyz'):
    CHARS[0xD5 + i] = c
REV = {v: k for k, v in CHARS.items()}
REV['’'] = 0xB4
REV['\u00a0'] = 0x00

# 0xFC extended control code -> number of parameter bytes
FC_LEN = {0x01: 1, 0x02: 1, 0x03: 1, 0x04: 3, 0x05: 1, 0x06: 1, 0x07: 0, 0x08: 1, 0x09: 0, 0x0A: 0,
          0x0B: 2, 0x0C: 1, 0x0D: 1, 0x0E: 1, 0x0F: 0, 0x10: 2, 0x11: 1, 0x12: 1, 0x13: 1, 0x14: 1,
          0x15: 0, 0x16: 0, 0x17: 0, 0x18: 0}

TERM = 0xFF


def decode(data: bytes, pos: int = 0, maxlen: int = 4000):
    """Decode a string at pos. Returns (text, end_pos_after_terminator) or (None, None) if invalid."""
    out = []
    i = pos
    end = min(len(data), pos + maxlen)
    while i < end:
        b = data[i]
        if b == TERM:
            return ''.join(out), i + 1
        if b == 0xFE:
            out.append('\\n'); i += 1
        elif b == 0xFA:
            out.append('\\l'); i += 1
        elif b == 0xFB:
            out.append('\\p'); i += 1
        elif b == 0xFC:
            if i + 1 >= end: return None, None
            sub = data[i + 1]
            n = FC_LEN.get(sub)
            if n is None: return None, None
            params = data[i + 2:i + 2 + n]
            if len(params) < n: return None, None
            out.append('[FC' + ''.join(' %02X' % x for x in (sub, *params)) + ']')
            i += 2 + n
        elif b == 0xFD:
            if i + 1 >= end: return None, None
            out.append('[FD %02X]' % data[i + 1]); i += 2
        elif b in CHARS:
            out.append(CHARS[b]); i += 1
        else:
            return None, None
    return None, None


_tok = re.compile(r'\\n|\\l|\\p|\[FC(?: [0-9A-Fa-f]{2})+\]|\[FD [0-9A-Fa-f]{2}\]|\[[A-Za-z]+\]|.', re.S)


def encode(text: str, terminate: bool = True) -> bytes:
    out = bytearray()
    for m in _tok.finditer(text):
        t = m.group(0)
        if t == '\\n': out.append(0xFE)
        elif t == '\\l': out.append(0xFA)
        elif t == '\\p': out.append(0xFB)
        elif t.startswith('[FC'):
            out.append(0xFC); out += bytes(int(x, 16) for x in t[3:-1].split())
        elif t.startswith('[FD'):
            out.append(0xFD); out.append(int(t[4:6], 16))
        elif t in REV:
            out.append(REV[t])
        elif t == '\n':
            out.append(0xFE)
        else:
            raise ValueError('unencodable %r in %r' % (t, text))
    if terminate: out.append(TERM)
    return bytes(out)


def is_texty(s: str) -> bool:
    """Heuristic: does decoded string look like real text?"""
    plain = re.sub(r'\\[nlp]|\[[^\]]*\]', '', s)
    if not plain.strip(): return False
    ascii_letters = sum(1 for c in plain if 'a' <= c <= 'z' or 'A' <= c <= 'Z')
    if ascii_letters == 0: return False
    good = sum(1 for c in plain if c.isalnum() or c in " .,!?'-…:/()\"“”‘$")
    if good < len(plain) * 0.85: return False
    accented = sum(1 for c in plain if c.isalpha() and not ('a' <= c <= 'z' or 'A' <= c <= 'Z'))
    if accented > ascii_letters: return False
    if not re.search(r'[^\W\d_]{2}', plain): return False
    return True
