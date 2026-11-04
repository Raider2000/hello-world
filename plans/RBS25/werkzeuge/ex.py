"""Extraktion der Vektoren aus dem Aufteilungsplan 2014 (M 1:100)."""
import pymupdf, json
from shapely.geometry import Polygon
K = 72/25.4*10   # pt pro m bei 1:100 = 28.3465
PDF = '/home/user/hello-world/plans/RBS25/quelle/20140801-Aufteilungsplan_Grundrisse_RB25.pdf'
FLOORS = {  # clip (pt), Ursprung (pt): linke untere Rohbau-Außenecke Hauptbaukörper
 'OG1': dict(clip=(140, 120, 800, 520), o=(241.2, 491.88)),
 'OG2': dict(clip=(1090, 120, 1750, 520), o=(1192.44, 494.16)),
 'DG':  dict(clip=(2030, 120, 2700, 520), o=(2104.44, 495.0)),
 'EG':  dict(clip=(170, 940, 900, 1360), o=(271.8, 1318.56)),
 'KG':  dict(clip=(1440, 940, 2100, 1360), o=(1521.06, 1318.56)),
}
_page = None
def page():
    global _page
    if _page is None:
        _page = pymupdf.open(PDF)[0]
    return _page
def tom(fl, p):
    ox, oy = FLOORS[fl]['o']
    return (round((p[0]-ox)/K, 4), round((oy-p[1])/K, 4))
def drawings(fl):
    clip = pymupdf.Rect(*FLOORS[fl]['clip'])
    return [d for d in page().get_drawings() if clip.contains(d['rect'])]
def pts_of(dr):
    pts = []
    for it in dr['items']:
        if it[0] == 'l': pts += [it[1], it[2]]
        elif it[0] == 're': r = it[1]; pts += [r.tl, r.tr, r.br, r.bl]
        elif it[0] == 'qu': q = it[1]; pts += [q.ul, q.ur, q.lr, q.ll]
        else: pts += [it[1], it[-1]]
    out = []
    for q in pts:
        t = (q.x, q.y)
        if not out or abs(out[-1][0]-t[0])+abs(out[-1][1]-t[1]) > 1e-3: out.append(t)
    if len(out) > 1 and abs(out[0][0]-out[-1][0])+abs(out[0][1]-out[-1][1]) < 1e-3: out.pop()
    return out
def subpaths(dr):
    rings, cur = [], []
    for it in dr['items']:
        if it[0] == 're':
            r = it[1]; rings.append([r.tl, r.tr, r.br, r.bl]); continue
        if it[0] == 'qu':
            q = it[1]; rings.append([q.ul, q.ur, q.lr, q.ll]); continue
        a, b = it[1], it[-1]
        if cur and abs(cur[-1].x - a.x) + abs(cur[-1].y - a.y) > 1e-3:
            rings.append(cur); cur = []
        if not cur: cur = [a]
        cur.append(b)
    if cur: rings.append(cur)
    out = []
    for r in rings:
        pts = []
        for q in r:
            t = (q.x, q.y)
            if not pts or abs(pts[-1][0]-t[0])+abs(pts[-1][1]-t[1]) > 1e-3: pts.append(t)
        if len(pts) > 1 and abs(pts[0][0]-pts[-1][0])+abs(pts[0][1]-pts[-1][1]) < 1e-3: pts.pop()
        if len(pts) >= 3: out.append(pts)
    return out
def fills(fl):
    """Füllflächen: (Farbe, [Ring, ...]) – mehrere Teilpfade, Even-Odd."""
    res = []
    for d in drawings(fl):
        if d['type'] not in ('f', 'fs') or not d.get('fill'): continue
        col = tuple(round(c, 2) for c in d['fill'])
        rings = [[tom(fl, p) for p in r] for r in subpaths(d)]
        if rings:
            res.append((col, rings))
    return res
FILTER = {}  # optional je Geschoss: Shapely-Geometrie, nur Striche darin
_scache = {}
def strokes(fl):
    key = (fl, id(FILTER.get(fl)))
    if key in _scache:
        return _scache[key]
    res = _strokes(fl)
    if FILTER.get(fl) is not None:
        from shapely.geometry import Point
        from shapely.prepared import prep
        g = prep(FILTER[fl])
        res = [s for s in res if g.contains(Point(s[1])) and g.contains(Point(s[2]))]
    _scache[key] = res
    return res
def _strokes(fl):
    res = []
    for d in drawings(fl):
        if d['type'] != 's': continue
        for it in d['items']:
            if it[0] == 'l':
                res.append((round(d['width'], 2), tom(fl, (it[1].x, it[1].y)), tom(fl, (it[2].x, it[2].y))))
    return res
GREY, RED, YEL, NEIGH = (0.45,0.45,0.45), (1.0,0.55,0.55), (1.0,1.0,0.33), (0.84,0.84,0.84)
def words(fl):
    clip = pymupdf.Rect(*FLOORS[fl]['clip'])
    out = []
    for b in page().get_text('dict')['blocks']:
        for l in b.get('lines', []):
            t = ' '.join(s['text'] for s in l['spans']).strip()
            r = pymupdf.Rect(l['bbox'])
            if t and clip.contains(r):
                out.append((t, tom(fl, ((r.x0+r.x1)/2, (r.y0+r.y1)/2)), l['dir']))
    return out
