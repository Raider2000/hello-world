# Grundrisse

Maßgetreue Neuzeichnungen der Bestandsgrundrisse als offene Formate (SVG + DXF).

| Objekt | Ordner |
|--------|--------|
| KFS31  | [plans/KFS31](plans/KFS31) |
| WBS3   | [plans/WBS3](plans/WBS3)   |
| RBS25  | [plans/RBS25](plans/RBS25) |
| KSS29  | [plans/KSS29](plans/KSS29) |

Arbeitsweise, Koordinatensystem, Layer und Schema: [docs/ZEICHENRICHTLINIE.md](docs/ZEICHENRICHTLINIE.md).
Renderer: `python3 tools/render_plan.py --all`.

3D-Modell (glTF + Browser-Raumplaner mit Sonnenstand): `python3 tools/build_3d.py plans/<Objekt>/geometrie/<Geschoss>.json --viewer`,
Blender-Szene: `tools/blender_szene.py`. Beispiel: [plans/KSS29/3d](plans/KSS29/3d/README.md).
