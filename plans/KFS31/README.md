# KFS31 – Karl-Ferlemann-Straße 31

## Quellen

| Datei | Inhalt | Planstand | Status |
|-------|--------|-----------|--------|
| `quelle/2026-Grundriss-Karl_Ferlemann_Str_31-WE1-vereinfacht.svg` | WE 1, vereinfacht (Inkscape, unbemaßt, Flächen „ca.“) | 2026 | **neueste Fassung für WE 1** |
| `quelle/2026-Grundriss-WE1-vektorisiert.svg` | WE 1, automatisch vektorisiert | 2026 | Referenz |
| `quelle/20101111-Grundrisse-Karl_Ferlemann_Str_31.pdf` | Scan, 16 S.: Lageplan, Grundrisse (S. 3–7), Ansichten, Schnitt, Abgeschlossenheitsunterlagen | 11.11.2010 | **neueste Fassung für alle Geschosse** |
| `quelle/19990111-Grundrisse-Karl_Ferlemann_Str_31.pdf` | Scan, 20 S.: Bauantragspläne (Grundrisse, Schnitte, Ansichten) mit Bemaßung | 11.01.1999 | ersetzt, Maßquelle |

## Geschosse

| Geschoss | Geometrie | SVG | DXF | Flächenprüfung |
|----------|-----------|-----|-----|----------------|
| EG | `geometrie/EG.json` | `ausgabe/KFS31_EG.svg` | `ausgabe/KFS31_EG.dxf` | 3 Abweichungen > 3 % (dokumentiert, s. u.) |

## Quellen-Seitenzuordnung

| Geschoss | 2010 (Raumaufteilung, WE) | 1999 (Maße) | 2026 |
|----------|---------------------------|-------------|------|
| EG | S. 4 | S. 4 (Neubau/West) + S. 5 (Altbau/Ost) | WE 1 |

## Koordinatensystem (alle Geschosse gleich)

- Ursprung (0,0) = Südwestecke Rohbau Neubau (Raimundstraße/Hofseite), x nach Osten entlang der
  Raimundstraße, y nach Norden entlang der Karl-Ferlemann-Straße.
- Neubau (Westteil) x = 0 … 12,39, Fuge 0,02, Altbau x = 12,41 … 26,91 (14,50 lt. 1999).
- Ecke Raimund-/Karl-Ferlemann-Straße abgeschrägt: (24,76 | 0) → (26,91 | 2,15).
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
