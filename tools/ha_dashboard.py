#!/usr/bin/env python3
"""Home-Assistant-Dashboard-Hintergrund aus einer Geometrie-JSON erzeugen.

Erzeugt aus der maßgetreuen Neuzeichnung (plans/<Objekt>/geometrie/<G>.json)
einen reduzierten, hellgrauen Grundriss als SVG für eine Home-Assistant
``picture-elements``-Karte – inklusive angedeuteter Umgebung (Straße, Garten) –
sowie eine Positionsliste (Raummitten, Fenster, Türen) in Prozent der Bildfläche,
mit der sich Badges/Icons direkt platzieren lassen.

Aufruf:
    python3 tools/ha_dashboard.py plans/KSS29/dashboard/dashboard.json

Die Konfiguration (JSON) legt Quelle, Format und Umgebung fest, siehe
plans/KSS29/dashboard/dashboard.json als Beispiel.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from xml.sax.saxutils import escape

sys.path.insert(0, str(Path(__file__).resolve().parent))
import render_plan as rp  # noqa: E402  (gleiche Wand-/Öffnungslogik wie der Plan)

ROOT = Path(__file__).resolve().parent.parent
GREY = "#8f8f8f"


def slug(name: str) -> str:
    tr = str.maketrans({"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss", "Ä": "ae", "Ö": "oe", "Ü": "ue"})
    s = "".join(c if c.isalnum() else "_" for c in name.translate(tr).lower())
    return "_".join(p for p in s.split("_") if p)


def inside(pt, poly):
    x, y = pt
    c = False
    for i in range(len(poly)):
        (x1, y1), (x2, y2) = poly[i - 1], poly[i]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            c = not c
    return c


def seg_dist(p, a, b):
    ax, ay = a; bx, by = b; px, py = p
    dx, dy = bx - ax, by - ay
    t = 0 if dx == dy == 0 else max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    return math.hypot(px - ax - t * dx, py - ay - t * dy)


def visual_center(poly, n=48):
    """Punkt im Raum mit größtem Abstand zu den Wänden (gut für Badges, auch bei L-Räumen)."""
    xs, ys = [q[0] for q in poly], [q[1] for q in poly]
    best, bd = ((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2), -1
    for i in range(n + 1):
        for j in range(n + 1):
            q = (min(xs) + (max(xs) - min(xs)) * i / n, min(ys) + (max(ys) - min(ys)) * j / n)
            if not inside(q, poly):
                continue
            d = min(seg_dist(q, poly[k - 1], poly[k]) for k in range(len(poly)))
            # leichte Bevorzugung der Raummitte, damit symmetrische Räume mittig bleiben
            d -= 0.02 * math.hypot(q[0] - (min(xs) + max(xs)) / 2, q[1] - (min(ys) + max(ys)) / 2)
            if d > bd:
                best, bd = q, d
    return best


def text_width(txt: str, size: float) -> float:
    return 0.56 * size * len(txt)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("config", type=Path)
    cfg_path = ap.parse_args().config.resolve()
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    plan = json.loads((ROOT / cfg["source"]).read_text(encoding="utf-8"))

    W, H = cfg.get("width", 1280), cfg.get("height", 800)
    pad = cfg.get("padding", 24)
    left_band, right_band = cfg.get("left_band", {}), cfg.get("right_band", {})
    lb_w, rb_w = left_band.get("width", 96), right_band.get("width", 120)
    gap_l, gap_r = cfg.get("gap_left", 56), cfg.get("gap_right", 36)
    exclude = set(cfg.get("exclude_rooms", []))
    faint = set(cfg.get("faint_rooms", []))
    rename = cfg.get("rename", {})
    # optional: "label_pos" {Raum: [x, y]} und "badge_pos" {Raum: [x, y]} in Metern
    north_up_rotation = 0  # Geometrie ist nordorientiert (y = Norden)

    rooms = [r for r in plan.get("rooms", []) if r.get("name", "").strip() and r["name"] not in exclude]
    geo = rp.build(plan)

    # ---- Ausdehnung (ohne ausgeschlossene Räume) ----------------------------
    pts = [p for _, poly in geo["walls"] for p in poly]
    pts += [p for _, poly, _h in geo["walls_holed"] for p in poly]
    pts += [p for r in rooms for p in r["polygon"]]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)

    ax0 = pad + lb_w + gap_l
    ax1 = W - pad - rb_w - gap_r
    ay0, ay1 = pad + 16, H - pad - 16
    S = min((ax1 - ax0) / (x1 - x0), (ay1 - ay0) / (y1 - y0))
    ox = ax0 + ((ax1 - ax0) - (x1 - x0) * S) / 2
    oy = ay0 + ((ay1 - ay0) - (y1 - y0) * S) / 2
    T = lambda p: (ox + (p[0] - x0) * S, oy + (y1 - p[1]) * S)
    P = lambda poly: " ".join(f"{T(p)[0]:.1f},{T(p)[1]:.1f}" for p in poly)
    plan_left, plan_right = T((x0, 0))[0], T((x1, 0))[0]

    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
         f'font-family="system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif">',
         f'<title>{escape(cfg.get("title", plan["object"] + " " + plan["floor"]))}</title>',
         f'<desc>Erzeugt mit tools/ha_dashboard.py aus {escape(cfg["source"])} · Maßstab {S:.1f} px/m</desc>']

    # ---- Umgebung -----------------------------------------------------------
    env = ['<g id="umgebung">']
    if left_band:
        bx = pad
        env.append(f'<rect x="{bx}" y="{pad}" width="{lb_w}" height="{H-2*pad}" rx="3" fill="{GREY}" fill-opacity="0.07"/>')
        # Gehweg-Kante und Fahrbahnmitte
        env.append(f'<line x1="{bx+lb_w-10}" y1="{pad}" x2="{bx+lb_w-10}" y2="{H-pad}" stroke="{GREY}" stroke-opacity="0.25" stroke-width="1.5"/>')
        cx = bx + (lb_w - 10) / 2
        env.append(f'<line x1="{cx:.0f}" y1="{pad+14}" x2="{cx:.0f}" y2="{H-pad-14}" stroke="{GREY}" stroke-opacity="0.25" stroke-width="2" stroke-dasharray="14 12"/>')
        lbl = escape(left_band.get("label", "STRASSE"))
        env.append(f'<text x="{cx-12:.0f}" y="{H/2:.0f}" transform="rotate(-90 {cx-12:.0f} {H/2:.0f})" text-anchor="middle" '
                   f'font-size="13" letter-spacing="3" fill="{GREY}" fill-opacity="0.75">{lbl}</text>')
        if left_band.get("between_label"):
            vx = (bx + lb_w + plan_left) / 2
            env.append(f'<text x="{vx:.0f}" y="{H-pad-60}" transform="rotate(-90 {vx:.0f} {H-pad-60})" text-anchor="start" '
                       f'font-size="10" letter-spacing="2" fill="{GREY}" fill-opacity="0.5">{escape(left_band["between_label"])}</text>')
    if right_band:
        rx = W - pad - rb_w
        env.append(f'<rect x="{rx}" y="{pad}" width="{rb_w}" height="{H-2*pad}" rx="3" fill="{GREY}" fill-opacity="0.05"/>')
        # angedeutete Bäume/Sträucher
        for i, (fx, fy, r) in enumerate(right_band.get("trees", [(0.35, 0.16, 22), (0.62, 0.40, 16), (0.38, 0.68, 26), (0.66, 0.88, 18)])):
            tx, ty = rx + fx * rb_w, pad + fy * (H - 2 * pad)
            env.append(f'<circle cx="{tx:.0f}" cy="{ty:.0f}" r="{r}" fill="{GREY}" fill-opacity="0.06" stroke="{GREY}" stroke-opacity="0.22" stroke-width="1.2"/>')
        lbl = escape(right_band.get("label", "GARTEN"))
        gx = rx + rb_w / 2
        env.append(f'<text x="{gx:.0f}" y="{H/2:.0f}" transform="rotate(-90 {gx:.0f} {H/2:.0f})" text-anchor="middle" '
                   f'font-size="13" letter-spacing="3" fill="{GREY}" fill-opacity="0.75">{lbl}</text>')
    # Nordpfeil oben rechts im Plangebiet
    nx_, ny_ = ax1 + gap_r / 2, pad + 26
    env.append(f'<g transform="translate({nx_:.0f} {ny_:.0f}) rotate({north_up_rotation})" fill="{GREY}" fill-opacity="0.7">'
               f'<path d="M0,-16 L6,8 L0,4 L-6,8 Z"/><text y="22" text-anchor="middle" font-size="10">N</text></g>')
    env.append('</g>')
    o += env

    # ---- Raumflächen --------------------------------------------------------
    o.append(f'<g id="raeume" fill="{GREY}" stroke="none">')
    for r in rooms:
        if r.get("outline") or r["name"] in faint:
            op = 0.04 if r["name"] in faint else 0.10
            dash = ' stroke-dasharray="6 5"' if r["name"] in faint else ""
            o.append(f'<polygon id="raum-{slug(r["name"])}" points="{P(r["polygon"])}" fill-opacity="{op}" '
                     f'stroke="{GREY}" stroke-opacity="0.55" stroke-width="1.5"{dash}/>')
        else:
            o.append(f'<polygon id="raum-{slug(r["name"])}" points="{P(r["polygon"])}" fill-opacity="0.045"/>')
    o.append('</g>')

    # ---- Wände (Gruppen-Opacity -> keine dunklen Überlagerungen) ------------
    ext_ids = {w["id"] for w in plan.get("walls", []) if w.get("type") == "exterior"}
    ext_polys, int_polys = [], []
    walls = {w["id"]: w for w in plan.get("walls", [])}
    ops_by_wall = {}
    for op in plan.get("openings", []):
        if "wall" in op:
            ops_by_wall.setdefault(op["wall"], []).append(op)
    for wid, w in walls.items():
        polys, *_ = rp.wall_segments(w, ops_by_wall.get(wid, []))
        (ext_polys if wid in ext_ids else int_polys).extend(polys)
    for wp in plan.get("wall_polygons", []):
        (int_polys if wp.get("type") != "exterior" else ext_polys).append(wp["polygon"])
    o.append(f'<g id="aussenwaende" fill="{GREY}" opacity="0.85">')
    o += [f'<polygon points="{P(p)}"/>' for p in ext_polys]
    o.append('</g>')
    o.append(f'<g id="innenwaende" fill="{GREY}" opacity="0.45">')
    o += [f'<polygon points="{P(p)}"/>' for p in int_polys]
    o.append('</g>')

    # ---- Fenster und Türen --------------------------------------------------
    positions = {"format": {"width": W, "height": H, "px_per_m": round(S, 2)}, "rooms": [], "windows": [], "doors": []}
    pct = lambda p: {"left": f"{T(p)[0]/W*100:.1f}%", "top": f"{T(p)[1]/H*100:.1f}%"}
    o.append(f'<g id="fenster" stroke="{GREY}" fill="none">')
    door_svg = [f'<g id="tueren" fill="none" stroke="{GREY}">']
    for op in plan.get("openings", []):
        frame = op["host"] if "host" in op else walls[op["wall"]]
        if "host" in op:
            u, n, band = rp.host_frame(frame)
        else:
            _, u, n, band = rp.wall_segments(frame, [])
        a = frame["a"]
        s, w_ = op["offset"], op["width"]
        lo, hi = band
        p = lambda d, off: (a[0] + u[0] * d + n[0] * off, a[1] + u[1] * d + n[1] * off)
        mid = (lo + hi) / 2
        c = p(s + w_ / 2, mid)
        vertical = abs(u[1]) > abs(u[0])
        entry = {"id": op.get("id"), "name": op.get("name", ""), **pct(c),
                 "orientation": "vertikal" if vertical else "horizontal",
                 "length_px": round(w_ * S, 1)}
        if op["type"] == "window":
            (sx, sy), (ex, ey) = T(p(s, mid)), T(p(s + w_, mid))
            o.append(f'<line x1="{sx:.1f}" y1="{sy:.1f}" x2="{ex:.1f}" y2="{ey:.1f}" stroke-width="2" stroke-opacity="0.9"/>')
            for d in (s, s + w_):
                (jx, jy), (kx, ky) = T(p(d, lo)), T(p(d, hi))
                o.append(f'<line x1="{jx:.1f}" y1="{jy:.1f}" x2="{kx:.1f}" y2="{ky:.1f}" stroke-width="1" stroke-opacity="0.6"/>')
            positions["windows"].append(entry)
        else:
            lines, arcs = rp.opening_geometry(frame, op, u, n, band)
            for (la, lb_) in lines:
                (sx, sy), (ex, ey) = T(la), T(lb_)
                door_svg.append(f'<line x1="{sx:.1f}" y1="{sy:.1f}" x2="{ex:.1f}" y2="{ey:.1f}" stroke-width="1.6" stroke-opacity="0.65"/>')
            for arc in arcs:
                (fx, fy), (ex, ey) = T(arc["from"]), T(arc["to"])
                cc = arc["center"]
                cross = (arc["from"][0] - cc[0]) * (arc["to"][1] - cc[1]) - (arc["from"][1] - cc[1]) * (arc["to"][0] - cc[0])
                sweep = 1 if cross < 0 else 0
                r = arc["radius"] * S
                door_svg.append(f'<path d="M{fx:.1f},{fy:.1f} A{r:.1f},{r:.1f} 0 0 {sweep} {ex:.1f},{ey:.1f}" '
                                f'stroke-width="1" stroke-opacity="0.4" stroke-dasharray="3 3"/>')
            positions["doors"].append(entry)
    o.append('</g>')
    door_svg.append('</g>')
    o += door_svg

    # ---- Beschriftung (oben links im Raum, Mitte bleibt frei für Badges) ----
    o.append(f'<g id="beschriftung" fill="{GREY}">')
    for r in rooms:
        name = rename.get(r["name"], r["name"])
        rxs = [q[0] for q in r["polygon"]]
        rys = [q[1] for q in r["polygon"]]
        (bx0, by0), (bx1, by1) = T((min(rxs), max(rys))), T((max(rxs), min(rys)))
        bw, bh = bx1 - bx0, by1 - by0
        # Mittelpunkt für Badges: Mitte der Bounding-Box, sonst Schwerpunkt
        cxy = cfg.get("badge_pos", {}).get(r["name"]) or visual_center(r["polygon"])
        positions["rooms"].append({"id": slug(name), "name": name, **pct(cxy),
                                   "area_m2": round(rp.shoelace(r["polygon"]), 2)})
        size = 13
        outline = r.get("outline") or r["name"] in faint
        op_ = 0.75 if outline else 0.8
        fixed = cfg.get("label_pos", {}).get(r["name"])
        if fixed:  # feste Position (Meter, linke Grundlinie) aus der Konfiguration
            fx_, fy_ = T(fixed)
            o.append(f'<text x="{fx_:.1f}" y="{fy_:.1f}" font-size="{size}" fill-opacity="{op_}">{escape(name)}</text>')
        elif bw >= text_width(name, size) + 20:
            o.append(f'<text x="{bx0+10:.1f}" y="{by0+22:.1f}" font-size="{size}" fill-opacity="{op_}">{escape(name)}</text>')
        elif bh >= text_width(name, size) + 20:  # schmaler, hoher Raum: senkrecht
            o.append(f'<text x="{bx0+18:.1f}" y="{by1-10:.1f}" font-size="{size}" fill-opacity="{op_}" '
                     f'transform="rotate(-90 {bx0+18:.1f} {by1-10:.1f})">{escape(name)}</text>')
        else:
            size = max(9, int((bw - 12) / (0.56 * len(name))))
            o.append(f'<text x="{bx0+6:.1f}" y="{by0+18:.1f}" font-size="{size}" fill-opacity="{op_}">{escape(name)}</text>')
    o.append('</g>')
    o.append('</svg>')

    out_svg = cfg_path.parent / cfg.get("output", "dashboard.svg")
    out_svg.write_text("\n".join(o) + "\n", encoding="utf-8")
    out_pos = out_svg.with_name(out_svg.stem + "_positionen.json")
    out_pos.write_text(json.dumps(positions, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{out_svg.relative_to(ROOT)}  ({W}×{H}, {S:.1f} px/m)")
    print(f"{out_pos.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
