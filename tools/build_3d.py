#!/usr/bin/env python3
"""3D-Modell aus der Grundriss-Geometrie: geometrie/<Geschoss>.json -> glTF-Binärdatei (.glb).

Aufruf:
    python3 tools/build_3d.py plans/KSS29/geometrie/OG1.json
    python3 tools/build_3d.py plans/KSS29/geometrie/OG1.json --viewer

Ausgabe:
    plans/<Objekt>/3d/<Objekt>_<Geschoss>.glb   Modell (Meter, Y oben, -Z = Plan-Nord)
    plans/<Objekt>/3d/<Objekt>_<Geschoss>.html  Browser-Ansicht mit eingebettetem Modell (--viewer)

Das GLB ist ein offenes Format: Blender (Datei > Importieren > glTF 2.0), three.js, SketchUp,
Unity usw. lesen es direkt. Jeder Knoten trägt einen sprechenden Namen (Wand_*, Boden_*,
Tuer_*, Fenster_*, Licht_*), Materialnamen sind einheitlich (Wand_weiss, Boden_Parkett, ...).
Höhen und Annahmen: siehe HOEHEN unten und plans/<Objekt>/3d/README.md.
Optional: plans/<Objekt>/3d/ausstattung.json (Deckenspots je Raum, Bodenfarben, Balkonbrüstung).
Nur Standardbibliothek, keine Abhängigkeiten.
"""
from __future__ import annotations

import argparse
import base64
import json
import math
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ----------------------------------------------------------------- Höhen (m über OKFF OG)
# Werkplan: OKFF OG +2,90, OK Rohdecke +2,75 -> Fußbodenaufbau 0,15.
# Fenster: BRH/STH im Plan absolut (z. B. BRH +3,60 / STH +5,13) -> minus 2,90.
# Innentüren: Rohbaurichtmaß 2,135 ab Rohdecke -> 2,135 - 0,15 = 1,985 über OKFF.
HOEHEN = {
    "okff_absolut": 2.90,        # OKFF OG über ±0,00
    "aufbau": 0.15,              # Estrich + Belag
    "raumhoehe": 2.55,           # ANNAHME: Geschosshöhe 2,90 − Decke 0,20 − Aufbau 0,15
    "decke_oben": 2.90,          # OK Decke über OG = OKFF DG (Annahme)
    "rohdecke_unten": -0.35,     # UK Decke über EG (Annahme 0,20 Decke)
    "eg_unten": -2.90,           # Gelände ≈ OKFF EG (Annahme)
    "gelaender": 1.00,           # Geländerhöhe Balkone (Annahme)
    "tuer_innen": 2.135 - 0.15,  # lichte Höhe Innentüren über OKFF
}

FARBEN = {  # Materialname -> (RGBA linear-sRGB grob, metallic, roughness)
    "Wand_weiss": ((0.92, 0.92, 0.91, 1.0), 0.0, 0.9),
    "Decke_weiss": ((0.94, 0.94, 0.94, 1.0), 0.0, 0.95),
    "Tuer_weiss": ((0.95, 0.95, 0.95, 1.0), 0.0, 0.45),
    "Zarge_weiss": ((0.93, 0.93, 0.93, 1.0), 0.0, 0.5),
    "Rahmen_weiss": ((0.93, 0.93, 0.93, 1.0), 0.0, 0.5),
    "Fensterbank": ((0.85, 0.85, 0.83, 1.0), 0.0, 0.4),
    "Glas": ((0.80, 0.90, 0.95, 0.15), 0.0, 0.05),
    "Boden_Parkett": ((0.55, 0.38, 0.22, 1.0), 0.0, 0.6),
    "Boden_Fliese": ((0.62, 0.60, 0.57, 1.0), 0.0, 0.5),
    "Boden_Treppenhaus": ((0.50, 0.50, 0.50, 1.0), 0.0, 0.7),
    "Balkon_Beton": ((0.60, 0.60, 0.58, 1.0), 0.0, 0.9),
    "Gelaender_Metall": ((0.25, 0.26, 0.28, 1.0), 0.6, 0.4),
    "Bruestung_Platte": ((0.55, 0.55, 0.53, 1.0), 0.0, 0.8),
    "Fassade_Putz": ((0.86, 0.84, 0.80, 1.0), 0.0, 0.95),
    "Dach_Begruent": ((0.20, 0.32, 0.12, 1.0), 0.0, 1.0),
    "Gelaende_Rasen": ((0.18, 0.30, 0.10, 1.0), 0.0, 1.0),
    "Kamin": ((0.90, 0.90, 0.89, 1.0), 0.0, 0.9),
    "Leuchte": ((1.0, 0.97, 0.9, 1.0), 0.0, 0.3),
}

# Bodenbelag nach Raumname (Werkplan-Notizen: Parkett / Feinsteinzeug)
BELAG = {
    "Badezimmer": "Boden_Fliese", "Toilette": "Boden_Fliese", "Flur": "Boden_Fliese",
    "Garderobe": "Boden_Fliese", "Treppenhaus": "Boden_Treppenhaus",
}
KEIN_LICHT = {"Treppenhaus"}


# ----------------------------------------------------------------- Geometrie-Helfer
def poly_area(p):
    return 0.5 * sum(p[i][0] * p[(i + 1) % len(p)][1] - p[(i + 1) % len(p)][0] * p[i][1] for i in range(len(p)))


def ccw(p):
    return list(p) if poly_area(p) > 0 else list(reversed(p))


def triangulate(poly):
    """Ear-Clipping für einfache Polygone (CCW). Gibt Indextripel zurück."""
    idx = list(range(len(poly)))
    tris = []

    def is_convex(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]) > 1e-12

    def inside(p, a, b, c):
        d1 = (p[0] - b[0]) * (a[1] - b[1]) - (a[0] - b[0]) * (p[1] - b[1])
        d2 = (p[0] - c[0]) * (b[1] - c[1]) - (b[0] - c[0]) * (p[1] - c[1])
        d3 = (p[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (p[1] - a[1])
        neg = d1 < -1e-12 or d2 < -1e-12 or d3 < -1e-12
        pos = d1 > 1e-12 or d2 > 1e-12 or d3 > 1e-12
        return not (neg and pos)

    guard = 0
    while len(idx) > 3 and guard < 10000:
        guard += 1
        for k in range(len(idx)):
            i0, i1, i2 = idx[k - 1], idx[k], idx[(k + 1) % len(idx)]
            a, b, c = poly[i0], poly[i1], poly[i2]
            if not is_convex(a, b, c):
                continue
            if any(inside(poly[j], a, b, c) for j in idx if j not in (i0, i1, i2)):
                continue
            tris.append((i0, i1, i2))
            idx.pop(k)
            break
        else:  # degeneriert (kollineare Punkte): kollinearen Punkt entfernen
            idx.pop(0)
    if len(idx) == 3:
        tris.append(tuple(idx))
    return tris


class Mesh:
    """Sammelt Dreiecke je Material. Koordinaten in Plan-System (x Ost, y Nord, z Höhe)."""

    def __init__(self):
        self.prims: dict[str, dict] = {}

    def _p(self, mat):
        return self.prims.setdefault(mat, {"pos": [], "nrm": [], "uv": [], "idx": []})

    def tri(self, mat, pts, uvs, want_normal=None):
        a, b, c = pts
        u = [b[i] - a[i] for i in range(3)]
        v = [c[i] - a[i] for i in range(3)]
        n = [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]]
        ln = math.sqrt(sum(x * x for x in n))
        if ln < 1e-12:
            return
        n = [x / ln for x in n]
        if want_normal is not None and sum(n[i] * want_normal[i] for i in range(3)) < 0:
            pts, uvs, n = [a, c, b], [uvs[0], uvs[2], uvs[1]], [-x for x in n]
        p = self._p(mat)
        base = len(p["pos"])
        for q, t in zip(pts, uvs):
            p["pos"].append(q)
            p["nrm"].append(n)
            p["uv"].append(t)
        p["idx"].extend([base, base + 1, base + 2])

    def quad(self, mat, q, uvs, want_normal):
        self.tri(mat, [q[0], q[1], q[2]], [uvs[0], uvs[1], uvs[2]], want_normal)
        self.tri(mat, [q[0], q[2], q[3]], [uvs[0], uvs[2], uvs[3]], want_normal)

    def prism(self, mat, poly, z0, z1, caps=True, side_mat=None):
        """Extrudiert ein Plan-Polygon von z0 bis z1 (Normalen nach außen)."""
        poly = ccw(poly)
        if z1 - z0 < 1e-6:
            return
        side_mat = side_mat or mat
        n = len(poly)
        s = 0.0
        for i in range(n):
            a, b = poly[i], poly[(i + 1) % n]
            dx, dy = b[0] - a[0], b[1] - a[1]
            ln = math.hypot(dx, dy)
            if ln < 1e-9:
                continue
            out = (dy / ln, -dx / ln, 0.0)
            self.quad(side_mat,
                      [(a[0], a[1], z0), (b[0], b[1], z0), (b[0], b[1], z1), (a[0], a[1], z1)],
                      [(s, z0), (s + ln, z0), (s + ln, z1), (s, z1)], out)
            s += ln
        if caps:
            for t in triangulate(poly):
                pts = [poly[i] for i in t]
                self.tri(mat, [(p[0], p[1], z1) for p in pts], [(p[0], p[1]) for p in pts], (0, 0, 1))
                self.tri(mat, [(p[0], p[1], z0) for p in pts], [(p[0], p[1]) for p in pts], (0, 0, -1))

    def box_along(self, mat, a, u, s0, s1, off0, off1, z0, z1):
        """Quader entlang Richtung u ab Punkt a: Länge s0..s1, quer off0..off1 (links von u)."""
        nx, ny = -u[1], u[0]
        pts = [
            (a[0] + u[0] * s0 + nx * off0, a[1] + u[1] * s0 + ny * off0),
            (a[0] + u[0] * s1 + nx * off0, a[1] + u[1] * s1 + ny * off0),
            (a[0] + u[0] * s1 + nx * off1, a[1] + u[1] * s1 + ny * off1),
            (a[0] + u[0] * s0 + nx * off1, a[1] + u[1] * s0 + ny * off1),
        ]
        self.prism(mat, pts, z0, z1)

    def empty(self):
        return not any(p["idx"] for p in self.prims.values())


# ----------------------------------------------------------------- glTF-Writer
class Gltf:
    def __init__(self):
        self.bin = bytearray()
        self.doc = {
            "asset": {"version": "2.0", "generator": "tools/build_3d.py"},
            "scene": 0, "scenes": [{"name": "Szene", "nodes": []}],
            "nodes": [], "meshes": [], "materials": [], "accessors": [], "bufferViews": [],
            "buffers": [{"byteLength": 0}],
        }
        self.mat_index: dict[str, int] = {}
        self.lights: list = []

    def material(self, name):
        if name not in self.mat_index:
            rgba, metal, rough = FARBEN[name]
            m = {"name": name, "pbrMetallicRoughness": {
                "baseColorFactor": list(rgba), "metallicFactor": metal, "roughnessFactor": rough}}
            if rgba[3] < 1.0:
                m["alphaMode"] = "BLEND"
                m["doubleSided"] = True
            if name == "Leuchte":
                m["emissiveFactor"] = [1.0, 0.92, 0.75]
            self.mat_index[name] = len(self.doc["materials"])
            self.doc["materials"].append(m)
        return self.mat_index[name]

    def _view(self, data: bytes, target=None):
        while len(self.bin) % 4:
            self.bin.append(0)
        off = len(self.bin)
        self.bin.extend(data)
        v = {"buffer": 0, "byteOffset": off, "byteLength": len(data)}
        if target:
            v["target"] = target
        self.doc["bufferViews"].append(v)
        return len(self.doc["bufferViews"]) - 1

    def _acc(self, flat, comp, typ, count, minmax=None, target=34962):
        fmt = {"5126": "f", "5125": "I"}[str(comp)]
        view = self._view(struct.pack("<%d%s" % (len(flat), fmt), *flat), target)
        a = {"bufferView": view, "componentType": comp, "count": count, "type": typ}
        if minmax:
            a["min"], a["max"] = minmax
        self.doc["accessors"].append(a)
        return len(self.doc["accessors"]) - 1

    def mesh(self, name, mesh: Mesh, origin=(0.0, 0.0, 0.0)):
        prims = []
        for mat, p in mesh.prims.items():
            if not p["idx"]:
                continue
            # Plan (x, y, z) -> glTF (x, z, -y), relativ zum Knotenursprung
            pos = [(q[0] - origin[0], q[2] - origin[2], -(q[1] - origin[1])) for q in p["pos"]]
            nrm = [(n[0], n[2], -n[1]) for n in p["nrm"]]
            flat = [c for q in pos for c in q]
            mn = [min(q[i] for q in pos) for i in range(3)]
            mx = [max(q[i] for q in pos) for i in range(3)]
            ap = self._acc(flat, 5126, "VEC3", len(pos), (mn, mx))
            an = self._acc([c for n in nrm for c in n], 5126, "VEC3", len(nrm))
            au = self._acc([c for t in p["uv"] for c in (t[0], -t[1])], 5126, "VEC2", len(p["uv"]))
            ai = self._acc(p["idx"], 5125, "SCALAR", len(p["idx"]), target=34963)
            prims.append({"attributes": {"POSITION": ap, "NORMAL": an, "TEXCOORD_0": au},
                          "indices": ai, "material": self.material(mat)})
        self.doc["meshes"].append({"name": name, "primitives": prims})
        return len(self.doc["meshes"]) - 1

    def node(self, name, mesh: Mesh | None = None, parent=None, origin=(0.0, 0.0, 0.0),
             yaw=0.0, extras=None, light=None, rotation=None):
        n = {"name": name}
        if mesh is not None and not mesh.empty():
            n["mesh"] = self.mesh(name, mesh)  # Netz in Knoten-Koordinaten
        if any(origin):
            n["translation"] = [origin[0], origin[2], -origin[1]]
        if yaw:
            n["rotation"] = [0.0, math.sin(yaw / 2), 0.0, math.cos(yaw / 2)]
        if rotation:
            n["rotation"] = list(rotation)
        if extras:
            n["extras"] = extras
        if light is not None:
            n["extensions"] = {"KHR_lights_punctual": {"light": light}}
        self.doc["nodes"].append(n)
        i = len(self.doc["nodes"]) - 1
        if parent is None:
            self.doc["scenes"][0]["nodes"].append(i)
        else:
            self.doc["nodes"][parent].setdefault("children", []).append(i)
        return i

    def point_light(self, name, lumen=1000, color=(1.0, 0.85, 0.65)):
        self.lights.append({"name": name, "type": "point", "color": list(color),
                            "intensity": round(lumen / (4 * math.pi), 2), "range": 12.0})
        return len(self.lights) - 1

    def spot_light(self, name, lumen=400, beam_deg=60, color=(1.0, 0.85, 0.65)):
        """Einbauspot, strahlt entlang -Z des Knotens. Lichtstärke aus Lichtstrom und Kegel."""
        outer = math.radians(beam_deg / 2)
        cd = lumen / (2 * math.pi * (1 - math.cos(outer)))
        self.lights.append({"name": name, "type": "spot", "color": list(color), "intensity": round(cd, 1),
                            "range": 8.0, "spot": {"innerConeAngle": round(outer * 0.55, 4),
                                                   "outerConeAngle": round(outer, 4)}})
        return len(self.lights) - 1

    def glb(self) -> bytes:
        if self.lights:
            self.doc.setdefault("extensionsUsed", []).append("KHR_lights_punctual")
            self.doc["extensions"] = {"KHR_lights_punctual": {"lights": self.lights}}
        while len(self.bin) % 4:
            self.bin.append(0)
        self.doc["buffers"][0]["byteLength"] = len(self.bin)
        js = json.dumps(self.doc, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        while len(js) % 4:
            js += b" "
        total = 12 + 8 + len(js) + 8 + len(self.bin)
        return (struct.pack("<III", 0x46546C67, 2, total) + struct.pack("<II", len(js), 0x4E4F534A) + js
                + struct.pack("<II", len(self.bin), 0x004E4942) + bytes(self.bin))


# ----------------------------------------------------------------- Modellaufbau
def parse_num(s):
    return float(s.replace(",", "."))


def opening_heights(o, wall):
    """(UK, OK) einer Öffnung über OKFF aus dem Namen (BRH/STH bzw. Breite/Höhe)."""
    name = o.get("name", "")
    if "z0" in o and "z1" in o:
        return o["z0"], o["z1"]
    m = re.search(r"BRH \+([\d,]+), STH \+([\d,]+)", name)
    if o["type"] == "window" and m:
        return parse_num(m.group(1)) - HOEHEN["okff_absolut"], parse_num(m.group(2)) - HOEHEN["okff_absolut"]
    m = re.search(r"\d,\d+/(\d,\d+)", name)
    h = parse_num(m.group(1)) if m else 2.135
    if o["type"] == "door":
        if wall["type"] == "exterior":   # Balkon-/Loggiatür, Höhe ab OKFF bis STH
            return 0.0, min(h, 2.23)
        return 0.0, h - HOEHEN["aufbau"]
    return 0.70, 2.23


def wall_frame(w):
    (ax, ay), (bx, by) = w["a"], w["b"]
    ln = math.hypot(bx - ax, by - ay)
    u = ((bx - ax) / ln, (by - ay) / ln)
    t = w["thickness"]
    al = w.get("align", "center")
    off0, off1 = {"center": (-t / 2, t / 2), "left": (0.0, t), "right": (-t, 0.0)}[al]
    return (ax, ay), u, ln, off0, off1


def srgb_to_linear(c):
    c = c / 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def apply_ausstattung(aus: dict):
    """Farben aus ausstattung.json in die Materialtabelle übernehmen."""
    for mat, d in (aus.get("boeden") or {}).items():
        if mat in FARBEN and "farbe_srgb" in d:
            _, metal, rough = FARBEN[mat]
            FARBEN[mat] = (tuple(srgb_to_linear(v) for v in d["farbe_srgb"]) + (1.0,), metal, rough)
    br = aus.get("balkonbruestung") or {}
    if "farbe_srgb" in br:
        FARBEN["Bruestung_Platte"] = (tuple(srgb_to_linear(v) for v in br["farbe_srgb"]) + (1.0,), 0.0, 0.8)
    if "hoehe" in br:
        HOEHEN["gelaender"] = br["hoehe"]


def build(geo: dict, aus: dict | None = None) -> tuple[Gltf, dict]:
    aus = aus or {}
    apply_ausstattung(aus)
    spots = (aus.get("spots") or {}).get("raeume", {})
    spot_lm = (aus.get("spots") or {}).get("lumen", 400)
    spot_beam = (aus.get("spots") or {}).get("abstrahlwinkel", 60)
    panels = (aus.get("balkonbruestung") or {}).get("art") == "platten"
    g = Gltf()
    H = HOEHEN
    info = {"rooms": [], "openings": [], "bounds": None}
    root = g.node(f"{geo['object']}_{geo['floor']}", extras={
        "object": geo["object"], "floor": geo["floor"], "floor_name": geo.get("floor_name", ""),
        "hoehen": H, "achsen": "glTF: +X Ost, -Z Nord (Plan-y), +Y oben; Ursprung SW-Rohbauecke, Höhe 0 = OKFF"})
    walls = {w["id"]: w for w in geo["walls"]}
    ops_by_wall: dict[str, list] = {}
    for o in geo.get("openings", []):
        if "wall" in o:
            ops_by_wall.setdefault(o["wall"], []).append(o)

    # Außenmaße (für Decke, EG-Block, Fassade)
    ext = [w for w in geo["walls"] if w["type"] == "exterior"]
    xs = [c for w in ext for c in (w["a"][0], w["b"][0])]
    ys = [c for w in ext for c in (w["a"][1], w["b"][1])]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    info["bounds"] = [x0, y0, x1, y1]

    grp_w = g.node("Waende", parent=root)
    grp_o = g.node("Oeffnungen", parent=root)
    grp_f = g.node("Boeden", parent=root)
    grp_l = g.node("Leuchten", parent=root)
    grp_x = g.node("Umgebung", parent=root, extras={"context": True})

    # ---- Wände mit Öffnungen
    for w in geo["walls"]:
        a, u, ln, off0, off1 = wall_frame(w)
        exterior = w["type"] == "exterior"
        zb, zt = (H["rohdecke_unten"], H["decke_oben"]) if exterior else (-H["aufbau"], H["raumhoehe"])
        m = Mesh()
        mat = "Wand_weiss"
        cuts = []
        for o in ops_by_wall.get(w["id"], []):
            u0, u1 = opening_heights(o, w)
            cuts.append((o["offset"], o["offset"] + o["width"], max(u0, zb), min(u1, zt), o))
        cuts.sort(key=lambda c: c[0])
        pos = 0.0
        for s, e, cz0, cz1, o in cuts:
            if s > pos + 1e-6:
                m.box_along(mat, a, u, pos, s, off0, off1, zb, zt)
            if cz1 <= cz0:  # Öffnung außerhalb des Geschosses (z. B. Treppenhausfenster über Podest)
                m.box_along(mat, a, u, s, e, off0, off1, zb, zt)
            else:
                m.box_along(mat, a, u, s, e, off0, off1, zb, cz0)
                m.box_along(mat, a, u, s, e, off0, off1, cz1, zt)
            pos = max(pos, e)
        if pos < ln - 1e-6:
            m.box_along(mat, a, u, pos, ln, off0, off1, zb, zt)
        g.node(f"Wand_{w['id']}", m, parent=grp_w, extras={"wall": w["id"], "type": w["type"], "solid": True})

        # ---- Öffnungen: Fenster, Balkontüren, Türen
        for s, e, cz0, cz1, o in cuts:
            if cz1 <= cz0:
                continue
            width = e - s
            mid = (a[0] + u[0] * (s + e) / 2, a[1] + u[1] * (s + e) / 2)
            inward = None
            info["openings"].append({"id": o["id"], "type": o["type"], "wall": w["id"],
                                     "exterior": exterior, "center": [round(mid[0], 3), round(mid[1], 3)],
                                     "dir": [round(u[0], 4), round(u[1], 4)], "width": round(width, 3),
                                     "z0": round(cz0, 3), "z1": round(cz1, 3),
                                     "thickness": w["thickness"],
                                     "inside": inner_side(geo, mid, u, w["thickness"]) if exterior else 0})
            fm = Mesh()
            fr = 0.06
            if exterior:
                # Rahmen + Glas in Wandmitte, Fensterbank innen
                c0, c1 = (off0 + off1) / 2 - 0.035, (off0 + off1) / 2 + 0.035
                fm.box_along("Rahmen_weiss", a, u, s, s + fr, c0, c1, cz0, cz1)
                fm.box_along("Rahmen_weiss", a, u, e - fr, e, c0, c1, cz0, cz1)
                fm.box_along("Rahmen_weiss", a, u, s + fr, e - fr, c0, c1, cz1 - fr, cz1)
                fm.box_along("Rahmen_weiss", a, u, s + fr, e - fr, c0, c1, cz0, cz0 + fr)
                if o["type"] == "window" and width > 1.5:   # zweiflügelig: Mittelpfosten
                    mm = (s + e) / 2
                    fm.box_along("Rahmen_weiss", a, u, mm - fr / 2, mm + fr / 2, c0, c1, cz0 + fr, cz1 - fr)
                if o["type"] == "door":   # Flügelrahmen bei Balkontür-Flügeln
                    fm.box_along("Rahmen_weiss", a, u, s + fr, e - fr, c0, c1, 0.9, 0.95)
                fm.box_along("Glas", a, u, s + fr, e - fr, -0.005 + (off0 + off1) / 2, 0.005 + (off0 + off1) / 2,
                             cz0 + fr, cz1 - fr)
                if o["type"] == "window" and cz0 > 0.2:
                    # Fensterbank auf der Innenseite: die Seite, auf der ein Raum liegt
                    side_in = inner_side(geo, mid, u, w["thickness"])
                    if side_in > 0:
                        fm.box_along("Fensterbank", a, u, s - 0.02, e + 0.02, off1 - 0.02, off1 + 0.20 - 0.02, cz0 - 0.02, cz0)
                    else:
                        fm.box_along("Fensterbank", a, u, s - 0.02, e + 0.02, off0 - 0.18, off0 + 0.02, cz0 - 0.02, cz0)
                kind = "Fenster" if o["type"] == "window" else "Balkontuer"
                g.node(f"{kind}_{o['id']}", fm, parent=grp_o,
                       extras={"opening": o["id"], "name": o.get("name", ""), "glass": True})
            else:
                # Innentür: Zarge (weiß) + Türblatt (weiß) an Drehpunkt, Standard 90° geöffnet
                zw = 0.03
                fm.box_along("Zarge_weiss", a, u, s, s + zw, off0 - 0.01, off1 + 0.01, 0, cz1)
                fm.box_along("Zarge_weiss", a, u, e - zw, e, off0 - 0.01, off1 + 0.01, 0, cz1)
                fm.box_along("Zarge_weiss", a, u, s, e, off0 - 0.01, off1 + 0.01, cz1 - zw, cz1)
                g.node(f"Zarge_{o['id']}", fm, parent=grp_o, extras={"opening": o["id"], "solid": True})
                hinge_at_start = o.get("hinge", "start") == "start"
                sgn = 1 if o.get("side", "left") == "left" else -1
                nrm = (-u[1] * sgn, u[0] * sgn)
                hs = s + zw if hinge_at_start else e - zw
                face = off1 if sgn > 0 else off0
                hp = (a[0] + u[0] * hs + (-u[1]) * face, a[1] + u[1] * hs + u[0] * face)
                close_dir = u if hinge_at_start else (-u[0], -u[1])
                yaw_closed = math.atan2(close_dir[1], close_dir[0])
                yaw_open = math.atan2(nrm[1], nrm[0])
                leaf_w = width - 2 * zw - 0.005
                lm = Mesh()
                # Blatt lokal: +x vom Band weg, Dicke 4 cm zur Aufschlagseite hin (lokal -y => Plan)
                leaf = [(0.0, -0.04), (leaf_w, -0.04), (leaf_w, 0.0), (0.0, 0.0)]
                glas = "Glasausschnitt" in o.get("name", "")
                if glas:
                    gx0, gx1, gz0, gz1 = 0.15, leaf_w - 0.15, 0.55, cz1 - 0.35
                    blat = [(0.0, gx0, 0.0, cz1 - zw - 0.005), (gx1, leaf_w, 0.0, cz1 - zw - 0.005),
                            (gx0, gx1, 0.0, gz0), (gx0, gx1, gz1, cz1 - zw - 0.005)]
                    for bx0, bx1, bz0, bz1 in blat:
                        lm.prism("Tuer_weiss", [(bx0, -0.04), (bx1, -0.04), (bx1, 0.0), (bx0, 0.0)], bz0, bz1)
                    lm.prism("Glas", [(gx0, -0.024), (gx1, -0.024), (gx1, -0.016), (gx0, -0.016)], gz0, gz1)
                else:
                    lm.prism("Tuer_weiss", leaf, 0.005, cz1 - zw - 0.005)
                # Drücker
                hx = leaf_w - 0.07
                lm.prism("Gelaender_Metall", [(hx - 0.12, 0.0), (hx, 0.0), (hx, 0.05), (hx - 0.12, 0.05)], 1.03, 1.05)
                lm.prism("Gelaender_Metall", [(hx - 0.12, -0.09), (hx, -0.09), (hx, -0.04), (hx - 0.12, -0.04)], 1.03, 1.05)
                # Blattdicke muss geschlossen zur Wandmitte zeigen (rechts von close_dir ist -y lokal)
                if (close_dir[1] * nrm[0] - close_dir[0] * nrm[1]) > 0:
                    for p in lm.prims.values():
                        p["pos"] = [(q[0], -q[1], q[2]) for q in p["pos"]]
                        p["nrm"] = [(n[0], -n[1], n[2]) for n in p["nrm"]]
                        p["idx"] = [i for t in range(0, len(p["idx"]), 3)
                                    for i in (p["idx"][t], p["idx"][t + 2], p["idx"][t + 1])]
                # Blatt so lokal orientieren, dass +x geschlossen zur Gegenzarge zeigt;
                # Öffnungswinkel = Drehung um den Drehpunkt (Knoten-Yaw).
                # Plan-Drehung um z ist glTF-Drehung um +Y mit gleichem Winkel.
                g.node(f"Tuer_{o['id']}", lm, parent=grp_o, origin=(hp[0], hp[1], 0.0), yaw=yaw_open,
                       extras={"door": o["id"], "name": o.get("name", ""), "yawClosed": yaw_closed,
                               "yawOpen": yaw_open, "solid": True})

    # ---- Wandpolygone (Kamin, Geländer)
    for wp in geo.get("wall_polygons", []):
        m = Mesh()
        if wp["id"].lower().startswith("gelaender"):
            railing(m, wp["polygon"], x0, x1, panels)
            g.node(f"Gelaender_{wp['id']}", m, parent=grp_x, extras={"solid": True})
        else:
            m.prism("Kamin", wp["polygon"], -H["aufbau"], H["decke_oben"])
            g.node(f"Bauteil_{wp['id']}", m, parent=grp_w, extras={"solid": True})

    # ---- Räume: Böden, Leuchten, Balkonplatten
    for r in geo.get("rooms", []):
        poly = r["polygon"]
        name = r["name"].strip()
        cx = r.get("label_pos", [sum(p[0] for p in poly) / len(poly), sum(p[1] for p in poly) / len(poly)])
        if not r.get("outline"):
            m = Mesh()
            mat = BELAG.get(name, "Boden_Parkett")
            m.prism(mat, poly, -0.02, 0.0, caps=True)
            area = abs(poly_area(poly))
            g.node(f"Boden_{name}", m, parent=grp_f, extras={
                "room": name, "area": round(area, 2), "area_stated": r.get("area_stated"),
                "label": cx, "floor": True})
            info["rooms"].append({"name": name, "label": cx, "area": round(area, 2),
                                  "area_stated": r.get("area_stated"), "polygon": poly})
            if name in spots:
                down = (-math.sqrt(0.5), 0.0, 0.0, math.sqrt(0.5))   # -Z des Lichts nach unten
                for i, (sx, sy) in enumerate(spots[name], 1):
                    li = g.spot_light(f"Spot_{name}_{i}", lumen=spot_lm, beam_deg=spot_beam)
                    sm = Mesh()
                    ring = [(0.045 * math.cos(k * math.pi / 8), 0.045 * math.sin(k * math.pi / 8)) for k in range(16)]
                    sm.prism("Leuchte", ring, -0.004, 0.0)
                    sn = g.node(f"Spot_{name}_{i}", sm, parent=grp_l, origin=(sx, sy, H["raumhoehe"]),
                                extras={"room": name, "lamp": True, "spot": True, "lumen": spot_lm})
                    g.node(f"Licht_{name}_{i}", None, parent=sn, origin=(0.0, 0.0, -0.01), light=li,
                           rotation=down, extras={"room": name})
            elif name not in KEIN_LICHT:
                cpt = centroid(poly) if point_in_poly(centroid(poly), poly) else cx
                lum = 600 + 60 * area     # grob: ~100 lx Grundlicht
                li = g.point_light(f"Licht_{name}", lumen=round(lum))
                lm = Mesh()
                circ = [(0.18 * math.cos(k * math.pi / 8), 0.18 * math.sin(k * math.pi / 8)) for k in range(16)]
                lm.prism("Leuchte", circ, -0.06, 0.0)
                ln_ = g.node(f"Leuchte_{name}", lm, parent=grp_l, origin=(cpt[0], cpt[1], H["raumhoehe"]),
                             extras={"room": name, "lamp": True, "lumen": round(lum)})
                g.node(f"Licht_{name}", None, parent=ln_, origin=(0.0, 0.0, -0.12), light=li,
                       extras={"room": name})
        elif name.startswith("Balkon"):
            # Platte bis Geländeraußenkante
            rail = nearest_railing(geo, poly)
            bb = bbox(poly + (rail or []))
            m = Mesh()
            m.prism("Balkon_Beton", rect(*bb), -0.22, -0.02)
            m.prism("Balkon_Beton", poly, -0.02, 0.0)
            g.node(f"Balkon_{name}", m, parent=grp_x, extras={"room": name, "floor": True, "area_stated": r.get("area_stated")})
            info["rooms"].append({"name": name, "label": cx, "area": round(abs(poly_area(poly)), 2),
                                  "area_stated": r.get("area_stated"), "polygon": poly, "outdoor": True})
        elif name == "Vordach":
            m = Mesh()
            m.prism("Balkon_Beton", poly, -0.37, -0.15)
            g.node("Vordach", m, parent=grp_x)
        elif name == "Flachdach":
            m = Mesh()
            m.prism("Dach_Begruent", poly, H["eg_unten"], -0.40)
            g.node("Flachdach_EG", m, parent=grp_x, extras={"context": True})
        elif name == "" and len(poly) == 4:
            bb = bbox(poly)
            if bb[2] - bb[0] < 0.5 and bb[3] - bb[1] < 1.0:   # Schacht E 20/20 im AR
                m = Mesh()
                m.prism("Wand_weiss", poly, 0.0, H["raumhoehe"])
                g.node("Schacht", m, parent=grp_w, extras={"solid": True})

    # ---- Decke über OG (ausblendbar), EG-Block, Gelände
    m = Mesh()
    m.prism("Decke_weiss", rect(x0, y0, x1, y1), H["raumhoehe"], H["decke_oben"])
    g.node("Decke", m, parent=root, extras={"ceiling": True})
    m = Mesh()
    m.prism("Wand_weiss", rect(x0, y0, x1, y1), H["rohdecke_unten"], -H["aufbau"] - 0.0001)
    m.prism("Fassade_Putz", rect(x0, y0, x1, y1), H["eg_unten"], H["rohdecke_unten"])
    g.node("EG_Baukoerper", m, parent=grp_x, extras={"context": True})
    m = Mesh()
    m.prism("Gelaende_Rasen", rect(x0 - 30, y0 - 30, x1 + 30, y1 + 30), H["eg_unten"] - 0.05, H["eg_unten"])
    g.node("Gelaende", m, parent=grp_x, extras={"context": True, "ground": True})
    return g, info


def railing(m: Mesh, poly, bx0, bx1, panels=False):
    """Brüstung an den Außenkanten der Geländer-Kontur (nicht an der Fassade):
    Stabgeländer oder geschlossene Plattenverkleidung (lichtundurchlässig)."""
    x0, y0, x1, y1 = bbox(poly)
    H = HOEHEN["gelaender"]
    t = 0.04
    edges = []
    near = lambda v, w: abs(v - w) < 0.02
    if not (near(x0, bx0) or near(x0, bx1)):
        edges.append(((x0 + 0.05, y0 + 0.05), (x0 + 0.05, y1 - 0.05)))
    if not (near(x1, bx0) or near(x1, bx1)):
        edges.append(((x1 - 0.05, y0 + 0.05), (x1 - 0.05, y1 - 0.05)))
    edges.append(((x0 + 0.05, y0 + 0.05), (x1 - 0.05, y0 + 0.05)))
    edges.append(((x0 + 0.05, y1 - 0.05), (x1 - 0.05, y1 - 0.05)))
    for (ax, ay), (bx, by) in edges:
        ln = math.hypot(bx - ax, by - ay)
        if ln < 0.05:
            continue
        u = ((bx - ax) / ln, (by - ay) / ln)
        if panels:
            m.box_along("Bruestung_Platte", (ax, ay), u, -0.05, ln + 0.05, -0.02, 0.02, -0.25, H)   # Platte
            m.box_along("Gelaender_Metall", (ax, ay), u, -0.05, ln + 0.05, -0.03, 0.03, H, H + 0.03)  # Abdeckung
            continue
        m.box_along("Gelaender_Metall", (ax, ay), u, 0, ln, -0.03, 0.03, H - 0.05, H)      # Handlauf
        m.box_along("Gelaender_Metall", (ax, ay), u, 0, ln, -0.015, 0.015, 0.08, 0.12)     # Untergurt
        n = max(1, int(ln / 0.12))
        for k in range(n + 1):
            s = k * ln / n
            m.box_along("Gelaender_Metall", (ax, ay), u, s - t / 4, s + t / 4, -t / 4, t / 4, 0.0, H - 0.05)


def nearest_railing(geo, poly):
    bb = bbox(poly)
    for wp in geo.get("wall_polygons", []):
        if wp["id"].lower().startswith("gelaender"):
            rb = bbox(wp["polygon"])
            if rb[0] <= bb[2] + 0.2 and rb[2] >= bb[0] - 0.2 and rb[1] <= bb[3] + 0.2 and rb[3] >= bb[1] - 0.2:
                return wp["polygon"]
    return None


def inner_side(geo, mid, u, t):
    """+1 wenn links der Wandachse (Laufrichtung) ein Innenraum liegt, sonst −1."""
    nx, ny = -u[1], u[0]
    p = (mid[0] + nx * (t / 2 + 0.3), mid[1] + ny * (t / 2 + 0.3))
    for r in geo.get("rooms", []):
        if not r.get("outline") and point_in_poly(p, r["polygon"]):
            return 1
    return -1


def bbox(pts):
    return (min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts))


def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def centroid(poly):
    a = poly_area(poly)
    cx = cy = 0.0
    for i in range(len(poly)):
        x0, y0 = poly[i]
        x1, y1 = poly[(i + 1) % len(poly)]
        f = x0 * y1 - x1 * y0
        cx += (x0 + x1) * f
        cy += (y0 + y1) * f
    return (cx / (6 * a), cy / (6 * a))


def point_in_poly(p, poly):
    x, y = p
    inside = False
    for i in range(len(poly)):
        x0, y0 = poly[i]
        x1, y1 = poly[(i + 1) % len(poly)]
        if (y0 > y) != (y1 > y) and x < (x1 - x0) * (y - y0) / (y1 - y0) + x0:
            inside = not inside
    return inside


# ----------------------------------------------------------------- Ausgabe
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("geometry", type=Path)
    ap.add_argument("--viewer", action="store_true", help="HTML-Ansicht mit eingebettetem Modell erzeugen")
    ap.add_argument("--out", type=Path, help="Ausgabeordner (Standard: plans/<Objekt>/3d)")
    args = ap.parse_args(argv)
    geo = json.loads(args.geometry.read_text(encoding="utf-8"))
    out = args.out or args.geometry.resolve().parent.parent / "3d"
    aus_path = out / "ausstattung.json"
    aus = json.loads(aus_path.read_text(encoding="utf-8")) if aus_path.exists() else {}
    if aus:
        print(f"Ausstattung: {aus_path}")
    g, info = build(geo, aus)
    info["ausstattung"] = {"boeden": {k: v.get("name", "") for k, v in (aus.get("boeden") or {}).items()},
                           "bruestung": (aus.get("balkonbruestung") or {}).get("art", "stabgelaender")}
    out.mkdir(parents=True, exist_ok=True)
    stem = f"{geo['object']}_{geo['floor']}"
    glb = g.glb()
    (out / f"{stem}.glb").write_bytes(glb)
    print(f"{out / (stem + '.glb')}: {len(glb) / 1024:.0f} KB, {len(g.doc['nodes'])} Knoten, "
          f"{len(g.doc['materials'])} Materialien, {len(g.lights)} Leuchten")
    if args.viewer:
        tpl = (ROOT / "tools" / "viewer3d" / "viewer.html").read_text(encoding="utf-8")
        meta = {"object": geo["object"], "floor": geo["floor"], "title": geo.get("floor_name", stem),
                "hoehen": HOEHEN, **info}
        html = (tpl.replace("/*__MODEL_B64__*/\"\"", json.dumps(base64.b64encode(glb).decode("ascii")))
                   .replace("/*__MODEL_META__*/{}", json.dumps(meta, ensure_ascii=False))
                   .replace("__TITLE__", f"{geo['object']} Raumplaner"))
        (out / f"{stem}.html").write_text(html, encoding="utf-8")
        print(f"{out / (stem + '.html')}: {len(html) / 1024:.0f} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
