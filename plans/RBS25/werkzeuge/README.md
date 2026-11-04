# Werkzeuge der RBS25-Neuzeichnung

Hilfsskripte, mit denen die Geometrie-JSONs in `../geometrie/` aus dem Vektor-PDF
`../quelle/20140801-Aufteilungsplan_Grundrisse_RB25.pdf` erzeugt wurden (Stand 04.11.2026).
Maßgeblich ist das JSON; die Skripte dienen der Nachvollziehbarkeit.

- `ex.py`: Vektoren aus dem PDF extrahieren
- `cfg.py`: Geschossursprünge (pt) und Maßstab 1 m = 28,3465 pt
- `doors.py`: Türen und Aufschläge
- `build.py`: Geschoss-JSONs erzeugen

Ursprünglich in einem temporären Arbeitsverzeichnis ausgeführt; Pfade bei erneuter Nutzung anpassen.
