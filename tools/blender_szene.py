"""Blender-Szene aus dem 3D-Modell: Sonne nach Ort, Datum und Uhrzeit, Himmel, Cycles, Kamera im Raum.

Aufruf (getestet mit Blender 5.2, sollte ab 3.6 laufen):
    blender --python tools/blender_szene.py -- plans/KSS29/3d/KSS29_OG1.glb --datum 2026-06-21 --zeit 16:00 --raum Wohnen
    blender -b --python tools/blender_szene.py -- plans/KSS29/3d/KSS29_OG1.glb --datum 2026-12-21 --zeit 10:00 \
            --raum Schlafzimmer --render /tmp/schlafzimmer_dez.png

Optionen:
    --datum JJJJ-MM-TT   Standard: 21. Juni des laufenden Jahres
    --zeit HH:MM         Ortszeit MEZ/MESZ (Sommerzeit wird automatisch berücksichtigt), Standard 12:00
    --breite / --laenge  Standort, Standard München (48,137 / 11,575)
    --nord GRAD          Nordabweichung des Plans im Uhrzeigersinn (wie im Browser-Viewer)
    --bedeckt            bedeckter Himmel statt Sonne
    --licht              Deckenleuchten einschalten
    --raum NAME          Kamera in diesen Raum stellen (Name wie im Grundriss, z. B. Wohnen, Küche)
    --render DATEI.png   Bild rendern und speichern (mit -b ohne Oberfläche)
    --samples N          Cycles-Samples, Standard 256
    --aufloesung BxH     Bildgröße, Standard 1920x1080

Auch für das GLB mit Möbeln aus dem Browser-Viewer („Modell mit Möbeln als GLB“) verwendbar.
Achsen nach dem glTF-Import: +X Ost, +Y Nord, +Z oben (Meter), Höhe 0 = Fertigfußboden.
Die Sonnenberechnung ist dieselbe wie im Viewer (SunCalc/NOAA, Genauigkeit ca. 0,1°).
"""
from __future__ import annotations

import argparse
import datetime as dt
import math
import sys


# --------------------------------------------------------------------------- Sonnenstand
def sun_position(utc: dt.datetime, lat: float, lon: float) -> tuple[float, float]:
    """(Azimut ab Nord im Uhrzeigersinn, Höhe) in Grad."""
    rad = math.pi / 180
    ms = utc.replace(tzinfo=dt.timezone.utc).timestamp() * 1000
    d = ms / 864e5 - 0.5 + 2440588 - 2451545
    M = rad * (357.5291 + 0.98560028 * d)
    C = rad * (1.9148 * math.sin(M) + 0.02 * math.sin(2 * M) + 0.0003 * math.sin(3 * M))
    L = M + C + rad * 102.9372 + math.pi
    e = rad * 23.4397
    dec = math.asin(math.sin(e) * math.sin(L))
    ra = math.atan2(math.sin(L) * math.cos(e), math.cos(L))
    H = rad * (280.16 + 360.9856235 * d) + lon * rad - ra
    phi = lat * rad
    el = math.asin(math.sin(phi) * math.sin(dec) + math.cos(phi) * math.cos(dec) * math.cos(H))
    az = math.atan2(math.sin(H), math.cos(H) * math.sin(phi) - math.tan(dec) * math.cos(phi)) + math.pi
    return (az / rad) % 360, el / rad


def local_to_utc(date: dt.date, hh: int, mm: int) -> tuple[dt.datetime, bool]:
    """MEZ/MESZ -> UTC (Sommerzeit: letzter Sonntag März bis letzter Sonntag Oktober, 01:00 UTC)."""
    def last_sunday(y, m):
        nxt = dt.date(y + (m == 12), m % 12 + 1, 1)
        last = nxt - dt.timedelta(days=1)
        return last - dt.timedelta(days=(last.weekday() + 1) % 7)
    y = date.year
    ds = dt.datetime.combine(last_sunday(y, 3), dt.time(1))
    de = dt.datetime.combine(last_sunday(y, 10), dt.time(1))
    local = dt.datetime.combine(date, dt.time(hh, mm))
    dst = ds <= local - dt.timedelta(hours=1) < de
    return local - dt.timedelta(hours=2 if dst else 1), dst


def parse(argv):
    ap = argparse.ArgumentParser(prog="blender --python tools/blender_szene.py --")
    ap.add_argument("glb")
    ap.add_argument("--datum", default=f"{dt.date.today().year}-06-21")
    ap.add_argument("--zeit", default="12:00")
    ap.add_argument("--breite", type=float, default=48.137)
    ap.add_argument("--laenge", type=float, default=11.575)
    ap.add_argument("--nord", type=float, default=0.0)
    ap.add_argument("--bedeckt", action="store_true")
    ap.add_argument("--licht", action="store_true")
    ap.add_argument("--raum")
    ap.add_argument("--render")
    ap.add_argument("--samples", type=int, default=256)
    ap.add_argument("--aufloesung", default="1920x1080", help="Bildgröße in Pixeln, z. B. 1280x720")
    return ap.parse_args(argv)


# --------------------------------------------------------------------------- Blender
def build_scene(a):
    import bpy
    from mathutils import Vector

    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=a.glb)
    scene = bpy.context.scene

    hh, mm = (int(v) for v in a.zeit.split(":"))
    utc, dst = local_to_utc(dt.date.fromisoformat(a.datum), hh, mm)
    az, el = sun_position(utc, a.breite, a.laenge)
    azp = math.radians(az + a.nord)   # Azimut im Plan-System (+Y = Plan-Nord)
    elr = math.radians(el)
    sun_dir = Vector((math.sin(azp) * math.cos(elr), math.cos(azp) * math.cos(elr), math.sin(elr)))
    print(f"Sonne {a.datum} {a.zeit} {'MESZ' if dst else 'MEZ'}: Azimut {az:.1f}°, Höhe {el:.1f}°")

    # Himmel (Nishita) ohne Sonnenscheibe, Sonne als eigene Lampe mit scharfen Schatten
    world = bpy.data.worlds.new("Himmel")
    scene.world = world
    if not getattr(world, "node_tree", None):
        world.use_nodes = True   # ab Blender 5 ohnehin aktiv
    nt = world.node_tree
    bg = nt.nodes["Background"]
    if a.bedeckt:
        bg.inputs["Color"].default_value = (0.8, 0.82, 0.85, 1)
        bg.inputs["Strength"].default_value = 1.2 * max(0.02, math.sin(max(elr, 0.02)))
    else:
        sky = nt.nodes.new("ShaderNodeTexSky")
        types = sky.bl_rna.properties["sky_type"].enum_items.keys()
        sky.sky_type = next(t for t in ("NISHITA", "MULTIPLE_SCATTERING", "SINGLE_SCATTERING") if t in types)
        sky.sun_disc = False
        sky.sun_elevation = max(elr, -0.1)
        sky.sun_rotation = math.pi - azp          # Cycles: Richtung (sin r, -cos r) -> Nord = π
        nt.links.new(sky.outputs["Color"], bg.inputs["Color"])
        bg.inputs["Strength"].default_value = 0.35

    if not a.bedeckt and el > -1:
        sun_data = bpy.data.lights.new("Sonne", type="SUN")
        sun_data.energy = 4.0 * max(0.0, min(1.0, (el + 1) / 10))
        sun_data.angle = math.radians(0.53)
        sun_obj = bpy.data.objects.new("Sonne", sun_data)
        scene.collection.objects.link(sun_obj)
        sun_obj.rotation_euler = sun_dir.to_track_quat("Z", "Y").to_euler()

    # Deckenleuchten aus dem Modell
    for ob in scene.objects:
        if ob.type == "LIGHT" and ob.name.startswith("Licht_"):
            ob.hide_render = ob.hide_viewport = not a.licht

    # Glas: transparent statt brechend. Brechendes Glas (Transmission) würde in Cycles
    # das direkte Sonnenlicht als Kaustik schlucken; Fensterglas lässt es fast ungehindert durch.
    for m in bpy.data.materials:
        if m.name.startswith("Glas") and m.node_tree:
            bsdf = m.node_tree.nodes.get("Principled BSDF")
            if bsdf:
                key = "Transmission Weight" if "Transmission Weight" in bsdf.inputs else "Transmission"
                bsdf.inputs[key].default_value = 0.0
                bsdf.inputs["Roughness"].default_value = 0.02
                bsdf.inputs["Alpha"].default_value = 0.08   # ca. 92 % Lichtdurchlass
            for lk in list(m.node_tree.links):              # Alpha aus Vertex-/Texturdaten lösen
                if lk.to_socket.name == "Alpha":
                    m.node_tree.links.remove(lk)

    # Kamera
    cam_data = bpy.data.cameras.new("Kamera")
    cam_data.lens = 16
    cam = bpy.data.objects.new("Kamera", cam_data)
    scene.collection.objects.link(cam)
    scene.camera = cam
    floor = None
    if a.raum:
        floor = next((o for o in scene.objects if o.name.replace("_", " ").startswith("Boden " + a.raum)), None)
        if floor is None:
            print(f"Raum '{a.raum}' nicht gefunden. Vorhanden:",
                  ", ".join(o.name[6:] for o in scene.objects if o.name.startswith("Boden_")))
    if floor is not None:
        bb = [floor.matrix_world @ Vector(c) for c in floor.bound_box]
        cx = sum(v.x for v in bb) / 8
        cy = sum(v.y for v in bb) / 8
        # von der fensterfernen Seite in Richtung Fenster schauen: nächstes Fenster suchen
        wins = [o for o in scene.objects if o.name.startswith(("Fenster_", "Balkontuer_"))]
        target = None
        if wins:
            def ctr(o):
                b = [o.matrix_world @ Vector(c) for c in o.bound_box]
                return Vector((sum(v.x for v in b) / 8, sum(v.y for v in b) / 8, 0))
            target = min((ctr(o) for o in wins), key=lambda p: (p - Vector((cx, cy, 0))).length)
        d = (target - Vector((cx, cy, 0))) if target else Vector((0, 1, 0))
        d.z = 0
        d.normalize()
        cam.location = (cx - d.x * 1.2, cy - d.y * 1.2, 1.6)
        cam.rotation_euler = (math.radians(88), 0, math.atan2(d.y, d.x) - math.pi / 2)
        # Decke sichtbar lassen (Innenraum), Kamera steht im Raum
    else:
        for o in scene.objects:
            if o.name == "Decke":
                o.hide_render = o.hide_viewport = True
        cam.location = (22, -14, 20)
        cam.rotation_euler = (math.radians(55), 0, math.radians(55))
        cam_data.lens = 28

    # Cycles
    scene.render.engine = "CYCLES"
    scene.cycles.samples = a.samples
    scene.cycles.use_denoising = True
    scene.render.resolution_x, scene.render.resolution_y = (int(v) for v in a.aufloesung.lower().split("x"))
    for vt in ("AgX", "Filmic"):
        try:
            scene.view_settings.view_transform = vt
            break
        except TypeError:
            continue
    scene.view_settings.exposure = 0.5 if (floor is not None) else 0.0
    if a.render:
        scene.render.filepath = a.render
        bpy.ops.render.render(write_still=True)
        print("gespeichert:", a.render)


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    args = parse(argv)
    try:
        import bpy  # noqa: F401
    except ImportError:   # außerhalb von Blender: nur Sonnenstand ausgeben (Test)
        hh, mm = (int(v) for v in args.zeit.split(":"))
        utc, dst = local_to_utc(dt.date.fromisoformat(args.datum), hh, mm)
        az, el = sun_position(utc, args.breite, args.laenge)
        print(f"{args.datum} {args.zeit} {'MESZ' if dst else 'MEZ'} (UTC {utc:%H:%M}): Azimut {az:.1f}°, Höhe {el:.1f}°")
        sys.exit(0)
    build_scene(args)
