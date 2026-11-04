# WBS3 – Weinbergstraße 3

## Quellen

| Datei | Inhalt | Planstand | Status |
|-------|--------|-----------|--------|
| `quelle/20260919-Grundriss_1OG_Etage_gesamt_mit_Massen-Weinbergstr_3.svg` / `.pdf` | 1. OG, gesamte Etage, bemaßt, Vektor (mm, Ebenen) | 19.09.2026 | **neueste Fassung**, Grundlage |
| `quelle/20260919-Grundriss_1OG_WE3_mit_Massen-Weinbergstr_3.svg` / `.pdf` | 1. OG, nur WE3, bemaßt | 19.09.2026 | Auszug |
| `quelle/19980000-Teilungserklaerung_URNr_1291-1998_Nachtrag_1322-1998_Weinbergstr_3_Leipzig.pdf` | Teilungserklärung mit Nachtrag, Scan 30 S.; Wohnungsverzeichnis S. 4–5, Aufteilungspläne S. 21–26 (1. OG = Blatt 7, S. 23), Abgeschlossenheitsbescheinigung | 1998 | historisch, Wohnungsnummern; Scan zu unscharf für Maßabgleich |
| `quelle/20260919-Grundriss_1OG_WE3_ohne_Masse-Weinbergstr_3.pdf` | 1. OG, nur WE3, unbemaßt | 19.09.2026 | Auszug |

## Geschosse

| Geschoss | Geometrie | SVG | DXF | Flächenprüfung |
|----------|-----------|-----|-----|----------------|
| OG1 | `geometrie/OG1.json` (Etage gesamt, WE3 + WE4) | `ausgabe/WBS3_OG1.svg` | `ausgabe/WBS3_OG1.dxf` | alle 14 Räume mit Flächenangabe ≤ 0,4 % Abweichung; Balkone (Plan: ½ 1,23 / ½ 1,21 m²) per Hand geprüft: 2,453 / 2 = 1,226 und 2,425 / 2 = 1,213 |

## Zeichnung OG1

- Transformation: mm, y nach unten (Quelle) -> m, y nach oben, Ursprung linke untere Rohbau-Außenecke (Quelle 2600/16200); Details in `source.transformation`.
- Kontrollmaße: Gesamtbreite 14,535 m (Kette, bestätigt durch Aufteilungsplan 1998), alle Teilketten stimmen mit den Messpunkten überein; linke Tiefe 11,835 m, rechte Tiefe 11,745 m.
- Abgleich: Overlay Original gegen Neuzeichnung (Playwright, gleicher Maßstab) deckungsgleich, Abweichungen nur in Strichstärken.
- Renderer-Erweiterungen (abwärtskompatibel): `symbols` (Treppe, Nordpfeil), `holes` in `wall_polygons`, `margin`, `name_size` je Raum.

## Offene Punkte

- **Tiefe (geklärt):** Links 11,835 m – die Teilkette des Plans 2026 ergibt genau diesen Wert, das dort angegebene Gesamtmaß „11,805“ ist ein Rechenfehler (in der Neuzeichnung auf 11,83⁵ korrigiert). Rechts 11,745 m, bestätigt durch den Aufteilungsplan 1998 (Blatt 7). Die Nordfassade verläuft damit tatsächlich 9 cm schräg.
- Aussparung in der rechten Außenwand (0,175 × 0,19 m): laut Eigentümer vermutlich ein Wand-Einbauschrank mit Tür.

- Weitere Geschosse: keine Quellen vorhanden.
