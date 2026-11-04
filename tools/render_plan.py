#!/usr/bin/env python3
"""Grundriss-Renderer: Geometrie-JSON (Meter) -> SVG (1:100) + DXF.

Aufruf:
    python3 tools/render_plan.py plans/KFS29/geometrie/EG.json
    python3 tools/render_plan.py --all

Die Ausgabe landet in plans/<Objekt>/ausgabe/<Objekt>_<Geschoss>.svg|.dxf.
Schema und Zeichenregeln: siehe docs/ZEICHENRICHTLINIE.md.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent

# Layer: Name -> (DXF-Farbindex, SVG-Strichfarbe)
LAYERS = {
    "A_WAND_TRAGEND": (7, "#000000"),
    "A_WAND": (8, "#000000"),
    "A_WAND_NEU": (4, "#000000"),
    "A_OEFFNUNG": (1, "#000000"),
    "A_RAUM": (3, "#555555"),
    "A_BEMASSUNG": (5, "#333333"),
    "A_TEXT": (7, "#000000"),
    "A_UNGEPRUEFT": (6, "#d00000"),
}
MM_PER_M = 10.0  # 1:100 -> 1 m = 10 mm auf Papier


# ---------------------------------------------------------------- Geometrie
def vec(a, b):
    return (b[0] - a[0], b[1] - a[1])


def norm(v):
    length = math.hypot(*v)
    return (v[0] / length, v[1] / length), length


def wall_segments(wall, openings):
    """Zerlegt eine Wand an ihren Öffnungen in geschlossene Teilstücke."""
    (ux, uy), length = norm(vec(wall["a"], wall["b"]))
    cuts = sorted((o["offset"], o["offset"] + o["width"]) for o in openings)
    pos, pieces = 0.0, []
    for s, e in cuts:
        if s > pos + 1e-6:
            pieces.append((pos, s))
        pos = max(pos, e)
    if pos < length - 1e-6:
        pieces.append((pos, length))
    t = wall["thickness"]
    align = wall.get("align", "center")  # center | left | right (bzgl. a->b)
    nx, ny = -uy, ux
    lo, hi = {"center": (-t / 2, t / 2), "left": (0, t), "right": (-t, 0)}[align]
    ax, ay = wall["a"]
    polys = []
    for s, e in pieces:
        p = lambda d, o: (ax + ux * d + nx * o, ay + uy * d + ny * o)
        polys.append([p(s, lo), p(e, lo), p(e, hi), p(s, hi)])
    return polys, (ux, uy), (nx, ny), (lo, hi)


def wall_layer(wtype):
    """Wandtyp -> Layer. exterior/load-bearing tragend, new = neue Wand, sonst nichttragend."""
    if wtype in ("exterior", "load-bearing"):
        return "A_WAND_TRAGEND"
    if wtype == "new":
        return "A_WAND_NEU"
    return "A_WAND"


def host_frame(host):
    """Laufrichtung u, Normale n (links von a->b) und Band (lo, hi) einer Achse.

    Dient freien Öffnungen (``"host"`` statt ``"wall"``), die in ``wall_polygons``
    liegen und deshalb keine Achswand haben. ``thickness`` darf 0 sein (Türen).
    """
    (ux, uy), _ = norm(vec(host["a"], host["b"]))
    t = host.get("thickness", 0.0)
    lo, hi = {"center": (-t / 2, t / 2), "left": (0, t), "right": (-t, 0)}[host.get("align", "center")]
    return (ux, uy), (-uy, ux), (lo, hi)


def shoelace(poly):
    return abs(sum(poly[i][0] * poly[i - 1][1] - poly[i - 1][0] * poly[i][1]
                   for i in range(len(poly)))) / 2


def centroid(poly):
    return (sum(p[0] for p in poly) / len(poly), sum(p[1] for p in poly) / len(poly))


def opening_geometry(wall, op, u, n, band):
    """Liefert Linien (Liste von Punktpaaren) und Bögen für eine Öffnung."""
    ax, ay = wall["a"]
    lo, hi = band
    s, w = op["offset"], op["width"]
    p = lambda d, o: (ax + u[0] * d + n[0] * o, ay + u[1] * d + n[1] * o)
    lines, arcs = [], []
    if op["type"] == "window":
        mid = (lo + hi) / 2
        lines += [(p(s, lo), p(s + w, lo)), (p(s, hi), p(s + w, hi)),
                  (p(s, mid - 0.02), p(s + w, mid - 0.02)), (p(s, mid + 0.02), p(s + w, mid + 0.02)),
                  (p(s, lo), p(s, hi)), (p(s + w, lo), p(s + w, hi))]
    else:  # door
        hinge_at_start = op.get("hinge", "start") == "start"
        side = 1 if op.get("side", "left") == "left" else -1
        face = hi if side > 0 else lo
        h = s if hinge_at_start else s + w
        tip = s + w if hinge_at_start else s
        hinge = p(h, face)
        leaf_end = (hinge[0] + n[0] * side * w, hinge[1] + n[1] * side * w)
        lines.append((hinge, leaf_end))
        arcs.append({"center": hinge, "radius": w, "from": leaf_end, "to": p(tip, face)})
    return lines, arcs


def build(plan):
    walls = {w["id"]: w for w in plan.get("walls", [])}
    ops_by_wall = {}
    free_ops = []
    for op in plan.get("openings", []):
        if "host" in op:  # freie Öffnung ohne Achswand (z. B. in wall_polygons)
            free_ops.append(op)
            continue
        if op["wall"] not in walls:
            raise ValueError(f"Öffnung {op.get('id')} verweist auf unbekannte Wand {op['wall']}")
        ops_by_wall.setdefault(op["wall"], []).append(op)
    out = {"walls": [], "lines": [], "arcs": []}
    for wid, wall in walls.items():
        polys, u, n, band = wall_segments(wall, ops_by_wall.get(wid, []))
        layer = wall_layer(wall.get("type"))
        out["walls"] += [(layer, poly) for poly in polys]
        for op in ops_by_wall.get(wid, []):
            ls, ars = opening_geometry(wall, op, u, n, band)
            out["lines"] += [("A_OEFFNUNG", l) for l in ls]
            out["arcs"] += [("A_OEFFNUNG", a) for a in ars]
    for wp in plan.get("wall_polygons", []):
        out["walls"].append((wall_layer(wp.get("type")), wp["polygon"]))
    for op in free_ops:
        u, n, band = host_frame(op["host"])
        ls, ars = opening_geometry(op["host"], op, u, n, band)
        out["lines"] += [("A_OEFFNUNG", l) for l in ls]
        out["arcs"] += [("A_OEFFNUNG", a) for a in ars]
    return out


def bbox(plan):
    pts = [pt for w in plan.get("walls", []) for pt in (w["a"], w["b"])]
    pts += [pt for wp in plan.get("wall_polygons", []) for pt in wp["polygon"]]
    # Räume außerhalb der Wände (z. B. Balkon) gehören zur Zeichenfläche
    pts += [pt for r in plan.get("rooms", []) for pt in r["polygon"]]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


def margin_for(plan):
    """Zeichenrand in m: mindestens 2,5; wächst mit weit abgesetzten Maßketten."""
    offs = [abs(d.get("offset", 1.0)) for d in plan.get("dimensions", [])]
    return max(2.5, max(offs, default=0) + 1.3)


def room_report(plan):
    rows = []
    for r in plan.get("rooms", []):
        calc = shoelace(r["polygon"])
        stated = r.get("area_stated")
        dev = None if stated is None else (calc - stated) / stated * 100
        rows.append((r["name"], calc, stated, dev))
    return rows


# ---------------------------------------------------------------------- SVG
def render_svg(plan, geo, path):
    x0, y0, x1, y1 = bbox(plan)
    margin = margin_for(plan)  # m
    W, H = x1 - x0 + 2 * margin, y1 - y0 + 2 * margin + 2.0
    tx = lambda p: ((p[0] - x0 + margin) * MM_PER_M, (y1 - p[1] + margin) * MM_PER_M)
    pts = lambda poly: " ".join(f"{tx(p)[0]:.2f},{tx(p)[1]:.2f}" for p in poly)
    o = []
    o.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W*MM_PER_M:.1f}mm" '
             f'height="{H*MM_PER_M:.1f}mm" viewBox="0 0 {W*MM_PER_M:.1f} {H*MM_PER_M:.1f}">')
    o.append(f'<title>{escape(plan["object"])} – {escape(plan["floor_name"])}</title>')
    o.append('<style>text{font-family:Arial,Helvetica,sans-serif}</style>')
    o.append(f'<rect width="100%" height="100%" fill="#ffffff"/>')

    o.append('<g id="A_RAUM" fill="none">')
    for r in plan.get("rooms", []):
        if r.get("outline"):  # optional: gestrichelte Kontur (z. B. Balkon außerhalb der Wände)
            o.append(f'<polygon points="{pts(r["polygon"])}" fill="#f4f4f4" stroke="#555" '
                     f'stroke-width="0.25" stroke-dasharray="2,1"/>')
        else:
            o.append(f'<polygon points="{pts(r["polygon"])}" fill="#f4f4f4" stroke="none"/>')
    o.append('</g>')

    if any(lay == "A_WAND_NEU" for lay, _ in geo["walls"]):
        o.append('<defs><pattern id="schraffur-neu" width="1.6" height="1.6" patternUnits="userSpaceOnUse" '
                 'patternTransform="rotate(45)"><rect width="1.6" height="1.6" fill="#ffffff"/>'
                 '<line x1="0" y1="0" x2="0" y2="1.6" stroke="#000" stroke-width="0.5"/></pattern></defs>')
    for layer in ("A_WAND_TRAGEND", "A_WAND", "A_WAND_NEU"):
        fill = {"A_WAND_TRAGEND": "#000000", "A_WAND": "#9a9a9a", "A_WAND_NEU": "url(#schraffur-neu)"}[layer]
        members = [poly for lay, poly in geo["walls"] if lay == layer]
        if layer == "A_WAND_NEU" and not members:
            continue
        o.append(f'<g id="{layer}" fill="{fill}" stroke="#000" stroke-width="0.35">')
        o += [f'<polygon points="{pts(poly)}"/>' for poly in members]
        o.append('</g>')

    o.append('<g id="A_OEFFNUNG" fill="none" stroke="#000" stroke-width="0.18">')
    for _, (a, b) in geo["lines"]:
        (ax, ay), (bx, by) = tx(a), tx(b)
        o.append(f'<line x1="{ax:.2f}" y1="{ay:.2f}" x2="{bx:.2f}" y2="{by:.2f}"/>')
    for _, arc in geo["arcs"]:
        (fx, fy), (ex, ey) = tx(arc["from"]), tx(arc["to"])
        r = arc["radius"] * MM_PER_M
        c = arc["center"]
        cross = (arc["from"][0] - c[0]) * (arc["to"][1] - c[1]) - (arc["from"][1] - c[1]) * (arc["to"][0] - c[0])
        sweep = 1 if cross < 0 else 0  # y-Achse im SVG gespiegelt
        o.append(f'<path d="M{fx:.2f},{fy:.2f} A{r:.2f},{r:.2f} 0 0 {sweep} {ex:.2f},{ey:.2f}" stroke-dasharray="1,0.8"/>')
    o.append('</g>')

    o.append('<g id="A_BEMASSUNG" stroke="#333" stroke-width="0.13" font-size="2.2" fill="#333">')
    for d in plan.get("dimensions", []):
        (ux, uy), length = norm(vec(d["a"], d["b"]))
        off = d.get("offset", 1.0)
        nx, ny = -uy * off, ux * off
        a2, b2 = (d["a"][0] + nx, d["a"][1] + ny), (d["b"][0] + nx, d["b"][1] + ny)
        (ax, ay), (bx, by) = tx(a2), tx(b2)
        o.append(f'<line x1="{ax:.2f}" y1="{ay:.2f}" x2="{bx:.2f}" y2="{by:.2f}"/>')
        for p0, p1 in ((d["a"], a2), (d["b"], b2)):
            (sx, sy), (ex, ey) = tx(p0), tx(p1)
            o.append(f'<line x1="{sx:.2f}" y1="{sy:.2f}" x2="{ex:.2f}" y2="{ey:.2f}"/>')
            o.append(f'<line x1="{ex-0.8:.2f}" y1="{ey+0.8:.2f}" x2="{ex+0.8:.2f}" y2="{ey-0.8:.2f}" stroke-width="0.35"/>')
        mx, my = (ax + bx) / 2, (ay + by) / 2
        ang = -math.degrees(math.atan2(uy, ux))
        if ang < -90 or ang > 90:
            ang += 180
        label = d.get("label") or f"{length:.3f}".replace(".", ",")
        o.append(f'<text x="{mx:.2f}" y="{my-0.8:.2f}" text-anchor="middle" stroke="none" '
                 f'transform="rotate({ang:.1f} {mx:.2f} {my:.2f})">{escape(label)}</text>')
    o.append('</g>')

    o.append('<g id="A_TEXT" font-size="2.6" text-anchor="middle" fill="#000">')
    for r in plan.get("rooms", []):
        cx, cy = tx(r.get("label_pos") or centroid(r["polygon"]))
        area = r.get("area_stated") or shoelace(r["polygon"])
        o.append(f'<text x="{cx:.2f}" y="{cy:.2f}" font-weight="bold">{escape(r["name"])}</text>')
        # optional: "subtitle" ersetzt die Flächenzeile, "show_area": false blendet sie aus
        if r.get("subtitle"):
            o.append(f'<text x="{cx:.2f}" y="{cy+3.2:.2f}" font-size="2.2">{escape(r["subtitle"])}</text>')
        elif r.get("show_area", True):
            area_txt = f"{area:.2f}".replace(".", ",")
            o.append(f'<text x="{cx:.2f}" y="{cy+3.2:.2f}" font-size="2.2">{area_txt} m²</text>')
    for nt in plan.get("notes", []):
        cx, cy = tx(nt["pos"])
        bold = ' font-weight="bold"' if nt.get("bold") else ""
        o.append(f'<text x="{cx:.2f}" y="{cy:.2f}" font-size="{nt.get("size", 2.2)}" '
                 f'text-anchor="{nt.get("anchor", "middle")}"{bold}>{escape(nt["text"])}</text>')
    o.append('</g>')

    unv = plan.get("unverified", [])
    if unv:
        o.append('<g id="A_UNGEPRUEFT" fill="none" stroke="#d00000" stroke-width="0.3" font-size="2" >')
        for u in unv:
            cx, cy = tx(u["pos"])
            o.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="2.5"/>')
            # optional: "short" ist die Kurzfassung im Plan ("" = nur Kreis); "text" bleibt die volle Begründung
            shown = u.get("short", u["text"])
            if shown:
                o.append(f'<text x="{cx+3:.2f}" y="{cy:.2f}" fill="#d00000" stroke="none">{escape(shown)}</text>')
        o.append('</g>')

    # Schriftfeld
    src = plan.get("source", {})
    by = (H - 1.6) * MM_PER_M
    o.append(f'<g id="SCHRIFTFELD" font-size="2.6" fill="#000">'
             f'<text x="{margin*MM_PER_M:.1f}" y="{by:.1f}" font-weight="bold">'
             f'{escape(plan["object"])} · {escape(plan["floor_name"])} · M 1:100</text>'
             f'<text x="{margin*MM_PER_M:.1f}" y="{by+4:.1f}" font-size="2">'
             f'Quelle: {escape(src.get("file", "?"))} ({escape(src.get("date", "?"))}) · Maße in m · '
             f'Neuzeichnung, ohne Gewähr – rot markierte Werte ungeprüft</text></g>')
    o.append('</svg>')
    path.write_text("\n".join(o), encoding="utf-8")


# ---------------------------------------------------------------------- DXF
def render_dxf(plan, geo, path):
    import ezdxf

    doc = ezdxf.new("R2018", setup=True)
    doc.units = ezdxf.units.M
    msp = doc.modelspace()
    for name, (color, _) in LAYERS.items():
        doc.layers.add(name, color=color)
    for layer, poly in geo["walls"]:
        msp.add_lwpolyline(poly, close=True, dxfattribs={"layer": layer})
        h = msp.add_hatch(color={"A_WAND_TRAGEND": 7, "A_WAND": 8}.get(layer, 4), dxfattribs={"layer": layer})
        h.paths.add_polyline_path(poly, is_closed=True)
        if layer == "A_WAND_NEU":  # neue Wände: Schraffur statt Vollfläche
            h.set_pattern_fill("ANSI31", scale=0.05)
    for layer, (a, b) in geo["lines"]:
        msp.add_line(a, b, dxfattribs={"layer": layer})
    for layer, arc in geo["arcs"]:
        c = arc["center"]
        a1 = math.degrees(math.atan2(arc["from"][1] - c[1], arc["from"][0] - c[0]))
        a2 = math.degrees(math.atan2(arc["to"][1] - c[1], arc["to"][0] - c[0]))
        if (a2 - a1) % 360 > 180:
            a1, a2 = a2, a1
        msp.add_arc(c, arc["radius"], a1, a2, dxfattribs={"layer": layer})
    for r in plan.get("rooms", []):
        msp.add_lwpolyline(r["polygon"], close=True, dxfattribs={"layer": "A_RAUM"})
        cx, cy = r.get("label_pos") or centroid(r["polygon"])
        area = r.get("area_stated") or shoelace(r["polygon"])
        msp.add_text(r["name"], height=0.25, dxfattribs={"layer": "A_TEXT"}).set_placement(
            (cx, cy), align=ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER)
        if r.get("subtitle") or r.get("show_area", True):
            msp.add_text(r.get("subtitle") or f"{area:.2f} m²".replace(".", ","), height=0.2,
                         dxfattribs={"layer": "A_TEXT"}).set_placement(
                (cx, cy - 0.35), align=ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER)
    for nt in plan.get("notes", []):
        al = {"middle": ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER,
              "start": ezdxf.enums.TextEntityAlignment.MIDDLE_LEFT,
              "end": ezdxf.enums.TextEntityAlignment.MIDDLE_RIGHT}[nt.get("anchor", "middle")]
        msp.add_text(nt["text"], height=nt.get("size", 2.2) / 10, dxfattribs={"layer": "A_TEXT"}).set_placement(
            nt["pos"], align=al)
    for d in plan.get("dimensions", []):
        (ux, uy), _ = norm(vec(d["a"], d["b"]))
        off = d.get("offset", 1.0)
        base = (d["a"][0] - uy * off, d["a"][1] + ux * off)
        dim = msp.add_aligned_dim(p1=d["a"], p2=d["b"], distance=off, dimstyle="EZ_M_100_H25_CM",
                                  dxfattribs={"layer": "A_BEMASSUNG"})
        dim.render()
    for u in plan.get("unverified", []):
        msp.add_circle(u["pos"], 0.25, dxfattribs={"layer": "A_UNGEPRUEFT"})
        msp.add_text(u["text"], height=0.2, dxfattribs={"layer": "A_UNGEPRUEFT"}).set_placement(
            (u["pos"][0] + 0.3, u["pos"][1]))  # im DXF immer die volle Begründung
    doc.saveas(path)


# ---------------------------------------------------------------------- main
def render(json_path: Path):
    plan = json.loads(json_path.read_text(encoding="utf-8"))
    geo = build(plan)
    out_dir = json_path.parent.parent / "ausgabe"
    out_dir.mkdir(exist_ok=True)
    stem = f'{plan["object"]}_{plan["floor"]}'
    render_svg(plan, geo, out_dir / f"{stem}.svg")
    render_dxf(plan, geo, out_dir / f"{stem}.dxf")
    print(f"{json_path.relative_to(ROOT)} -> ausgabe/{stem}.svg, .dxf")
    bad = False
    for name, calc, stated, dev in room_report(plan):
        flag = ""
        if dev is not None and abs(dev) > 3:
            flag, bad = "  <-- Abweichung > 3 %", True
        st = "—" if stated is None else f"{stated:.2f}"
        dv = "" if dev is None else f"{dev:+.1f} %"
        print(f"   {name:<24} berechnet {calc:7.2f} m²  laut Plan {st:>7}  {dv}{flag}")
    return not bad


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="*", type=Path)
    ap.add_argument("--all", action="store_true", help="alle plans/*/geometrie/*.json rendern")
    args = ap.parse_args()
    files = sorted(ROOT.glob("plans/*/geometrie/*.json")) if args.all else [f.resolve() for f in args.files]
    if not files:
        ap.error("keine Geometriedateien angegeben")
    ok = all([render(f) for f in files])
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
