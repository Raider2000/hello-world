# Grundrisse

Maßgetreue Neuzeichnungen der Bestandsgrundrisse als offene Formate (SVG + DXF), erzeugt aus je
einer Geometrie-JSON pro Geschoss. Originale liegen unverändert in `plans/<Objekt>/quelle/`.

| Objekt | Adresse | Geschosse | Grundlage |
|--------|---------|-----------|-----------|
| [KFS31](plans/KFS31) | Karl-Ferlemann-Straße 31 | KG, EG, OG1, OG2, DG | Scans 2010 (Raum/WE) + 1999 (Maße), WE 1 Stand 2026 |
| [KSS29](plans/KSS29) | Kastenssestraße 29 | OG1 | Werkplan-Scan (Baujahr 2020/21); [HA-Dashboard](plans/KSS29/dashboard) |
| [RBS25](plans/RBS25) | Reichenbachstraße 25, Augsburg | KG, EG, OG1, OG2, DG | Aufteilungsplan 2014 (Vektor), WE05 Sanierung 2026 |
| [WBS3](plans/WBS3)   | Weinbergstraße 3, Leipzig | OG1 | Vektorplan 19.09.2026, Teilungserklärung 1998 |

- Arbeitsweise, Koordinatensystem, Layer und Schema: [docs/ZEICHENRICHTLINIE.md](docs/ZEICHENRICHTLINIE.md)
- Pläne erzeugen: `pip install -r tools/requirements.txt` und `python3 tools/render_plan.py --all`
- Rot nummerierte Punkte in den Plänen sind angenommene oder ungeprüfte Werte (Legende unter dem Schriftfeld).
- 3D-Modell (glTF + Browser-Raumplaner mit Sonnenstand): `python3 tools/build_3d.py plans/<Objekt>/geometrie/<Geschoss>.json --viewer`,
  Blender-Szene: `tools/blender_szene.py`. Beispiel: [plans/KSS29/3d](plans/KSS29/3d/README.md).
