"""Hilfsfunktionen zum Erzeugen der KFS31-Geometrie-JSON (Scratch, nicht im Repo)."""
import json, math

R = lambda v: round(v, 3)

class Plan:
    def __init__(self, floor, floor_name, source):
        self.d = {"object": "KFS31", "floor": floor, "floor_name": floor_name, "source": source,
                  "walls": [], "openings": [], "rooms": [], "dimensions": [], "notes": [], "unverified": []}
        self.w = {}

    # Wand aus Rechteck der Rohbaukanten (achsparallel): Achse in Längsrichtung, mittig
    def rw(self, wid, x0, y0, x1, y1, typ="interior", direction=None):
        x0, x1 = sorted((x0, x1)); y0, y1 = sorted((y0, y1))
        horiz = (x1 - x0) >= (y1 - y0) if direction is None else direction == "h"
        if horiz:
            yc = (y0 + y1) / 2
            w = {"id": wid, "a": [R(x0), R(yc)], "b": [R(x1), R(yc)], "thickness": R(y1 - y0), "align": "center", "type": typ}
        else:
            xc = (x0 + x1) / 2
            w = {"id": wid, "a": [R(xc), R(y0)], "b": [R(xc), R(y1)], "thickness": R(x1 - x0), "align": "center", "type": typ}
        self._add(w); return w

    # Wand über Achse a->b (beliebige Richtung)
    def aw(self, wid, a, b, t, align="left", typ="exterior"):
        w = {"id": wid, "a": [R(a[0]), R(a[1])], "b": [R(b[0]), R(b[1])], "thickness": R(t), "align": align, "type": typ}
        self._add(w); return w

    def _add(self, w):
        assert w["id"] not in self.w, w["id"]
        self.d["walls"].append(w); self.w[w["id"]] = w

    # Öffnung: pos = Koordinate (x bzw. y, bei Schrägwand Abstand ab a) des Öffnungsanfangs
    def op(self, oid, wid, typ, pos, width, hinge=None, side=None, absolute=True):
        w = self.w[wid]
        a, b = w["a"], w["b"]
        if absolute:
            if abs(b[1] - a[1]) < 1e-9:   # horizontal
                off = (pos - a[0]) if b[0] > a[0] else (a[0] - pos - width)
            elif abs(b[0] - a[0]) < 1e-9:  # vertikal
                off = (pos - a[1]) if b[1] > a[1] else (a[1] - pos - width)
            else:
                raise ValueError("absolute Lage nur bei achsparallelen Wänden")
        else:
            off = pos
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        assert -1e-6 <= off and off + width <= L + 1e-6, (oid, off, width, L)
        o = {"id": oid, "wall": wid, "type": typ, "offset": R(off), "width": R(width)}
        if typ == "door":
            o["hinge"] = hinge or "start"; o["side"] = side or "left"
        self.d["openings"].append(o); return o

    def room(self, name, poly, area=None, **kw):
        r = {"name": name, "polygon": [[R(x), R(y)] for x, y in poly]}
        if area is not None: r["area_stated"] = area
        r.update(kw); self.d["rooms"].append(r); return r

    def dim(self, a, b, off, label=None):
        d = {"a": [R(a[0]), R(a[1])], "b": [R(b[0]), R(b[1])], "offset": off}
        if label: d["label"] = label
        self.d["dimensions"].append(d)

    def chain(self, pts, axis, base, off):
        """Maßkette entlang x (axis='x', base=y) oder y (axis='y', base=x)."""
        for p, q in zip(pts, pts[1:]):
            if axis == "x": self.dim((p, base), (q, base), off)
            else: self.dim((base, p), (base, q), off)

    def note(self, pos, text, **kw):
        n = {"pos": [R(pos[0]), R(pos[1])], "text": text}; n.update(kw); self.d["notes"].append(n)

    def unv(self, pos, text, short=None):
        u = {"pos": [R(pos[0]), R(pos[1])], "text": text}
        if short is not None: u["short"] = short
        self.d["unverified"].append(u)

    def save(self, path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.d, f, ensure_ascii=False, indent=1)
            f.write("\n")

def offset_poly(pts, d):
    """Polylinie (offen) um d nach links (bzgl. Laufrichtung) parallel verschieben, Ecken geschnitten."""
    segs = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        L = math.hypot(x1 - x0, y1 - y0); nx, ny = -(y1 - y0) / L, (x1 - x0) / L
        segs.append(((x0 + nx * d, y0 + ny * d), (x1 + nx * d, y1 + ny * d)))
    out = [segs[0][0]]
    for (p1, p2), (q1, q2) in zip(segs, segs[1:]):
        out.append(intersect(p1, p2, q1, q2))
    out.append(segs[-1][1]); return out

def intersect(p1, p2, q1, q2):
    x1, y1 = p1; x2, y2 = p2; x3, y3 = q1; x4, y4 = q2
    den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
    return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))

def area(poly):
    return abs(sum(poly[i][0] * poly[i - 1][1] - poly[i - 1][0] * poly[i][1] for i in range(len(poly)))) / 2
