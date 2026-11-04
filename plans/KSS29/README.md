# KSS29 – Kastenssestraße 29

## Quellen

| Datei | Inhalt | Planstand | Status |
|-------|--------|-----------|--------|
| `quelle/Grundriss_1.OG_Kastenssestrasse_29.pdf` | 1. OG, Scan A3 300 dpi, vollständig bemaßt (Ausführungs-/Werkplan) | undatiert, laut Eigentümer aktueller Stand (Baujahr 2020/2021) | **Maßquelle** |
| `quelle/Grundriss_1.OG_bearbeitet.xcf` | GIMP-Datei auf Basis des Scans (4961 × 3508 px) | – | Referenz, nicht verwendet |
| `quelle/dashboard/gen_plan.py` | Abstrahierter Grundriss als Home-Assistant-Hintergrund, Geometrie in m (v3) | 2026 | **neueste Raumnutzung**, Maße vereinfacht |
| `quelle/dashboard/floor_plan_floor_1_dashboard.svg` | Ausgabe von gen_plan.py, in Inkscape nachbearbeitet | 2026 | Referenz |

## Home-Assistant-Dashboard

Neu erzeugter Dashboard-Hintergrund aus der Neuzeichnung: [`dashboard/`](dashboard/README.md) (`tools/ha_dashboard.py`).

## Geschosse

| Geschoss | Geometrie | SVG | DXF | Flächenprüfung |
|----------|-----------|-----|-----|----------------|
| OG1 | `geometrie/OG1.json` | `ausgabe/KSS29_OG1.svg` | `ausgabe/KSS29_OG1.dxf` | bestanden, max. +2,7 % (Bad), Balkone −2,0/−2,8 % |

### OG1 – Vorgehen

- Der Scan liegt wie das Dashboard (Norden/Flachdach oben, Straße West, Garten Ost), nur die Texte stehen quer.
  Koordinaten: Meter, Ursprung SW-Rohbau-Außenecke, y nach Norden; `y = 11,675 − yd` (yd = Dashboard-y ab
  Nord-Außenkante). Details in `source.transformation`.
- Alle Wände, Öffnungen und Balkone stammen aus den Maßketten (Rohbau). Außenwand 36,5 (12 WD + 24,5 Porenbeton),
  Innenwände 24 / 17,5 / 11,5, Installationsvorwände 20.
- Raumnamen nach aktueller Nutzung (Dashboard), Flächen (`area_stated`) laut Scan-Stempel. Die Raumpolygone liegen auf den
  Rohbau-Innenkanten, die Stempel-NF sind Fertigmaße. Deshalb liegen die berechneten Flächen meist 1–3 % höher.
- Zuordnung Scan → Nutzung: AR → Garderobe, WC → Toilette, Diele → Flur, Kind 1 → Büro, Kind 2 → Kinderzimmer,
  Loggia/Balkon 2 → Balkon zur Straße, Balkon 1 → Balkon zum Garten.
- Abgleich: Overlay SVG/Scan im gleichen Maßstab, Restabweichung ca. 2–3 cm (der Scan ist um ca. 0,2° verdreht).

### Abweichungen Dashboard (`gen_plan.py`) ↔ Scan (Dashboard-Koordinaten, m)

| Bauteil | Dashboard | Scan |
|---------|-----------|------|
| Wand TRH/Garderobe | x 2,845–2,96 (11,5) | x 2,72–2,96 (24) |
| Wohnungstür | y 3,85–4,75 (0,90) | y 3,44–4,45 (1,01) |
| Fenster TRH West | y 3,80–4,80 | y 3,25–4,45 (1,20) |
| Fenster Küche West | y 5,66–6,86 | y 5,84–7,04 |
| Küche Nordwand / Tür | y 4,845–4,96 (11,5), Tür x 4,365–5,25 | y 4,575–4,815 (24), Tür x 4,155–5,04 |
| Südwand Bad/WC/Garderobe | y 3,645–3,76 | y 3,015–3,13 |
| WC (Toilette) | x 4,495–5,615, y 1,905–3,645, Nordwand y 1,79 | x 4,495–5,615, y 1,655–3,015, Vorwand 20 bei y 1,455–1,655, Ostvorwand x 5,615–5,815 |
| Türen WC / Bad | x 4,60–5,36 / 6,70–7,585 | x 4,555–5,315 / 6,31–7,195 |
| Wand Bad/Schlafen/Flur Ost | x 8,195–8,31 (11,5) | x 8,195–8,37 (17,5) |
| Wand Schlafen/Büro | y 5,285–5,40 | y 4,90–5,015 |
| Schlafzimmer-/Bürotür | y 3,80–4,685 / 6,08–6,965 | y 3,265–4,15 / 5,815–6,70 |
| Fenster Schlafen / Büro Ost | y 1,675–3,475 / 6,0–7,2 | y 1,31–3,11 / 5,84–7,04 |
| Kamin | x 5,45–5,85, y 4,96–5,66 | x 5,36–5,79, y 4,815–5,515 |
| Küche Ostwand | x 5,85–5,965 | x 5,79–5,965 (17,5) |
| Wand Küche/Loggia | y 7,645–7,76 (11,5) | y 7,715–8,08 (36,5) |
| Nordwand Wohnen/Kinderzimmer (Flur-Süd) | y 7,645–7,76 (11,5) | y 7,65–7,825 (17,5) |
| Türen Wohnen / Kinderzimmer | Angel bei x 6,85 bzw. 7,31 | zwei Türen 0,88 bei x 6,06–6,94 und 7,22–8,10 |
| Loggia-Tür | y 8,70–10,50 | y 8,57–10,37 |
| Südwand Loggia | beginnt bei x 1,00 | durchgehend ab x 0 (Loggia beidseitig von Wänden gefasst) |
| Balkon zur Straße | y 7,76–11,675 | Platte y 7,98–11,41, innen 8,08–11,31 |
| Balkon zum Garten | y 5,50–11,675 | Platte y 5,63–10,58, innen 5,73–10,48 |
| Balkontür Kinderzimmer | y 8,40–10,20 | y 8,57–10,37 |
| Fenster Süd Wohnen / Kinderzimmer | x 3,96–5,76 / 8,47–10,27 | x 5,13–6,93 / 8,68–10,48 |

## Klärungen (Eigentümer, 04.11.2026)

- Treppenhaus-Stempel 4,49 m² bezieht sich wahrscheinlich nur auf das Podest; keine Flächenprüfung für das Treppenhaus.
- Gestricheltes Rechteck vor dem Küchenfenster = Anleiterstelle für den 2. Rettungsweg.
- Die Dusche gehört zum Badezimmer und ist durch eine Trockenbauwand vom WC getrennt.
- Der Scan entspricht dem heutigen Stand; Baujahr 2020/2021.

## Offene Punkte

- Weitere Geschosse: keine Quellen vorhanden.
- OG1: Gesamtmaß Tiefe 11,67⁵ ↔ Summe aller Teilketten 11,68 (5 mm in den Südräumen aufgefangen).
- OG1: Balkonflächen (BF 6,88 / 7,37) nur mit Geländerachse erreichbar, gezeichnet bis Innenkante Geländer.
- OG1: Treppenstufen nicht gezeichnet (der Renderer kennt keine freien Linien), nur Treppenauge und Hinweise.
- Alle weiteren Annahmen stehen in `geometrie/OG1.json` unter `unverified`.
