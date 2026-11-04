#!/usr/bin/env python3
"""Erzeugt plans/RBS25/geometrie/<G>.json aus dem Aufteilungsplan 2014 (Vektor-PDF).

Aufruf: python3 build.py <G> [--dry]
Gemeinsames System: m, y nach oben, Ursprung = linke untere Rohbau-Außenecke des
Hauptbaukörpers (Südwestecke an der Brandwand zu Haus Nr. 23). Maßstab 1:100 → 1 m = 28,3465 pt.
"""
import sys, json, math
sys.path.insert(0, '/tmp/rbs25/tools')
from ex import *
from doors import find_doors, chains
from shapely.geometry import Polygon, MultiPolygon, LineString, Point, box
from shapely.ops import unary_union
from cfg import CFG

REPO = '/home/user/hello-world'
DBG = {}
R3 = lambda v: round(v + 0.0, 3)


def P(poly):
    """Ring oder Liste von Ringen (Even-Odd) -> Shapely-Geometrie."""
    if poly and isinstance(poly[0][0], (int, float)):
        return Polygon(poly).buffer(0)
    g = Polygon()
    for r in poly:
        if len(r) >= 3:
            g = g.symmetric_difference(Polygon(r).buffer(0))
    return g.buffer(0)


def polys(g):
    if g.is_empty:
        return []
    if g.geom_type == 'Polygon':
        return [g]
    return [x for x in getattr(g, 'geoms', []) if x.geom_type == 'Polygon']


def close_mitre(g, r):
    return g.buffer(r, join_style=2).buffer(-r, join_style=2)


def short_side(g):
    r = g.minimum_rotated_rectangle
    c = list(r.exterior.coords)
    return min(math.dist(c[0], c[1]), math.dist(c[1], c[2]))


def ring(coords):
    out = []
    for x, y in list(coords)[:-1]:
        p = [R3(x), R3(y)]
        if not out or out[-1] != p:
            out.append(p)
    if len(out) > 1 and out[0] == out[-1]:
        out.pop()
    return out


def fill_holes(g):
    return unary_union([Polygon(p.exterior) for p in polys(g)])


# ------------------------------------------------------------ Wände aus Achsen (für WE05-Übernahme)
def axis_wall_poly(w):
    (ax, ay), (bx, by) = w['a'], w['b']
    L = math.hypot(bx - ax, by - ay)
    ux, uy = (bx - ax) / L, (by - ay) / L
    nx, ny = -uy, ux
    t = w['thickness']
    lo, hi = {'center': (-t / 2, t / 2), 'left': (0, t), 'right': (-t, 0)}[w.get('align', 'center')]
    return Polygon([(ax + nx * lo, ay + ny * lo), (bx + nx * lo, by + ny * lo),
                    (bx + nx * hi, by + ny * hi), (ax + nx * hi, ay + ny * hi)])


_grey_cache = {}


def grey_union(fl):
    if fl not in _grey_cache:
        _grey_cache[fl] = unary_union([P(p) for c, p in fills(fl) if c == GREY]).buffer(0)
    return _grey_cache[fl]


def stacked(g, fl, others=('KG', 'EG', 'OG1', 'OG2'), buf=0.06):
    if g.area < 1e-6:
        return False
    for o in others:
        if o == fl:
            continue
        if g.intersection(grey_union(o).buffer(buf, join_style=2)).area / g.area < 0.6:
            return False
    return True


# ------------------------------------------------------------ WE05 (OG2.json Sanierungszustand)
def load_we05():
    # Stand vor dieser Neuzeichnung (git HEAD a72cce5), nur WE05
    return json.load(open('/tmp/rbs25/OG2_WE05_orig.json', encoding='utf-8'))


def tx_we05(p):
    """Altes OG2-System (Ursprung 0,135 m links der 6,85-m-Kette) -> gemeinsames System."""
    x, y = p
    return [R3(max(0.0, x - 0.010)) if x > 0 else 0.0, R3(y)]


# ------------------------------------------------------------ Hauptroutine
def build(fl):
    cfg = CFG[fl]
    out_unv = list(cfg.get('unverified', []))
    region = cfg.get('we05_region')
    region = Polygon(region) if region else None

    raw = [(c, P(p)) for c, p in fills(fl) if c in (GREY, RED)]
    raw = [(c, g) for c, g in raw if g.area > 0.0015]
    F = fill_holes(close_mitre(unary_union([g for c, g in raw if c == GREY]), 0.8))
    if cfg.get('fp_boxes'):
        F = fill_holes(close_mitre(unary_union([g for c, g in raw if c == GREY]).intersection(
            unary_union([box(*bx) for bx in cfg['fp_boxes']])), 0.8))
    for ex in cfg.get('footprint_add', []):
        F = unary_union([F, Polygon(ex)])
    Fb = F.boundary

    import ex as _ex
    flt = [F.buffer(0.5, join_style=2)] + [box(*bx) for bx in cfg.get('stairs', [])]
    if cfg.get('north'):
        flt.append(box(*cfg['north']))
    _ex.FILTER[fl] = unary_union(flt)
    walls_by_type = {'new': [], 'exterior': [], 'load-bearing': [], 'interior': []}
    balconies, outside = [], []
    for c, g in raw:
        if region is not None:
            g = g.difference(region).buffer(-0.012, join_style=2).buffer(0.012, join_style=2)
            if g.area < 0.004:
                continue
        if c == RED and short_side(g) > 0.6 and g.area / max(g.minimum_rotated_rectangle.area, 1e-9) > 0.9:
            (balconies if g.area > 3 else outside).append(g)
            continue
        if c == RED and not F.buffer(0.05).contains(g.centroid):
            outside.append(g)
            continue
        if c == RED:
            t = 'new'
        elif g.distance(Fb) < 0.03:
            t = 'exterior'
        elif stacked(g, fl, buf=cfg.get('stack_buf', 0.06)):
            t = 'load-bearing'
        else:
            t = 'interior'
        for ov in cfg.get('type_override', []):
            if Polygon(ov['area']).contains(g.centroid):
                t = ov['type']
        walls_by_type[t].append(g)

    plan = {
        'object': 'RBS25', 'floor': fl, 'floor_name': cfg['floor_name'],
        'margin': cfg.get('margin', 3.0),
        'source': cfg['source'],
        'walls': [], 'wall_polygons': [], 'openings': [], 'rooms': [], 'symbols': [],
        'dimensions': [], 'notes': [], 'unverified': [],
    }

    # --- WE05 übernehmen (nur OG2)
    we = None
    we_geoms = []
    if region is not None:
        we = load_we05()
        lb = set(cfg.get('we05_load_bearing', []))
        for w in we['walls']:
            w2 = dict(w, a=tx_we05(w['a']), b=tx_we05(w['b']))
            if w['id'] in lb:
                w2['type'] = 'load-bearing'
            w2['id'] = 'WE5-' + w['id']
            plan['walls'].append(w2)
            we_geoms.append(axis_wall_poly(w2))
        for wp in we['wall_polygons']:
            poly = [tx_we05(p) for p in wp['polygon']]
            if wp['id'] == 'fassade-links':  # Brandwand: Außenkante bleibt bei x = 0 (0,125 m statt 0,135 m)
                poly = [[0.0 if p[0] <= 0.0 else p[0], p[1]] for p in poly]
            t = wp['type']
            if wp['id'] in lb:
                t = 'load-bearing'
            plan['wall_polygons'].append({'id': 'WE5-' + wp['id'], 'type': t, 'polygon': poly})
            we_geoms.append(P(poly))
        for op in we['openings']:
            op2 = json.loads(json.dumps(op))
            op2['host']['a'] = tx_we05(op['host']['a'])
            op2['host']['b'] = tx_we05(op['host']['b'])
            op2['id'] = 'WE5-' + op['id']
            op2['name'] = 'WE5 – ' + op['name']
            plan['openings'].append(op2)

    for ew in cfg.get('extra_walls', []):
        plan['walls'].append(dict(ew))
        we_geoms.append(axis_wall_poly(ew))

    # --- PDF-Wände ausgeben (nach Typ vereinigt, ohne Überlappung)
    taken = unary_union(we_geoms) if we_geoms else Polygon()
    n = 0
    for t in ('new', 'exterior', 'load-bearing', 'interior'):
        if not walls_by_type[t]:
            continue
        g = unary_union(walls_by_type[t]).buffer(0).difference(taken)
        g = g.simplify(0.003)
        for pg in polys(g):
            if pg.area < 0.004:
                continue
            n += 1
            e = {'id': f'{t}-{n:02d}', 'type': t, 'polygon': ring(pg.exterior.coords)}
            holes = [ring(h.coords) for h in pg.interiors if Polygon(h).area > 0.002]
            if holes:
                e['holes'] = holes
            plan['wall_polygons'].append(e)
        taken = unary_union([taken, g])
    W = unary_union([taken] + we_geoms).buffer(0)

    # --- Öffnungen: Türen aus Bögen
    Wb = W.buffer(0.012)
    door_hosts, gap_regions = [], []

    def gap_region(a, b, lo, hi, ext=0.06):
        """Lücke zwischen den Laibungen: lokales Closing der Wandstücke beidseits der Achse a-b."""
        L_ = math.dist(a, b)
        u = ((b[0] - a[0]) / L_, (b[1] - a[1]) / L_)
        n = (-u[1], u[0])
        q = lambda s, t: (a[0] + u[0] * s + n[0] * t, a[1] + u[1] * s + n[1] * t)
        band = Polygon([q(-0.5, lo), q(L_ + 0.5, lo), q(L_ + 0.5, hi), q(-0.5, hi)])
        inner = Polygon([q(-ext, lo), q(L_ + ext, lo), q(L_ + ext, hi), q(-ext, hi)])
        r_ = max(0.6, L_ / 2 + 0.3)
        cl = close_mitre(W.intersection(band), r_)
        g = cl.intersection(inner).difference(W).buffer(0)
        ps = polys(g)
        return max(ps, key=lambda p: p.area) if ps else Polygon()

    def door_band(a, b, side):
        """Band über die Wanddicke auf der dem Aufschlag abgewandten Seite (Dicke gemessen an den Laibungen)."""
        L_ = math.dist(a, b)
        u = ((b[0] - a[0]) / L_, (b[1] - a[1]) / L_)
        n = (-u[1], u[0])
        sg = -1 if side == 'left' else 1
        best = 0.0
        for s in (-0.05, L_ + 0.05):
            p = (a[0] + u[0] * s, a[1] + u[1] * s)
            ray = LineString([p, (p[0] + n[0] * sg * 0.8, p[1] + n[1] * sg * 0.8)])
            x = ray.intersection(W.buffer(0.005))
            for part in ([x] if x.geom_type == 'LineString' else list(getattr(x, 'geoms', []))):
                if part.is_empty:
                    continue
                d0 = min(Point(c).distance(Point(p)) for c in part.coords)
                if d0 < 0.03:
                    best = max(best, part.length)
        t = (best or 0.3) + 0.02
        return (-t, 0.02) if side == 'left' else (-0.02, t)

    nd = 0
    for d in find_doors(fl):
        H = d['hinge']
        if region is not None and region.buffer(0.03).contains(Point(H)):
            continue
        if any(Point(H).distance(Point(x)) < 0.1 for x in cfg.get('skip_doors', [])):
            continue
        cands = []
        for P1, P2 in ((d['p1'], d['p2']), (d['p2'], d['p1'])):
            L = math.dist(H, P1)
            u = ((P1[0] - H[0]) / L, (P1[1] - H[1]) / L)
            q1 = Point(P1[0] + u[0] * 0.08, P1[1] + u[1] * 0.08)
            q2 = Point(H[0] - u[0] * 0.08, H[1] - u[1] * 0.08)
            cands.append((2 * Wb.contains(q1) + Wb.contains(q2), (P1, P2)))
        cands.sort(key=lambda c: -c[0])
        if cands[0][0] == cands[1][0]:
            print('  Tür unklar', [round(v, 3) for v in H], cands[0][0], file=sys.stderr)
        cands = [c[1] for c in cands]
        closed, leaf = cands[0]
        cr = (closed[0] - H[0]) * (leaf[1] - H[1]) - (closed[1] - H[1]) * (leaf[0] - H[0])
        side = 'left' if cr > 0 else 'right'
        nd += 1
        plan['openings'].append({'id': f'T{nd:02d}', 'name': 'Tür', 'type': 'door',
              'host': {'a': [R3(H[0]), R3(H[1])], 'b': [R3(closed[0]), R3(closed[1])], 'thickness': 0},
              'offset': 0, 'width': R3(math.dist(H, closed)), 'hinge': 'start', 'side': side})
        door_hosts.append(LineString([H, closed]))
        # Wand liegt auf der dem Aufschlag abgewandten Seite
        lo, hi = door_band(H, closed, side)
        gap_regions.append(gap_region(H, closed, lo, hi, ext=0.15))
    for md in cfg.get('extra_doors', []):
        nd += 1
        a, b = md['a'], md['b']
        plan['openings'].append({'id': f'T{nd:02d}', 'name': md.get('name', 'Tür'), 'type': 'door',
              'host': {'a': a, 'b': b, 'thickness': 0}, 'offset': 0, 'width': R3(math.dist(a, b)),
              'hinge': 'start', 'side': md['side']})
        door_hosts.append(LineString([a, b]))
        lo, hi = door_band(a, b, md['side'])
        gap_regions.append(gap_region(a, b, lo, hi, ext=0.15))

    # --- Fenster: Lücken im Umriss (Außenkante) der Außenwände
    nw = 0
    for pg in ([] if cfg.get('no_windows') else polys(F)):
        cs = list(pg.exterior.coords)
        if pg.exterior.is_ccw is False:
            cs = cs[::-1]
        from shapely.ops import linemerge
        diff = LineString(cs).difference(W.buffer(0.04))
        diff = linemerge(diff) if diff.geom_type == 'MultiLineString' else diff
        if True:
            for piece in ([diff] if diff.geom_type == 'LineString' else list(getattr(diff, 'geoms', []))):
                if piece.is_empty or not (0.3 <= piece.length <= 2.6):
                    continue
                if math.dist(piece.coords[0], piece.coords[-1]) < 0.9 * piece.length:
                    continue
                p0, p1 = piece.coords[0], piece.coords[-1]
                mid = piece.interpolate(0.5, normalized=True)
                if region is not None and region.buffer(0.02).contains(mid):
                    continue
                if any(Point(x).distance(mid) < 0.4 for x in cfg.get('skip_windows', [])):
                    continue
                L_ = math.dist(p0, p1)
                u = ((p1[0] - p0[0]) / L_, (p1[1] - p0[1]) / L_)
                n = (-u[1], u[0])  # CCW-Umriss: links = innen
                g = gap_region(p0, p1, -0.02, 0.75, ext=0.08)
                if g.is_empty or g.area < 0.05:
                    print('  Lücke ohne Fläche', [round(v,2) for v in p0], [round(v,2) for v in p1], round(g.area,3), file=sys.stderr)
                    continue
                if any(g.buffer(0.08).intersects(h) for h in door_hosts):
                    gap_regions.append(g)
                    continue
                # schmalste Stelle der Laibung = Glasebene
                ts = [(q[0] - p0[0]) * n[0] + (q[1] - p0[1]) * n[1] for q in g.exterior.coords]
                t0, t1 = max(0.0, min(ts)), max(ts)
                best = None
                for k in range(1, 30):
                    t = t0 + (t1 - t0) * k / 30
                    o = (p0[0] + n[0] * t, p0[1] + n[1] * t)
                    ln = LineString([(o[0] - u[0] * 3, o[1] - u[1] * 3), (o[0] + u[0] * (L_ + 3), o[1] + u[1] * (L_ + 3))])
                    s_ = ln.intersection(g)
                    if s_.is_empty or s_.geom_type != 'LineString':
                        continue
                    if best is None or s_.length < best[0] - 0.004:
                        best = (s_.length, s_)
                if best is None:
                    continue
                w, s_ = best
                A, B = s_.coords[0], s_.coords[-1]
                nw += 1
                plan['openings'].append({'id': f'F{nw:02d}', 'name': 'Fenster', 'type': 'window',
                    'host': {'a': [R3(A[0]), R3(A[1])], 'b': [R3(B[0]), R3(B[1])], 'thickness': 0.09, 'align': 'center'},
                    'offset': 0, 'width': R3(w)})
                gap_regions.append(g)

    if we is not None:
        for op in plan['openings']:
            if op['id'].startswith('WE5-'):
                a, bb_ = op['host']['a'], op['host']['b']
                gap_regions.append(gap_region(a, bb_, -0.45, 0.45))

    # --- Räume aus Freiflächen
    x0, y0, x1, y1 = W.bounds
    free = box(x0 - 3, y0 - 3, x1 + 3, y1 + 3).difference(W.buffer(0.004, join_style=2))
    gaps = [g for g in gap_regions if not g.is_empty]
    if gaps:
        free = free.difference(unary_union([g.buffer(0.006, join_style=2) for g in gaps]))
    for bl in cfg.get('barriers', []):
        free = free.difference(LineString(bl).buffer(0.004, cap_style=2))
    comps = polys(free)
    DBG.update(W=W, gaps=gaps, free=free, F=F)
    if we is not None:
        for r in we['rooms']:
            r2 = dict(r)
            r2['polygon'] = [tx_we05(p) for p in r['polygon']]
            if 'label_pos' in r:
                r2['label_pos'] = tx_we05(r['label_pos'])
            r2['name'] = 'WE5 – ' + r['name']
            r2.update(cfg.get('we05_room_patch', {}).get(r['name'], {}))
            plan['rooms'].append(r2)
    for rc in cfg['rooms']:
        pt = Point(rc['pos'])
        if 'polygon' in rc:
            poly = rc['polygon']
            pg = Polygon(poly)
        else:
            hit = [c for c in comps if c.contains(pt)]
            if not hit:
                print('  Raum nicht gefunden:', rc['name'], file=sys.stderr)
                continue
            pg = Polygon(hit[0].exterior).buffer(0.004, join_style=2).simplify(0.004)
            if pg.area > 80:
                print('  Raum offen (zu groß):', rc['name'], round(pg.area, 1), file=sys.stderr)
                continue
            poly = ring(pg.exterior.coords)
        r = {'name': rc['name'], 'polygon': poly, 'label_pos': rc.get('label', rc['pos'])}
        for k in ('area_stated', 'subtitle', 'show_area', 'outline', 'name_size'):
            if k in rc:
                r[k] = rc[k]
        plan['rooms'].append(r)
    # Balkone (rot gefüllt im Aufteilungsplan)
    for i, g in enumerate(sorted(balconies, key=lambda g: g.centroid.x)):
        bc = cfg['balconies'][i] if i < len(cfg.get('balconies', [])) else {'name': 'Balkon'}
        poly = ring(g.minimum_rotated_rectangle.exterior.coords)
        r = {'name': bc['name'], 'polygon': poly, 'label_pos': bc.get('label', [R3(g.centroid.x), R3(g.centroid.y)]),
             'outline': True, 'name_size': 2.2}
        for k in ('subtitle', 'show_area', 'area_stated'):
            if k in bc:
                r[k] = bc[k]
        plan['rooms'].append(r)

    # --- Symbole
    S = strokes(fl)
    if cfg.get('stairs'):
        for k, bx in enumerate(cfg['stairs']):
            bb = box(*bx)
            lines = [[[R3(a[0]), R3(a[1])], [R3(b[0]), R3(b[1])]] for w_, a, b in S
                     if bb.contains(Point(a)) and bb.contains(Point(b)) and math.dist(a, b) > 0.004]
            pgs = [{'points': [[R3(x), R3(y)] for x, y in r], 'fill': 'solid'} for c, p in fills(fl)
                   if c == (0.0, 0.0, 0.0) for r in p if all(bb.contains(Point(q)) for q in r)]
            plan['symbols'].append({'id': f'treppe-{k+1}', 'layer': 'A_TREPPE', 'lines': lines, 'polygons': pgs})
    if cfg.get('north'):
        bb = box(*cfg['north'])
        lines = [[[R3(a[0]), R3(a[1])], [R3(b[0]), R3(b[1])]] for w_, a, b in S
                 if bb.contains(Point(a)) and bb.contains(Point(b))]
        circ = []
        for d in drawings(fl):
            if d['type'] == 's' and any(it[0] == 'c' for it in d['items']):
                pts = [tom(fl, (q.x, q.y)) for it in d['items'] for q in it[1:]]
                if all(bb.contains(Point(q)) for q in pts):
                    xs, ys = [q[0] for q in pts], [q[1] for q in pts]
                    rr = (max(xs) - min(xs)) / 2
                    if rr > 0.1:
                        circ.append({'c': [R3((max(xs) + min(xs)) / 2), R3((max(ys) + min(ys)) / 2)], 'r': R3(rr)})
        plan['symbols'].append({'id': 'nordpfeil', 'layer': 'A_SYMBOL', 'lines': lines, 'circles': circ})
    if cfg.get('fixtures', True):
        # Einrichtung (Sanitärobjekte, WM) aus den Strichen innerhalb der Räume
        rooms_g = [Polygon(r['polygon']).buffer(-0.03) for r in plan['rooms']
                   if any(k in r['name'] for k in cfg.get('fixture_rooms', ('Bad', 'WC', 'Kochen', 'Abst')))
                   and not r['name'].startswith('WE5')]
        doorz = unary_union([Point(o['host']['a']).buffer(o['width'] + 0.03) for o in plan['openings'] if o['type'] == 'door'])
        segs = [s for s in S if math.dist(s[1], s[2]) > 0.003]
        yel = unary_union([P(p) for c_, p in fills(fl) if c_ == YEL]).buffer(0.25)
        lines = []
        for ch in chains(segs, 0.004):
            ls = LineString(ch)
            if ls.length < 0.15:
                continue
            if not any(rg.contains(ls) for rg in rooms_g):
                continue
            if doorz.contains(ls) or ls.intersects(yel):
                continue
            lines += [[[R3(a[0]), R3(a[1])], [R3(b[0]), R3(b[1])]] for a, b in zip(ch, ch[1:])]
        if lines:
            plan['symbols'].append({'id': 'einrichtung', 'layer': 'A_SYMBOL', 'lines': lines})
    if cfg.get('roof_box'):
        # Dachflächen (Sparren, Traufe, Grat) außerhalb der Räume
        rb = box(*cfg['roof_box'])
        rooms_all = unary_union([Polygon(r['polygon']).buffer(-0.04) for r in plan['rooms']])
        doorz2 = unary_union([Point(o['host']['a']).buffer(o['width'] + 0.03) for o in plan['openings'] if o['type'] == 'door'])
        rl = []
        for w_, a, b_ in S:
            if math.dist(a, b_) < 0.25:
                continue
            ls = LineString([a, b_])
            if not rb.contains(ls) or ls.intersects(rooms_all) or doorz2.contains(ls) or W.buffer(0.01).contains(ls):
                continue
            rl.append([[R3(a[0]), R3(a[1])], [R3(b_[0]), R3(b_[1])]])
        if rl:
            plan['symbols'].append({'id': 'dach', 'layer': 'A_SYMBOL', 'lines': rl})
    # Nachbarhäuser
    nb = box(x0 - 1.2, y0 - 0.2, x1 + 1.2, y1 + 1.6)
    if cfg.get('umgebung_boxes'):
        nb = unary_union([box(*bx) for bx in cfg['umgebung_boxes']])
    nlines = []
    for c, p in fills(fl):
        if c == NEIGH:
            g = P(p).intersection(nb)
            for pg in polys(g):
                cs = ring(pg.exterior.coords)
                nlines += [[cs[i], cs[(i + 1) % len(cs)]] for i in range(len(cs))]
    for g0 in outside:
        for g in polys(g0):
            cs = ring(g.exterior.coords)
            nlines += [[cs[i], cs[(i + 1) % len(cs)]] for i in range(len(cs))]
    if nlines:
        plan['symbols'].append({'id': 'umgebung', 'layer': 'A_SYMBOL', 'lines': nlines})

    plan['dimensions'] = []
    if we is not None:
        for d_ in we['dimensions']:
            if d_.get('label') in cfg.get('we05_drop_dims', []):
                continue
            d2 = dict(d_, a=tx_we05(d_['a']), b=tx_we05(d_['b']))
            d2.update(cfg.get('we05_dim_patch', {}).get(d_['label'] + '@' + str(d_['a'][0]), {}))
            if d2.get('label', '').startswith('ca. ') and d2['label'][4:] in cfg.get('we05_dims_confirmed', []):
                d2['label'] = d2['label'][4:]
            plan['dimensions'].append(d2)
    plan['dimensions'] += cfg.get('dimensions', [])
    for ac in cfg.get('auto_chains', []):
        dims, notes = auto_chain(W, **ac)
        plan['dimensions'] += dims
        cfg.setdefault('notes', []).extend(notes)
    plan['notes'] = cfg.get('notes', [])
    if we is not None:
        plan['notes'] = [dict(n_, pos=tx_we05(n_['pos'])) for n_ in we['notes'] if n_['text'] not in cfg.get('we05_drop_notes', [])] + plan['notes']
        for u in we['unverified']:
            if u['text'] in cfg.get('we05_drop_unverified', []):
                continue
            u2 = dict(u, pos=tx_we05(u['pos']))
            for k_, v_ in cfg.get('we05_unv_patch', {}).items():
                if u['text'].startswith(k_):
                    u2.update(v_)
            plan['unverified'].append(u2)
    plan['unverified'] += out_unv
    if not plan['walls']:
        del plan['walls']
    return plan


def fmt(v):
    c = round(v * 200) / 2  # cm, auf 0,5 cm
    s = f'{int(c) // 100},{int(c) % 100:02d}'
    return s + ('⁵' if c % 1 else '')


def auto_chain(W, axis, at, base, offset, lo=-50, hi=50, total=True, min_seg=0.4):
    """Maßkette aus den Wandkanten entlang einer Messlinie (axis 'x': horizontal bei y=at)."""
    if axis == 'x':
        ln = LineString([(lo, at), (hi, at)])
    else:
        ln = LineString([(at, lo), (at, hi)])
    x = ln.intersection(W)
    parts = [x] if x.geom_type == 'LineString' else list(getattr(x, 'geoms', []))
    k = 0 if axis == 'x' else 1
    pts = sorted({round(c[k], 3) for p in parts for c in p.coords})
    merged = []
    for p in pts:
        if merged and p - merged[-1] < 0.02:
            continue
        merged.append(p)
    dims, notes = [], []
    P = lambda v: [v, base] if axis == 'x' else [base, v]
    for a, b in zip(merged, merged[1:]):
        L = b - a
        small = L < min_seg
        dims.append({'a': P(a), 'b': P(b), 'offset': offset, 'label': ' ' if small else fmt(L)})
        if small:
            m = (a + b) / 2
            sg = -1 if offset < 0 else 1
            pos = [m, base + offset - sg * 0.33] if axis == 'x' else [base - offset + sg * 0.33 - 0.0, m]
            if axis == 'x':
                pos = [round(m, 3), round(base + offset - 0.33, 3)] if offset < 0 else [round(m, 3), round(base + offset + 0.12, 3)]
                notes.append({'pos': pos, 'text': fmt(L), 'size': 1.5})
            else:
                pos = [round(base - offset + 0.12, 3), round(m - 0.05, 3)] if offset < 0 else [round(base - offset - 0.12, 3), round(m - 0.05, 3)]
                notes.append({'pos': pos, 'text': fmt(L), 'size': 1.5, 'anchor': 'start' if offset < 0 else 'end'})
    if total and len(merged) > 1:
        dims.append({'a': P(merged[0]), 'b': P(merged[-1]), 'offset': offset + (-0.8 if offset < 0 else 0.8),
                     'label': fmt(merged[-1] - merged[0])})
    return dims, notes


def dump(plan, path):
    """Kompakte JSON-Ausgabe: eine Zeile je Element."""
    o = ['{']
    keys = list(plan.keys())
    for i, k in enumerate(keys):
        v = plan[k]
        comma = ',' if i < len(keys) - 1 else ''
        if isinstance(v, list):
            o.append(f'  "{k}": [')
            for j, e in enumerate(v):
                o.append('    ' + json.dumps(e, ensure_ascii=False) + (',' if j < len(v) - 1 else ''))
            o.append('  ]' + comma)
        elif isinstance(v, dict):
            o.append(f'  "{k}": {{')
            ks = list(v.keys())
            for j, kk in enumerate(ks):
                o.append(f'    "{kk}": ' + json.dumps(v[kk], ensure_ascii=False) + (',' if j < len(ks) - 1 else ''))
            o.append('  }' + comma)
        else:
            o.append(f'  "{k}": ' + json.dumps(v, ensure_ascii=False) + comma)
    o.append('}')
    open(path, 'w', encoding='utf-8').write('\n'.join(o) + '\n')


if __name__ == '__main__':
    fl = sys.argv[1]
    plan = build(fl)
    dump(plan, f'{REPO}/plans/RBS25/geometrie/{fl}.json')
    print('ok', fl, {k: len(v) for k, v in plan.items() if isinstance(v, list)})
