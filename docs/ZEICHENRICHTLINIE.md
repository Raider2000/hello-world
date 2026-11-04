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

## Layer (SVG-Gruppen = DXF-Layer)

| Layer            | Inhalt                         |
|------------------|--------------------------------|
| `A_WAND_TRAGEND` | Außen- und tragende Wände      |
| `A_WAND`         | nichttragende Innenwände       |
| `A_OEFFNUNG`     | Türen (mit Aufschlag), Fenster |
| `A_RAUM`         | Raumpolygone                   |
| `A_BEMASSUNG`    | Maßketten                      |
| `A_TEXT`         | Raumname, Fläche, Hinweise     |
| `A_UNGEPRUEFT`   | ungeprüfte/angenommene Werte   |

## Rendern

```bash
pip install -r tools/requirements.txt
python3 tools/render_plan.py plans/KFS29/geometrie/EG.json
python3 tools/render_plan.py --all
```

Ein vollständiges Schema-Beispiel liegt in `tools/beispiel/geometrie/EG.json`.
