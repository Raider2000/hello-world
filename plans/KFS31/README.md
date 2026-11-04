# KFS31 – Karl-Ferlemann-Straße 31

## Quellen

| Datei | Inhalt | Planstand | Status |
|-------|--------|-----------|--------|
| `quelle/2026-Grundriss-Karl_Ferlemann_Str_31-WE1-vereinfacht.svg` | WE 1, vereinfacht (Inkscape, unbemaßt, Flächen „ca.“) | 2026 | **neueste Fassung für WE 1** |
| `quelle/2026-Grundriss-WE1-vektorisiert.svg` | WE 1, automatisch vektorisiert | 2026 | Referenz |
| `quelle/20101111-Grundrisse-Karl_Ferlemann_Str_31.pdf` | Scan, 16 S.: Lageplan, Grundrisse (S. 3–7), Ansichten, Schnitt, Abgeschlossenheitsunterlagen | 11.11.2010 | **neueste Fassung für alle Geschosse** |
| `quelle/19990111-Teilungserklaerung-Karl_Ferlemann_Str_31.pdf` | Teilungserklärung (Text, 34 S.; Aufteilung S. 6–9 Abschnitt 1.2) | 11.01.1999 | Geschosszuordnung W1–W11, Keller, Spitzboden, Stellplätze; Aufteilung später durch Nachträge geändert (2. Nachtrag 13.05.2011) |
| `quelle/19990111-Grundrisse-Karl_Ferlemann_Str_31.pdf` | Scan, 20 S.: Bauantragspläne (Grundrisse, Schnitte, Ansichten) mit Bemaßung | 11.01.1999 | ersetzt, Maßquelle |

## Wohnungen

Belegt durch die Flächentabellen im Aufteilungsplan 2010 (S. 4–7) und die Geschosszuordnung der
Teilungserklärung 1999:

| Geschoss | Altbau Süd (Ecke) | Altbau Nord | Neubau |
|----------|-------------------|-------------|--------|
| EG  | W1 – 59,42 m² | W2 – 35,20 m² | Stellplätze (Parklift), AR 9/10/11 je 1,75 m² |
| OG1 | W3 – 62,90 m² | W4 – 61,25 m² (inkl. ½ Balkon) | W9 – 82,33 m² |
| OG2 | W5 – 62,90 m² | W6 – 61,25 m² | W10 – 82,93 m² |
| DG  | W7 – 62,90 m² | W8 – 61,25 m² | W11 – 82,08 m² |

Doppelstock-Stellplätze laut Teilungserklärung 1999 (ggf. durch Nachträge geändert): W3 Nr. 13.1 oben,
W5 Nr. 14.2 unten, W7 Nr. 14.1 oben, W9 Nr. 13.2 unten, W10 Nr. 12.2 unten, W11 Nr. 12.1 oben.

## Geschosse

| Geschoss | Geometrie | SVG | DXF | Flächenprüfung |
|----------|-----------|-----|-----|----------------|
| KG | `geometrie/KG.json` | `ausgabe/KFS31_KG.svg` | `ausgabe/KFS31_KG.dxf` | 9 begründete Abweichungen (Kellerverschläge schematisch, s. u.) |
| EG | `geometrie/EG.json` | `ausgabe/KFS31_EG.svg` | `ausgabe/KFS31_EG.dxf` | 3 begründete Abweichungen (s. u.) |
| OG1 | `geometrie/OG1.json` | `ausgabe/KFS31_OG1.svg` | `ausgabe/KFS31_OG1.dxf` | 2 begründete Abweichungen (Bad WE 3, Flur WE 9) |
| OG2 | `geometrie/OG2.json` | `ausgabe/KFS31_OG2.svg` | `ausgabe/KFS31_OG2.dxf` | 2 begründete Abweichungen (Bad WE 5, Flur WE 10) |
| DG | `geometrie/DG.json` | `ausgabe/KFS31_DG.svg` | `ausgabe/KFS31_DG.dxf` | 4 begründete Abweichungen (Bad WE 7; WE 11: Schlafen/Bad Dachschräge, Flur) |
| SB | `geometrie/SB.json` | `ausgabe/KFS31_SB.svg` | `ausgabe/KFS31_SB.dxf` | keine Abweichung > 3 % (Spitzböden W11 / W8 / W7: 0,0 / +0,4 / −1,6 %) |

## Quellen-Seitenzuordnung

| Geschoss | 2010 (Raumaufteilung, WE) | 1999 (Maße) | 2026 |
|----------|---------------------------|-------------|------|
| KG | S. 3 | S. 2 + S. 3 | – |
| EG | S. 4 | S. 4 (Neubau/West) + S. 5 (Altbau/Ost) | WE 1 |
| OG1 | S. 5 | S. 6 + S. 7 | – |
| OG2 | S. 6 | S. 8 + S. 9 | – |
| DG | S. 7 | S. 10 + S. 11 | – |
| SB | – (kein Grundriss 2010) | S. 12/13 (Grundriss), S. 18 (Schnitt A-A) | – |

Ansichten (2010 S. 8–10), Schnitt (S. 11) und Lageplan (S. 1–2) wurden nicht neu gezeichnet.

## Koordinatensystem (alle Geschosse gleich)

- Ursprung (0,0) = Südwestecke Rohbau Neubau (Raimundstraße/Hofseite), x nach Osten entlang der
  Raimundstraße, y nach Norden entlang der Karl-Ferlemann-Straße.
- Neubau (Westteil) x = 0 … 12,39, Fuge 0,02, Altbau x = 12,41 … 26,91 (14,50 lt. 1999).
- Ecke Raimund-/Karl-Ferlemann-Straße abgeschrägt: (24,76 | 0) → (26,91 | 2,15).
- KG lt. 1999 größer: 14,60 × 14,10 (Ostkante x = 27,01, Nordkante y = 14,10, Abschrägung 2,185),
  Außenwände 0,65–0,75. Der Neubau ist nicht unterkellert.
- Brandwand Nachbar (Nord) Außenkante y = 14,05.

## Arbeitsweise

Die 2010-Scans wurden über Passpunkte (Fassaden, Gebäudekanten, Gesamtmaßketten) mit einer
Polynomentzerrung (Restfehler ≤ 2 cm) auf das Koordinatensystem gebracht. Wandlagen wurden daraus
abgegriffen und mit den Maßketten 1999 abgeglichen; Fenster der Straßenfassaden aus den
Maßketten 1999. Der Plan 2026 (WE 1) wurde über die Fensterachsen 1999 skaliert
(ca. 133 px/m, Restfehler bis ±0,19 m, da unmaßstäblich).

## Offene Punkte

### EG
- **WE 1 – Bad/WC**: 5,18 m² berechnet, 6,35 m² lt. 2010, „ca. 6 m²“ lt. 2026. Die Zickzackwand
  stammt aus 2026 (deckt sich mit der Wandführung 2010); die Fliesenfläche im 2026-SVG läuft unter
  die Wand. Die Flächenangabe 2010 ist mit der gezeichneten Wand nicht zu erreichen → vor Ort messen.
- **WE 2 – Wohnen / Schlafen**: 14,26 / 7,56 m² berechnet gegenüber 15,05 / 7,25 m² lt. 2010; die
  Summe stimmt auf 2 %. Die Trennwand liegt im Plan 2010 anders als die Flächenangaben → Plan 2010
  ist in sich widersprüchlich.
- Nordwand WE 1 (zum Treppenhaus): Innenkante 5,21 (2010), 1999: 5,40.
- WE 1 lt. 2026: Küche als abgeschlossener Raum (2010: Kochnische), Raum „Kind“ heißt nun
  „Gast/Büro“, zweiflügelige Wohnungstür. Die Flächen in 2026 sind nur „ca.“-Werte (4/23/5/8/6/13 m²),
  deshalb bleiben die 2010-Werte als `area_stated` stehen.


- Das Objekt wurde ursprünglich als „KFS29“ geführt; die Unterlagen lauten auf Hausnr. 31.

### OG1 (gilt sinngemäß auch für OG2 und DG)
- Wohnungsnummern siehe „Wohnungen“ oben (aus den Flächentabellen 2010 belegt).
- Flur Neubau (WE 9/10/11): Flächentabelle 2010 nennt 2,60 m², die Raumstempel 2,85 (OG1) bzw. 2,65;
  die gezeichnete Geometrie ergibt 2,90 m² → aufmessen.
- **Bad Altbau Süd**: 5,61 m² berechnet, 6,65 m² lt. Plan. Die Zickzackwand ist aus dem EG (Stand 2026)
  übernommen, die Abweichung ist dieselbe wie dort → aufmessen.
- Fenster der Neubau-Südfassade sind nach der Maßkette 1999 gesetzt. Plan 2010 zeichnet sie ca. 0,24 m
  weiter westlich.
- Flur/Wohnen der Wohnung Nord gehen offen ineinander über; die Raumgrenze bei x = 20,75 ist so
  angenommen, dass beide Flächen passen.
- Außenwand Altbau in den OG 0,45 (1999), im EG 0,55.

### OG2
- Gleiche Zeichnung wie OG1 (Plan 2010 deckt sich beim Overlay): WE 5 (Süd), WE 6 (Nord), WE 10 (Neubau).

### DG
- Wände wie OG1/OG2 (Overlay mit Plan 2010 S. 7 deckungsgleich): WE 7 (Süd), WE 8 (Nord), WE 11 (Neubau).
- Neubau WE 11: gestrichelte Linie bei y ≈ 0,99 (Dachschräge). Laut Flächentabelle 2010 Schlafen 11,15 /
  Bad 5,55 / Kochen 8,60 m² (OG: 11,50 / 5,90 / 8,75) – die kleinen Abzüge passen zu einer Dachschräge.
  (Frühere Lesung 3,55 / 6,80 aus dem Raumstempel war falsch; die Tabellensumme 82,08 m² bestätigt die neuen Werte.)
- Neubau-Südfenster lt. Maßkette 1999 S. 10 (Doppelfenster); Altbau-Fenster wie OG übernommen
  (1999 bemaßt im DG abweichende Öffnungen).
- Bad WE 7: wie in OG1/OG2 (Zickzackwand), 5,61 statt 6,65 m².

### KG
- Die Kellerverschläge sind Lattenverschläge (ca. 0,07) und im Scan 2010 nur schematisch erkennbar.
  Die Trennwände sind aus dem entzerrten Scan abgegriffen; die Flächen weichen bis ca. 25 % ab
  (Keller 2/3/4/5/6, ELT, AR, HR/Technik +3,6 %).
- **Kellerzuordnung (geklärt):** Der Aufteilungsplan 2010 (S. 3) nummeriert die Keller 1–8 mit Flächentabelle;
  Keller n gehört zu Wohnung W n. Die Neubau-Wohnungen W9–W11 haben stattdessen die Abstellräume AR 9–11 im EG.
  (Die Teilungserklärung 1999 ordnete noch anders zu; maßgeblich ist die Aufteilung 2010/2011.)
- Keller 7: Raumstempel 4,65 m², Flächentabelle 7,65 m², Geometrie 5,35 m² – widersprüchlich, aufmessen.
- Nördlicher Raum (11,60–13,40) ohne Bezeichnung; Hofbereich westlich des AR (Schacht?) unklar.

### SB (Spitzboden)
- Quelle nur 1999 S. 12/13 (2010 ohne Spitzboden). Gezeichnet sind die drei Spitzbodenflächen mit lichter Höhe
  ≥ 1 m (gestrichelt), Giebel/Brandwand an der Fuge (0,24 / 0,02 / 0,45), die Trennwand zwischen den
  Altbau-Spitzböden und drei Bodentreppen. Die Außenkontur ist aus dem DG übernommen (Plan zeigt Traufen).
- Flächen: Der Plan nennt F = halbe Grundfläche und in Klammern die Grundfläche mit lichter Höhe ≥ 1 m:
  W11 17,26 (34,51), Altbau Süd 11,55 (23,10), Altbau Ost 15,26 (30,52) m². `area_stated` = Klammerwert.
- Lage der Streifen in y, die Trennwand und die Bodentreppen sind am entzerrten Scan abgegriffen (±5 cm). Bemaßt
  sind nur 12,15 / 0,24 / 0,02 / 0,45 / 14,05 / 26,91, die Breiten 2,84 und 3,50 sowie die Kette 14,05 (Ost).
- **Zuordnung W7/W8**: Das Kennzeichen im Süd-Spitzboden ist als „8“ lesbar, im Ost-Spitzboden unleserlich. Nach dem
  DG-Plan 1999 lag W8 im Südwestteil des Altbaus. Deshalb heißt der Süd-Spitzboden „W8“, der Ost-Spitzboden „W7“
  (Nummerierung 1999). Im Aufteilungsplan 2010 ist W7 = Süd, W8 = Nord. Ob die Sondernutzungsrechte durch
  die Nachträge 2010/2011 angepasst wurden, ist offen → Nachträge prüfen.
- W11: Die Teilungserklärung 1999 (1.2.11) nennt den Spitzboden „dazugehörend“, nicht ausdrücklich als
  Sondernutzungsrecht (anders als bei W7/W8).
- Die Trennwand ist mit „…KA F90“ beschriftet (Lesung unsicher). Ihre Fortsetzung unter der 1-m-Linie ist gestrichelt.
  Kamine sind nicht erkennbar. Dachgauben (Süd/Ost) sind nicht bemaßt und deshalb nicht gezeichnet.
- Werkzeuge: `werkzeuge/SB_entzerrung.py` (Entzerrung S. 12/13, Overlay), `werkzeuge/SB.py` (erzeugt das JSON).
