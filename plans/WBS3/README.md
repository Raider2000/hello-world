# WBS3 – Weinbergstraße 3

## Quellen

| Datei | Inhalt | Planstand | Status |
|-------|--------|-----------|--------|
| `quelle/20260919-Grundriss_1OG_Etage_gesamt_mit_Massen-Weinbergstr_3.svg` / `.pdf` | 1. OG, gesamte Etage, bemaßt, Vektor (mm, Ebenen) | 19.09.2026 | **neueste Fassung**, Grundlage |
| `quelle/20260919-Grundriss_1OG_WE3_mit_Massen-Weinbergstr_3.svg` / `.pdf` | 1. OG, nur WE3, bemaßt | 19.09.2026 | Auszug |
| `quelle/20260919-Grundriss_1OG_WE3_ohne_Masse-Weinbergstr_3.pdf` | 1. OG, nur WE3, unbemaßt | 19.09.2026 | Auszug |

## Geschosse

| Geschoss | Geometrie | SVG | DXF | Flächenprüfung |
|----------|-----------|-----|-----|----------------|
| OG1 | `geometrie/OG1.json` (Etage gesamt, WE3 + Wohnung rechts) | `ausgabe/WBS3_OG1.svg` | `ausgabe/WBS3_OG1.dxf` | alle 14 Räume mit Flächenangabe ≤ 0,4 % Abweichung; Balkone (Plan: ½ 1,23 / ½ 1,21 m²) per Hand geprüft: 2,453 / 2 = 1,226 und 2,425 / 2 = 1,213 |

## Zeichnung OG1

- Transformation: mm, y nach unten (Quelle) -> m, y nach oben, Ursprung linke untere Rohbau-Außenecke (Quelle 2600/16200); Details in `source.transformation`.
- Kontrollmaße: Gesamtbreite 14,535 m (Kette), alle 12 Maßketten der Quelle stimmen mit den Messpunkten überein; linke Gebäudetiefe 11,835 m (Wandecken) gegen Kette 11,805 m, siehe `unverified`.
- Abgleich: Overlay Original gegen Neuzeichnung (Playwright, gleicher Maßstab) deckungsgleich, Abweichungen nur in Strichstärken.
- Renderer-Erweiterungen (abwärtskompatibel): `symbols` (Treppe, Nordpfeil), `holes` in `wall_polygons`, `margin`, `name_size` je Raum.

## Offene Punkte

- Wohnung rechts: Nummer im Plan nicht genannt, Präfix „WE-R“ vorläufig.
- Maßkette 11,805 m links um 0,03 m gegenüber den Wandecken versetzt; Nordfassade um 0,09 m schräg (aus Quelle übernommen).

- Weitere Geschosse: keine Quellen vorhanden.
