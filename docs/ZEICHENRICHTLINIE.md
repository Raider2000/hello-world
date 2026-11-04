# Zeichenrichtlinie – Neuzeichnung der Grundrisse

Ziel: Die Bestandsgrundrisse (Scans, PDFs, Bilder) werden **maßgetreu** in eine
offene, versionierbare Form überführt. Für jedes Geschoss gibt es genau eine
Geometriedatei, aus der SVG (Ansicht, M 1:100) und DXF (CAD-Austausch) erzeugt werden.

## Ablage

```
plans/<OBJEKT>/
  quelle/       Originale, unverändert (PDF/JPG/PNG/DWG). Dateiname behalten.
  geometrie/    <GESCHOSS>.json – einzige Quelle der Wahrheit für die Zeichnung
  ausgabe/      <OBJEKT>_<GESCHOSS>.svg / .dxf – generiert, nicht von Hand ändern
  README.md     Quellenverzeichnis, Geschossliste, offene Punkte
```

Geschosskürzel: `KG`, `EG`, `OG1`, `OG2`, …, `DG`, `SB` (Spitzboden).

## Arbeitsweise (wie beim Neuzeichnen eines Bestandsplans)

1. **Quelle sichten**: Planstand, Datum, Maßstab, Nordpfeil, Geschoss. Bei mehreren
   Fassungen gilt die neueste; ältere bleiben in `quelle/`, werden aber im README
   als „ersetzt“ geführt.
2. **Achsen & Außenmaße zuerst**: Ursprung (0,0) = linke untere Außenecke des
   Rohbaus, x nach rechts, y nach oben, Einheit **Meter**, 3 Nachkommastellen.
   Außenmaßketten festlegen, dann Innenmaßketten.
3. **Wände**: Achse `a`→`b` mit `thickness` und `align` (`left`/`right`/`center`
   relativ zur Laufrichtung a→b). Typ `exterior`, `load-bearing` oder `interior`.
   Übliche Stärken: 0,365 / 0,30 / 0,24 / 0,175 / 0,115 m – nur wenn der Plan nichts
   anderes sagt.
4. **Öffnungen**: an Wand gebunden, `offset` = Abstand ab Wandpunkt `a` bis
   Rohbaukante Öffnung, `width` = Rohbaurichtmaß (z. B. 0,885 / 1,01 / 1,26 m).
   Türen: `hinge` (`start`/`end`) und `side` (`left`/`right` relativ zu a→b).
5. **Räume**: Polygon in Fertigmaßen der Innenkanten, `area_stated` = Fläche laut Plan.
   Der Renderer vergleicht berechnete und angegebene Fläche; **> 3 % Abweichung**
   bricht mit Exit-Code 1 ab und muss geklärt oder dokumentiert werden.
6. **Nichts erfinden**: Unleserliche oder widersprüchliche Maße werden plausibel
   angenommen **und** in `unverified` mit Position und Text eingetragen
   (erscheint rot im Plan, Layer `A_UNGEPRUEFT`).
7. **Abgleich**: SVG rendern, neben das Original legen (Overlay auf gleichen Maßstab),
   Abweichungen korrigieren. Erst dann committen.

## Erweiterungen des Schemas (alle optional, abwärtskompatibel)

Für Bestandsfassaden mit abgeschrägten Laibungen und für Sanierungspläne:

- **`wall_polygons`**: `[{"id", "type", "polygon": [[x,y], …]}]` – Wände als freies Polygon
  (Meter, wie alles andere), wenn Achse + Stärke die Form nicht abbilden (Laibungen,
  Wandwinkel). Layer-Logik wie bei `walls`. Die Öffnung liegt dann als Lücke im Polygon.
- **Wandtyp `new`**: neue/zu errichtende Wände und zugemauerte Öffnungen. Layer `A_WAND_NEU`,
  im SVG schraffiert, im DXF mit Schraffur ANSI31. Gilt für `walls` und `wall_polygons`.
  Typen `exterior`/`load-bearing` → `A_WAND_TRAGEND`, alles andere → `A_WAND`.
- **Freie Öffnungen**: statt `"wall": "<id>"` ein `"host": {"a","b","thickness","align"}`
  (Hilfsachse, `thickness` darf 0 sein). `offset`/`width`/`hinge`/`side` wie bei Wandöffnungen,
  geschnitten wird nichts. Für Türen: `a` = Angel, `b` = Schließlage, `side` = Seite des Aufschlags
  relativ zu a→b.
- **Räume**: `subtitle` ersetzt die Flächenzeile (z. B. „Metallkonstruktion“), `show_area: false`
  blendet sie aus, `outline: true` zeichnet eine gestrichelte Kontur (Balkon außerhalb der Wände).
  Räume zählen zur Zeichenfläche, der Zeichenrand wächst mit weit abgesetzten Maßketten.
- **`notes`**: `{"pos","text"}` plus optional `size`, `anchor` (`start`/`middle`/`end`), `bold`;
  Notes erscheinen auch im DXF (Layer `A_TEXT`). Maßketten: `label` überschreibt den Wert
  (z. B. „ca. 2,30“); ein Leerzeichen zeigt nur die Maßkette ohne Text.
- **`unverified`**: `text` ist die volle Begründung, optional `short` die Kurzfassung im SVG
  (`""` = nur roter Kreis). Im DXF steht immer der volle Text.
- **`source.transformation`**: Freitext zur Koordinatentransformation, wenn eine bestehende
  Zeichnung (z. B. mm, y nach unten) übernommen wurde. Das Rohdaten-Original bleibt in `quelle/`.

Beispiel: `plans/RBS25/geometrie/OG2.json`.

## Layer (SVG-Gruppen = DXF-Layer)

| Layer            | Inhalt                         |
|------------------|--------------------------------|
| `A_WAND_TRAGEND` | Außen- und tragende Wände      |
| `A_WAND`         | nichttragende Innenwände       |
| `A_WAND_NEU`     | neue Wände (Typ `new`, schraffiert) |
| `A_OEFFNUNG`     | Türen (mit Aufschlag), Fenster |
| `A_RAUM`         | Raumpolygone                   |
| `A_BEMASSUNG`    | Maßketten                      |
| `A_TEXT`         | Raumname, Fläche, Hinweise     |
| `A_UNGEPRUEFT`   | ungeprüfte/angenommene Werte   |

## Rendern

```bash
pip install -r tools/requirements.txt
python3 tools/render_plan.py plans/KFS31/geometrie/EG.json
python3 tools/render_plan.py --all
```

Ein vollständiges Schema-Beispiel liegt in `tools/beispiel/geometrie/EG.json`.
