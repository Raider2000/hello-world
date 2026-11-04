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

Gemeinsames Koordinatensystem aller Geschosse: Meter, y nach oben, Ursprung = linke untere
Rohbau-Außenecke des Hauptbaukörpers (Brandwand zu Haus Nr. 23 / Straßenfassade). Grundlage ist der
Aufteilungsplan 2014 (Vektor-PDF, M 1:100 → 1 m = 28,3465 pt); je Geschoss nur eine Verschiebung
(Ursprung in pt, siehe `source.transformation`), kein Drehen/Skalieren.

| Geschoss | Geometrie | SVG / DXF | Wohnungen | Flächenprüfung |
|----------|-----------|-----------|-----------|----------------|
| KG | `geometrie/KG.json` | `ausgabe/RBS25_KG.svg` / `.dxf` | Kellerabteile K1–K8 (Zuordnung zu WE offen), Flur 1–3, Fahrräder/Kinderwägen | keine Planflächen (nur berechnet) |
| EG (gesamte Etage) | `geometrie/EG.json` | `ausgabe/RBS25_EG.svg` / `.dxf` | WE1, WE2 (+ Hauseingang) | keine Planflächen (nur berechnet); Außenanlagen nicht übernommen |
| OG1 (gesamte Etage) | `geometrie/OG1.json` | `ausgabe/RBS25_OG1.svg` / `.dxf` | WE3, WE4 | keine Planflächen (nur berechnet); Achsen wie OG2: Kette unten 3,24⁵ / 3,21 / 2,20 / 3,22 / 3,16⁵, Gesamt 16,51⁵ |
| OG2 (gesamte Etage) | `geometrie/OG2.json` | `ausgabe/RBS25_OG2.svg` / `.dxf` | WE5 (nach Sanierung), WE6 | WE5 Wohnen +0,2 %, Schlafen +0,3 %, Flur +0,5 %; WE6 Kind +0,1 %, Bad −1,2 %, Flur −0,7 %, Schlafen ±0,0 %, Wohnen/Essen +0,2 % (Sollwerte bemaßter Plan) |

### KG – Transformation

- `x_m = (x_pt − 1521,06) / 28,3465`, `y_m = (1318,56 − y_pt) / 28,3465`; x-Ursprung über die Mitte der Treppenhauswände an das OG2 angeglichen.
  Die KG-Außenwände liegen im Plan 5–10 cm innerhalb der Obergeschoss-Fassaden (Gesamtbreite KG 16,44 m) – unverändert übernommen, in `unverified`.

### EG – Transformation

- `x_m = (x_pt − 271,80) / 28,3465`, `y_m = (1318,56 − y_pt) / 28,3465`. Treppenhauswände im EG 0,27 statt 0,24 m stark (laut Plan).

### OG1 – Transformation

- `x_m = (x_pt − 241,20) / 28,3465`, `y_m = (491,88 − y_pt) / 28,3465`. Wände, Treppenhaus und Achsen decken sich mit dem OG2 (≤ 1 cm).

### OG2 – Transformation und Kontrollmaße

- Aufteilungsplan: `x_m = (x_pt − 1192,44) / 28,3465`, `y_m = (494,16 − y_pt) / 28,3465`.
- WE05 (Sanierungszustand) aus der bisherigen `OG2.json`: `x_neu = x_alt − 0,010`, `y_neu = y_alt`.
  Die Brandwand links ist damit 0,125 m stark (16,515 − Kettensumme 16,39); die 6,85-m-Kette liegt bei x = 0,125 … 6,975.
- Kontrollmaße soll (bemaßter Plan) / ist (Zeichnung): Kette unten 3,25 / 3,21 / 2,20 / 3,22 / 3,16 → 3,250 / 3,210 / 2,203 / 3,217 / 3,168;
  Gesamtbreite 16,515 / 16,527; Tiefe links 9,84 / 9,84 (WE05) bzw. 9,83 (Aufteilungsplan); rechte Seite 11,395 / 11,405
  (0,57 / 4,94 / 0,27 / 3,23 / 0,30 / 1,86 / 0,225 → 0,572 / 4,940 / 0,271 / 3,230 / 0,300 / 1,859 / 0,233); 12,15 / 12,167.

## Klärungen (Eigentümer, 04.11.2026)

- **Balkon WE05**: 3,00 × 2,50 m = 7,50 m² ist korrekt; für die Miete wird er zur Hälfte (3,75 m²) angesetzt.
- **Flächen Essen, Kochen, Bad**: kein neues Aufmaß; Flächen werden aus der Neuzeichnung berechnet und als „berechnet“ gekennzeichnet.
- **Tragende Wände**: nicht belegt; wahrscheinlich tragend sind die Wand Wohnen/Schlafen und die Flurwände – als tragend gezeichnet, in `unverified` vermerkt.

## Offene Punkte

- Alle „ca.“-Maße aus dem Vorgänger sind in `unverified` geführt, bis sie mit dem Aufteilungsplan 2014 bzw. dem bemaßten Brandschutzplan abgeglichen sind.
- Sanitärobjekte und Waschmaschinenstellplatz nur schematisch; Fensterbänke und Balkongeländer nicht gezeichnet.
