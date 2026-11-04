# KSS29 – 3D-Modell 1. OG

Begehbares 3D-Modell der Wohnung, erzeugt aus `../geometrie/OG1.json`. Es dient zum Möblieren,
zum Prüfen von Bildern an der Wand und zum Einschätzen von Tageslicht und Kunstlicht.

| Datei | Inhalt | Öffnen mit |
|-------|--------|------------|
| `KSS29_OG1.html` | Raumplaner im Browser, Modell eingebettet | Doppelklick, Chrome/Edge/Firefox/Safari (lädt three.js aus dem Internet) |
| `KSS29_OG1.glb` | Modell als glTF 2.0 (offenes Format) | Blender, SketchUp, Unity, Windows 3D-Viewer, three.js |
| `ausstattung.json` | Deckenspots, Bodenbeläge, Balkonbrüstung (Eingabe für den Generator) | Texteditor |

Neu erzeugen, nachdem sich der Grundriss geändert hat:

```bash
python3 tools/build_3d.py plans/KSS29/geometrie/OG1.json --viewer
```

## Browser-Ansicht

- **Rundgang**: Ziehen zum Umsehen. Tippe auf den Boden, um dorthin zu gehen, oder gehe mit WASD bzw. den Pfeiltasten (Shift läuft schneller).
  Unter „Räume“ springst du mit „Hin“ in jeden Raum.
- **Übersicht**: Modell von außen ohne Decke, mit Sonnenbahn des gewählten Tages. **Grundriss**: Draufsicht, genordet.
- **Sonne**: Datum, Uhrzeit, Zeitraffer, klarer oder bedeckter Himmel. Die Kurve zeigt die Sonnenhöhe über den Tag.
  Standort ist München (aus Home Assistant). Nordabweichung einstellbar, falls der Lageplan nicht genau genordet ist.
- **Licht**: Deckenleuchten (automatisch bei Dämmerung, an oder aus, Helligkeit, 2700 bis 4000 K), Himmelslicht,
  Belichtung, Türen offen oder zu, Augenhöhe.
- **Möbel**: 22 Möbeltypen mit Maßen in cm, Drehen, Farbe, Duplizieren. Ziehen verschiebt das Möbelstück am 5-cm-Raster, R dreht es.
- **Bilder**: Eigenes Foto hochladen und auf eine Wand tippen. Breite, Höhe der Bildmitte und Rahmen lassen sich einstellen.
  Das Bild lässt sich an der Wand verschieben.
- **Sichern**: Die Einrichtung bleibt im Browser gespeichert. Mit „Einrichtung als Datei“ sicherst du sie als JSON,
  „Modell mit Möbeln als GLB“ exportiert alles für Blender.

## Blender

```bash
blender --python tools/blender_szene.py -- plans/KSS29/3d/KSS29_OG1.glb --datum 2026-12-21 --zeit 10:00 --raum Schlafzimmer
```

Das Skript importiert das Modell, setzt Sonne und Himmel nach Ort, Datum und Uhrzeit (MEZ/MESZ), stellt Cycles ein und
eine Kamera in den Raum. Mit `-b … --render bild.png` rendert es ohne Oberfläche. Optionen: `--bedeckt`, `--licht`,
`--nord`, `--breite/--laenge`, `--samples`, `--aufloesung`. Getestet mit Blender 5.2.
Auch das GLB mit Möbeln aus dem Browser lässt sich so laden.

Struktur im GLB: `Waende/Wand_<id>`, `Oeffnungen/Fenster_*|Balkontuer_*|Tuer_*|Zarge_*`, `Boeden/Boden_<Raum>`,
`Leuchten/Leuchte_<Raum>` (Punktlicht) bzw. `Leuchten/Spot_<Raum>_<n>` (Spotlicht), `Decke`, `Umgebung` (EG-Baukörper, Balkone, Brüstungen, Gelände).
Türblätter drehen um ihren Bandpunkt, die Winkel für offen und zu stehen in den Extras (`yawOpen`, `yawClosed`).

## Ausstattung (`ausstattung.json`)

- **Deckenspots** in Flur (4), Garderobe (2), Bad (5, davon einer über der Dusche) und WC (1), Lage aus den pinken
  Symbolen im Werkplan („Vorschlag Deckenspots“). Je 400 lm, 60° Abstrahlwinkel (angenommen). Die übrigen Räume haben
  eine Deckenleuchte in Raummitte (Annahme, Lage unbekannt).
- **Böden**: kleinformatiges Stabparkett Eiche hell (Schiffsverband 7 × 49 cm angenommen), Feinsteinzeug hellgrau 60 × 60.
- **Balkonbrüstung**: Plattenverkleidung, lichtundurchlässig, 1,00 m hoch, Farbe angenommen (hellgrau). Gilt für Balkon und Loggia.

Die Beispiel-Einrichtung im Browser folgt dem heutigen Stand: durchgehender Wandschrank im Schlafzimmer,
Schreibtisch im Büro an der Nordwand, Couch mittig im Wohnzimmer mit Blick auf ein kleines Sideboard mit 55-Zoll-TV an der
Ostwand, Esstisch neben der Couch in Nord-Süd-Richtung. Maße und genaue Lage der Möbel sind geschätzt und lassen sich im
Browser anpassen.

## Annahmen (nicht aus dem Plan)

| Größe | Wert | Herleitung |
|-------|------|------------|
| Höhe 0 | OKFF 1. OG (+2,90) | Werkplan |
| lichte Raumhöhe | **2,55 m** | Annahme: Geschosshöhe 2,90 − Decke 0,20 − Fußbodenaufbau 0,15 |
| Fenster | Brüstung 0,70, Sturz 2,23 (AR/Bad: Brüstung 1,00) | BRH/STH aus dem Plan minus 2,90 |
| Balkon-/Loggiatüren | 0 bis 2,23 | Sturz wie Fenster |
| Innentüren | lichte Höhe 1,985 | Rohbaumaß 2,135 minus Fußbodenaufbau 0,15 |
| Wohnungstür | weiß wie Innentüren | Vorgabe: Innenwände und Türen weiß |
| Balkonbrüstung | Platten 1,00 m hoch, hellgrau | Plattenverkleidung laut Eigentümer, Höhe und Farbe angenommen |
| Böden | Parkett bzw. Feinsteinzeug 60 × 60 | Raumstempel im Werkplan, Garderobe wie Flur angenommen |
| Treppenhausfenster | nicht geöffnet | liegt mit Brüstung +6,50 über dieser Etage |

Nicht modelliert: Treppe, Geschoss darüber mit Balkonen oder Dachüberstand, Nachbarhäuser, Bäume, Rollläden.
Alles, was über der Wohnung oder davor Schatten wirft, fehlt also. Morgens und abends kann das Licht in der
Wirklichkeit deutlich früher weg sein.

## Grenzen der Lichtdarstellung

Im Browser sind Sonnenstand und Schattenwurf genau (Sonnenformel nach NOAA/SunCalc, ca. 0,1°). Das Licht, das
von den weißen Wänden zurückgeworfen wird, ist nur geschätzt: Ein Flächenlicht an jedem Fenster und ein
Grundlicht ersetzen die echte Lichtverteilung. Helligkeitsvergleiche zwischen Räumen oder Tageszeiten sind
deshalb nur grob. Für eine belastbare Beurteilung das Modell in Blender mit Cycles rendern.
