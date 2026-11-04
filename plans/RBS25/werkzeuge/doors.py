import math, sys
sys.path.insert(0, '/tmp/rbs25/tools')
from ex import *
def onseg(p, a, b, tol=0.01):
    L = math.dist(a, b)
    if L < 1e-6: return False
    t = ((p[0]-a[0])*(b[0]-a[0]) + (p[1]-a[1])*(b[1]-a[1])) / L**2
    if t < -0.01 or t > 1.01: return False
    q = (a[0]+t*(b[0]-a[0]), a[1]+t*(b[1]-a[1]))
    return math.dist(p, q) < tol
def circle3(a, b, c):
    ax, ay = a; bx, by = b; cx, cy = c
    d = 2*(ax*(by-cy) + bx*(cy-ay) + cx*(ay-by))
    if abs(d) < 1e-9: return None
    ux = ((ax*ax+ay*ay)*(by-cy) + (bx*bx+by*by)*(cy-ay) + (cx*cx+cy*cy)*(ay-by))/d
    uy = ((ax*ax+ay*ay)*(cx-bx) + (bx*bx+by*by)*(ax-cx) + (cx*cx+cy*cy)*(bx-ax))/d
    return (ux, uy), math.dist((ux, uy), a)
def chains(segs, tol=0.004):
    segs = [[s[1], s[2]] for s in segs]
    used = [False]*len(segs); out = []
    for i, s in enumerate(segs):
        if used[i]: continue
        used[i] = True; ch = list(s); grow = True
        while grow:
            grow = False
            for j, t in enumerate(segs):
                if used[j]: continue
                for end in (0, 1):
                    p = ch[-1] if end else ch[0]
                    for k in (0, 1):
                        if math.dist(p, t[k]) < tol:
                            q = t[1-k]
                            if end: ch.append(q)
                            else: ch.insert(0, q)
                            used[j] = True; grow = True; break
                    if used[j]: break
        out.append(ch)
    return out
def fit(pts):
    import numpy as np
    A = np.array([[2*p[0], 2*p[1], 1] for p in pts]); bb = np.array([p[0]**2+p[1]**2 for p in pts])
    (cx, cy, c), *_ = np.linalg.lstsq(A, bb, rcond=None)
    return (cx, cy), math.sqrt(c + cx*cx + cy*cy)
def best_arc(ch, tol=0.012):
    n = len(ch); best = None
    for i in range(n):
        for j in range(n-1, i+4, -1):
            if best and j - i <= best[1] - best[0]: break
            c = circle3(ch[i], ch[(i+j)//2], ch[j])
            if not c: continue
            C, r = c
            if all(abs(math.dist(C, p) - r) < tol for p in ch[i:j+1]):
                best = (i, j, C, r); break
    return best
def find_doors(fl, minr=0.45, maxr=1.4):
    S = strokes(fl)
    short = [s for s in S if math.dist(s[1], s[2]) < 0.2]
    doors = []
    for ch in chains(short, 0.01):
        if len(ch) < 6: continue
        b = best_arc(ch)
        if not b: continue
        i, j, C, r = b
        sub = ch[i:j+1]
        while len(sub) > 5:
            C, r = fit(sub)
            res = [abs(math.dist(C, p) - r) for p in sub]
            k = max(range(len(sub)), key=lambda q: res[q])
            if res[k] < 0.004: break
            if k == 0: sub = sub[1:]
            elif k == len(sub)-1: sub = sub[:-1]
            else: break
        # Angel auf achsparallele Ecke einrasten
        P1, P2 = sub[0], sub[-1]
        cand = [(P1[0], P2[1]), (P2[0], P1[1])]
        H = min(cand, key=lambda q: math.dist(q, C))
        if math.dist(H, C) > 0.12: continue
        C = H; r = (math.dist(H, P1) + math.dist(H, P2)) / 2
        if not (minr <= r <= maxr): continue
        a1 = math.atan2(sub[0][1]-C[1], sub[0][0]-C[0]); a2 = math.atan2(sub[-1][1]-C[1], sub[-1][0]-C[0])
        sweep = abs((a2 - a1 + math.pi) % (2*math.pi) - math.pi)
        if abs(sweep - math.pi/2) > 0.25: continue
        doors.append(dict(hinge=C, p1=P1, p2=P2, r=r))
    out = []
    for d in doors:
        if any(math.dist(d['hinge'], o['hinge']) < 0.08 and abs(d['r']-o['r']) < 0.08 for o in out): continue
        out.append(d)
    return out
if __name__ == '__main__':
    for d in find_doors(sys.argv[1]):
        print({k: (tuple(round(x, 3) for x in v) if isinstance(v, tuple) else (round(v, 3) if isinstance(v, float) else v)) for k, v in d.items()})
