"""Heuristic: is the 4-byte pointer at position r a genuine reference (not code/graphics bytes)?"""
def trusted(rom, r):
    if r % 4 == 0:
        return True
    if r < 0x160000:
        return False
    b1, b2 = rom[r-1], rom[r-2]
    if (b2, b1) == (0x0F, 0x00): return True          # loadpointer
    if b1 == 0x67: return True                        # preparemsg
    if b1 in (0x08, 0x09):
        prev = int.from_bytes(rom[r-4:r], 'little')
        if 0x08000000 <= prev < 0x0A000000: return True   # consecutive pointers (trainerbattle)
    if 0x5C in rom[max(0, r-6):r]: return True        # trainerbattle first text pointer
    if b1 == 0x9B and 0x1B0000 <= r < 0x1C6000: return True
    if b1 == 0xBD and 0x488000 <= r < 0x48A000: return True
    return False
