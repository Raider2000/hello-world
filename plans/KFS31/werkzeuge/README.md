# Werkzeuge der KFS31-Neuzeichnung

Hilfsskripte, mit denen die Geometrie-JSONs in `../geometrie/` erzeugt wurden (Stand 04.11.2026).
Sie dienen der Nachvollziehbarkeit; maßgeblich ist das JSON.

- `rectify.py`, `cal.json`, `ctrl.json`, `corners.py`, `findcal.py`, `grid.py`, `mgrid.py`: Entzerrung der 2010-Scans über Passpunkte (Polynom, Restfehler ≤ 2 cm)
- `crop.py`, `edge.py`, `lines.py`: Ausschnitte und Wandkanten abgreifen
- `overlay.py`: Neuzeichnung über den entzerrten Scan legen
- `common.py`, `EG.py`, `REG.py` (OG1/OG2/DG), `KG.py`: Erzeugen der Geschoss-JSONs
- `SB_entzerrung.py`, `SB.py`: Spitzboden (Entzerrung 1999 S. 12/13 mit Overlay, Erzeugen von `SB.json`)

Die Skripte erwarten gerenderte Scan-Seiten in einem Arbeitsverzeichnis (ursprünglich im
Scratchpad der Sitzung); Pfade bei erneuter Nutzung anpassen.
