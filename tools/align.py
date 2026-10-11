"""Align vanilla US strings with vanilla FR strings (same ROM structure, same order)."""
import json, re, sys
import numpy as np

CTRL = re.compile(r'\[FD [0-9A-F]{2}\]|\[FC(?: [0-9A-F]{2})+\]|[0-9]+')

def sig(t):
    return tuple(CTRL.findall(t))

def plain_len(t):
    return len(re.sub(r'\\[nlp]|\[[^\]]*\]', '', t))

def align(us, fr, band=600):
    A = [(int(k, 16), v['text']) for k, v in us.items()]; A.sort()
    B = [(int(k, 16), v['text']) for k, v in fr.items()]; B.sort()
    sa = [sig(t) for _, t in A]; sb = [sig(t) for _, t in B]
    la = [plain_len(t) for _, t in A]; lb = [plain_len(t) for _, t in B]
    n, m = len(A), len(B)
    GAP = -2
    # banded DP: score[i][j] for i in 0..n, j in i-band..i+band
    W = 2 * band + 1
    NEG = -10**9
    S = np.full((n + 1, W), NEG, dtype=np.int32)
    P = np.zeros((n + 1, W), dtype=np.int8)  # 0 diag,1 up (gap in B),2 left (gap in A)
    def jj(i, j): return j - i + band
    S[0, jj(0, 0)] = 0
    for j in range(1, min(band, m) + 1):
        S[0, jj(0, j)] = GAP * j; P[0, jj(0, j)] = 2
    for i in range(1, n + 1):
        lo = max(0, i - band); hi = min(m, i + band)
        for j in range(lo, hi + 1):
            best = NEG; arg = 0
            if j > 0 and abs(j - 1 - (i - 1)) <= band:
                same = sa[i-1] == sb[j-1]
                if same:
                    sc = 3 if sa[i-1] else 1
                    r = (lb[j-1] + 3) / (la[i-1] + 3)
                    sc += 2 if 0.6 <= r <= 2.0 else -2
                else:
                    sc = -6
                v = S[i-1, jj(i-1, j-1)] + sc
                if v > best: best, arg = v, 0
            if abs(j - (i - 1)) <= band:
                v = S[i-1, jj(i-1, j)] + GAP
                if v > best: best, arg = v, 1
            if j > 0 and abs(j - 1 - i) <= band:
                v = S[i, jj(i, j-1)] + GAP
                if v > best: best, arg = v, 2
            S[i, jj(i, j)] = best; P[i, jj(i, j)] = arg
    # traceback
    i, j = n, m; pairs = []
    while i > 0 or j > 0:
        p = P[i, jj(i, j)]
        if i > 0 and j > 0 and p == 0:
            pairs.append((A[i-1][0], B[j-1][0])); i -= 1; j -= 1
        elif i > 0 and (p == 1 or j == 0):
            i -= 1
        else:
            j -= 1
    pairs.reverse()
    return pairs

if __name__ == '__main__':
    us = json.load(open('data/derived/us.json', encoding='utf-8')); fr = json.load(open('data/derived/fr.json', encoding='utf-8'))
    pairs = align(us, fr)
    print(len(pairs), 'pairs of', len(us), len(fr))
    out = {hex(a): hex(b) for a, b in pairs}
    json.dump(out, open('data/derived/align_us_fr.json', 'w', encoding='utf-8'), indent=0)
