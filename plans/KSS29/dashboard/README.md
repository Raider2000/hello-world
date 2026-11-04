# KSS29 – Dashboard-Grundriss für Home Assistant

`KSS29_OG1_dashboard.svg` ist ein reduzierter Grundriss des 1. OG als Hintergrund für eine
`picture-elements`-Karte. Er wird **aus der maßgetreuen Neuzeichnung** (`../geometrie/OG1.json`)
erzeugt und ersetzt die bisherige Annäherung (`../quelle/dashboard/gen_plan.py`).

```bash
python3 tools/ha_dashboard.py plans/KSS29/dashboard/dashboard.json
```

## Gestaltung

- Format **1280 × 800 (16:10)** – passt im Querformat auf die meisten Android-Tablets und in eine
  Panel-Ansicht. Für ein iPad (4:3) in `dashboard.json` `"height": 960` setzen und neu erzeugen;
  der Grundriss skaliert automatisch.
- Nur Grautöne mit Transparenz und **ohne Hintergrundfläche** – funktioniert im hellen und dunklen HA-Theme.
- Umgebung angedeutet: links die Kastenssestraße (Fahrbahn mit Mittellinie, Gehwegkante) und der Vorgarten,
  rechts der Garten mit Bäumen, Nordpfeil oben rechts. Vordach gestrichelt, Balkone umrandet.
- Raumnamen stehen oben links im Raum, die Raummitte bleibt frei für Badges.
- Maßstab ca. 60,8 px/m, alle Wände, Fenster und Türen lagerichtig wie im Plan.

## Einbindung

SVG nach `/config/www/grundriss/` kopieren und in einer Ansicht mit `panel: true` verwenden:

```yaml
type: picture-elements
image: /local/grundriss/KSS29_OG1_dashboard.svg
elements:
  - type: state-label
    entity: sensor.kueche_temperatur        # eigene Entität
    style: {left: 35.8%, top: 53.2%}
  - type: state-icon
    entity: binary_sensor.fenster_kueche    # eigene Entität
    style: {left: 22.0%, top: 54.6%}
```

`picture-elements` zentriert Elemente standardmäßig auf `left`/`top` – die Werte unten sind genau dafür gedacht.
Die vollständige Liste (inkl. Türen und Länge der Öffnungen in px) steht in
`KSS29_OG1_dashboard_positionen.json`.

## Positionen Räume (Badge-Mitte)

| Raum | id | left | top |
|------|----|------|-----|
| Treppenhaus | `treppenhaus` | 28.5% | 24.4% |
| Garderobe | `garderobe` | 38.6% | 17.6% |
| Toilette | `toilette` | 45.1% | 23.4% |
| Badezimmer | `badezimmer` | 54.6% | 18.5% |
| Schlafzimmer | `schlafzimmer` | 68.5% | 25.7% |
| Flur | `flur` | 54.9% | 46.6% |
| Küche | `kueche` | 35.8% | 53.2% |
| Büro | `buero` | 68.5% | 53.8% |
| Wohnen | `wohnen` | 41.1% | 77.9% |
| Kinderzimmer | `kinderzimmer` | 65.6% | 78.3% |
| Balkon Straße | `balkon_strasse` | 21.0% | 79.3% |
| Balkon Garten | `balkon_garten` | 81.5% | 67.2% |
| Vordach | `vordach` | 16.8% | 24.8% |

## Positionen Fenster und Fenstertüren

| id | Öffnung | left | top | Lage |
|----|---------|------|-----|------|
| F1 | Fenster Garderobe | 38.9% | 7.0% | horizontal |
| F2 | Fenster Badezimmer | 54.8% | 7.0% | horizontal |
| F3 | Fenster Wohnen | 49.8% | 93.0% | horizontal |
| F4 | Fenster Kinderzimmer | 66.6% | 93.0% | horizontal |
| F5 | Fenster Treppenhaus | 22.0% | 34.9% | vertikal |
| F6 | Fenster Küche | 22.0% | 54.6% | vertikal |
| F7 | Fenster Schlafzimmer | 77.1% | 22.4% | vertikal |
| F8 | Fenster Büro | 77.1% | 54.6% | vertikal |
| T-B1a | Balkontür Kinderzimmer, Flügel N | 77.1% | 74.2% | vertikal |
| T-B1b | Balkontür Kinderzimmer, Flügel S | 77.1% | 81.0% | vertikal |
| T-L1a | Loggiatür Wohnen, Flügel N | 26.8% | 74.2% | vertikal |
| T-L1b | Loggiatür Wohnen, Flügel S | 26.8% | 81.0% | vertikal |

**Hinweis:** Die Positionen haben sich gegenüber dem alten Dashboard-Hintergrund geändert
(die alte Annäherung wich teils um 0,4–1,2 m ab). Bestehende Elemente bitte mit den Werten oben neu setzen.
