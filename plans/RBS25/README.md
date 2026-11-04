# RBS25 – Reichenbachstraße 25, Augsburg

## Quellen

| Datei | Inhalt | Planstand | Status |
|-------|--------|-----------|--------|
| `quelle/vorgaenger_WE05/build_plan.py` | Vorherige Neuzeichnung WE05 (2. OG), Geometrie in mm, A3 1:50 | 12.09.2026, WE05-GR-01 v1 | **neueste Fassung**, Grundlage |
| `quelle/vorgaenger_WE05/Pruefprotokoll.json` | Prüfprotokoll zur Vorgängerzeichnung (SHA-256 der Originalquellen) | 12.09.2026 | Referenz |
| `quelle/OG2_WE05_bestand_vektoren.json` | Vektordaten (pdfplumber) aus dem Bestandsplan WE05 mit Rückbau gelb, Bestand rot | – | Referenz/Abgleich |
| Grundriss 2. OG gesamt (WE5 + WE6, bemaßt) | Bild, nur im Chat geteilt | – | **fehlt als Datei** |
| Grundriss WE05 Istzustand (gelb/rot markiert) | Bild, nur im Chat geteilt | – | **fehlt als Datei** |

Originale laut Prüfprotokoll: `Grundriss WE05 ursprünglich bemaßt.pdf`, `Grundrisse.pdf`,
`Grundriss zweites OG Istzustand unbemaßt - Rohfassung.png`,
`Grundriss zweites OG vorheriger Planzustand bemaßt - Rohfassung.png`, `Grundriss_Rohfassun.png`.

## Geschosse

| Geschoss | Geometrie | SVG | DXF | Flächenprüfung |
|----------|-----------|-----|-----|----------------|
| OG2 (WE05, Zustand nach Sanierung) | `geometrie/OG2.json` | `ausgabe/RBS25_OG2.svg` | `ausgabe/RBS25_OG2.dxf` | Wohnen +0,2 %, Schlafen +0,3 %, Flur +0,5 % (alle < 3 %); Maßkette 3,25 / 0,15 / 3,21 / 0,24 = 6,85 m, Tiefe 9,84 m ✔ |

Transformation aus dem Vorgänger (mm, y nach unten) ins Repo-System (m, y nach oben,
Ursprung = linke untere Rohbau-Außenecke): `x_m = (x + 135) / 1000`, `y_m = (9840 − y) / 1000`.
Die 6,85-m-Kette liegt dadurch bei x = 0,135 … 6,985 m. Erzeugt mit `python3 tools/render_plan.py plans/RBS25/geometrie/OG2.json`.

## Offene Punkte

- **Balkon**: Geometrie des Vorgängers (3,00 × 2,50 m = 7,5 m²) widerspricht der Fläche 3,75 m² laut
  Gesamtplan 2. OG (4 Balkone übereinander). Gezeichnet ist die Vorgängergeometrie als Metallkonstruktion,
  ohne Flächenangabe und ohne Geländer; Maße ungeklärt.
- Essen (11,18 m²), Kochen (5,69 m²), Bad (7,91 m²) und Balkon haben keine gesicherte Plan-Fläche
  (`area_stated` fehlt); die Werte im Plan sind aus den Polygonen berechnet. Bad 5,58 m² und
  Kochen/Essen 11,77 m² gehören zum Vorzustand. Flur 3,69 m² nur als ca.-Wert aus einem Bild.
- Alle „ca.“-Maße (Küche 1,66; Bad 2,30; Durchgang 2,25; Raumtiefen 3,44 / 4,98 / 3,65; Balkon 3,00 / 2,50)
  stammen unverändert aus dem Vorgänger und sind in `unverified` geführt.
- Tragfähigkeit der erhaltenen Innenwände unbekannt: alle als `interior` geführt; Fassade und Treppenhaus-Trennwand
  als tragend. Maße der neuen Wände (Badtrennwand, Vorwände, zugemauerte Küchentür) nur aus dem Vorgänger.
- Sanitärobjekte, Waschmaschinenstellplatz nur als Notes (schematisch); Fensterbänke und Balkongeländer nicht gezeichnet.
- Die beiden Bilder (Gesamtplan 2. OG, Istzustand WE05) fehlen weiterhin als Datei.
- Weitere Geschosse/Wohnungen: keine Quellen vorhanden.
