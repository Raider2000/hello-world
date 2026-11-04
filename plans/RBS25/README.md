# RBS25 – Reichenbachstraße 25, Augsburg

## Quellen

| Datei | Inhalt | Planstand | Status |
|-------|--------|-----------|--------|
| `quelle/vorgaenger_WE05/build_plan.py` | Vorherige Neuzeichnung WE05 (2. OG), Geometrie in mm, A3 1:50 | 12.09.2026, WE05-GR-01 v1 | **neueste Fassung**, Grundlage |
| `quelle/vorgaenger_WE05/Pruefprotokoll.json` | Prüfprotokoll zur Vorgängerzeichnung (SHA-256 der Originalquellen) | 12.09.2026 | Referenz |
| `quelle/OG2_WE05_bestand_vektoren.json` | Vektordaten (pdfplumber) aus dem Bestandsplan WE05 mit Rückbau gelb, Bestand rot | – | Referenz/Abgleich |
| `quelle/20140801-Aufteilungsplan_Grundrisse_RB25.pdf` | Aufteilungsplan (Vektor-PDF, M 1:100): KG, EG mit Außenanlagen, 1. OG, 2. OG, DG | 01.08.2014 | **Grundlage aller Geschosse** (= „Grundrisse.pdf“ im Prüfprotokoll, SHA-256 identisch) |
| `quelle/Grundriss_WE05_urspruenglich_bemasst.pdf` | Brandschutznachweis Planungsbüro Kerl, 2. OG bemaßt | – | Maßquelle (SHA-256 identisch mit Prüfprotokoll) |
| `quelle/Grundrisse_Ansichten_Schnitte_RB25_Scan.pdf` | Scan, 2 S.: Grundrisse, Ansichten, Schnitt mit Stempel | – | Referenz |
| Rohfassungs-PNGs laut Prüfprotokoll (Istzustand gelb/rot, vorheriger Planzustand bemaßt) | nur als Bild im Chat geteilt | – | fehlen als Datei, inhaltlich durch die PDFs abgedeckt |

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

## Klärungen (Eigentümer, 04.11.2026)

- **Balkon WE05**: 3,00 × 2,50 m = 7,50 m² ist korrekt; für die Miete wird er zur Hälfte (3,75 m²) angesetzt.
- **Flächen Essen, Kochen, Bad**: kein neues Aufmaß; Flächen werden aus der Neuzeichnung berechnet und als „berechnet“ gekennzeichnet.
- **Tragende Wände**: nicht belegt; wahrscheinlich tragend sind die Wand Wohnen/Schlafen und die Flurwände – als tragend gezeichnet, in `unverified` vermerkt.

## Offene Punkte

- Alle „ca.“-Maße aus dem Vorgänger sind in `unverified` geführt, bis sie mit dem Aufteilungsplan 2014 bzw. dem bemaßten Brandschutzplan abgeglichen sind.
- Sanitärobjekte und Waschmaschinenstellplatz nur schematisch; Fensterbänke und Balkongeländer nicht gezeichnet.
