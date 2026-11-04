import sys; sys.path.insert(0, '/tmp/kfs31/build')
from common import *
SRC = {"file": "20101111-Grundrisse-Karl_Ferlemann_Str_31.pdf S. 4 (Raum/WE) · 19990111-…pdf S. 4/5 (Maße) · 2026-…WE1-vereinfacht.svg (WE 1)",
       "date": "2010-11-11 / 1999-01-11 / 2026", "version": "Aufteilungsplan WE 1–11, Bl. 02"}
p = Plan("EG", "Erdgeschoss", SRC)
T = 0.55  # Außenwand Altbau EG (1999)

# ---------------- Altbau Außenwände (Maße 1999: 14,50 x 14,05, Ecke 2,15/2,15)
p.aw("A1", (12.41, 0), (24.76, 0), T)                       # Fassade Raimundstraße
for i, x in enumerate([13.51, 15.61, 17.46, 19.31, 22.56], 1):
    p.op(f"F_S{i}", "A1", "window", x, 0.90)
p.aw("A2", (24.76, 0), (26.91, 2.15), T)                    # Eckabschrägung
p.op("F_E1", "A2", "window", (math.hypot(2.15, 2.15) - 0.90) / 2, 0.90, absolute=False)
p.aw("A3", (26.91, 2.15), (26.91, 14.05), T)                # Fassade Karl-Ferlemann-Straße
for i, y in enumerate([3.50, 6.75, 8.55, 10.25], 1):
    p.op(f"F_O{i}", "A3", "window", y, 0.90)
p.op("T_FR1", "A3", "door", 11.75, 1.55, "start", "left")   # Fahrradraum, zweiflügelig
p.aw("A4", (26.91, 14.05), (16.42, 14.05), 0.65)            # Brandwand Nachbar (Nord)
p.aw("A5", (16.42, 14.05), (16.42, 9.36), 0.56)             # Nordflügel West (Hof)
p.op("T_FR2", "A5", "door", 11.65, 1.51, "end", "left")     # Fahrradraum zum Hof
p.op("F_W1", "A5", "window", 10.38, 0.635)                  # Bad WE 2
p.rw("A6", 15.71, 8.68, 16.98, 9.36, "exterior")            # Mauerblock Ecke Eingang
p.rw("A7", 15.71, 7.20, 16.26, 8.68, "exterior")            # Eingangswand (Hof)
p.op("T_HE", "A7", "door", 7.66, 1.01, "start", "right")    # Hauseingang
p.rw("A8", 13.89, 7.15, 15.71, 7.63, "exterior")            # AR Nordwand
p.rw("A9", 13.89, 5.78, 14.43, 7.15, "exterior")            # AR Westwand
p.rw("A10", 12.41, 5.21, 14.43, 5.78, "exterior")           # WE 1 Nordwand zum Hof
p.rw("A11", 12.41, 0.55, 12.96, 5.21, "exterior")           # Giebelwand zum Neubau

# ---------------- tragende Innenwände
p.rw("L1", 14.43, 5.21, 21.35, 5.78, "load-bearing")        # WE 1 / Treppenhaus
p.op("T_WE1", "L1", "door", 19.75, 1.26, "start", "right")  # Wohnungstür WE 1 (2026: 2-flg.)
p.rw("L2", 21.35, 5.21, 26.36, 5.45, "load-bearing")        # WE 1 / WE 2
p.rw("L3", 21.35, 5.45, 21.65, 8.68, "load-bearing")        # Treppenhaus / WE 2 Küche
p.rw("L4", 16.98, 8.68, 21.35, 8.99, "load-bearing")        # Treppenhaus / WE 2
p.op("T_WE2", "L4", "door", 20.25, 1.01, "end", "left")     # Wohnungstür WE 2
p.rw("L5", 16.98, 11.05, 26.36, 11.50, "load-bearing")      # WE 2 / Fahrradraum

# ---------------- nichttragende Innenwände
p.rw("I1", 16.12, 5.78, 16.28, 7.15)                        # AR / Treppenhaus
p.op("T_AR", "I1", "door", 5.98, 0.885, "start", "left")
p.rw("I2", 14.93, 2.96, 15.04, 5.21)                        # WE 1 Küche (2026 Wand, 2010 Linie)
p.rw("I3", 18.84, 0.55, 18.99, 5.21)                        # WE 1 Wohnen / Gast
p.op("T_WZ", "I3", "door", 4.25, 0.885, "end", "left")
p.rw("I4", 18.99, 3.80, 21.34, 3.90)                        # WE 1 Gast / Flur
p.op("T_GB", "I4", "door", 19.06, 0.885, "start", "right")
p.rw("I5", 21.34, 0.55, 21.54, 3.90)                        # WE 1 Gast / Bad
p.rw("I6", 21.54, 3.80, 22.42, 3.90)                        # WE 1 Bad / Flur
p.op("T_BD", "I6", "door", 21.60, 0.76, "start", "right")
p.rw("I7", 22.42, 3.80, 22.62, 5.21)                        # WE 1 Flur / Schlafzimmer
p.op("T_SZ", "I7", "door", 4.25, 0.885, "end", "right")
# Zickzackwand Bad / Schlafzimmer (Stand 2026, Maßstab über Fensterachsen 1999 hergeleitet)
# Badseite der Wand (2026: obere Kontur); Wand liegt jeweils links der Laufrichtung (Schlafzimmerseite)
ZB = [(22.435, 3.80), (23.27, 2.96), (22.61, 2.30), (24.355, 0.55)]
ZT = [0.19, 0.32, 0.18]
for i, (a, b) in enumerate(zip(ZB, ZB[1:]), 1):
    p.aw(f"I8{i}", a, b, ZT[i - 1], "left", "interior")
p.aw("I84", (23.44, 0.55), (23.82, 1.08), 0.74, "right", "interior")   # Mauerpfeiler Badfenster/Ecke
ZS = [offset_poly([a, b], t) for (a, b), t in zip(zip(ZB, ZB[1:]), ZT)]   # Schlafzimmerseiten
p.rw("I9", 19.64, 8.99, 19.81, 11.05)                       # WE 2 Bad / Flur
p.op("T_B2", "I9", "door", 9.22, 0.76, "end", "left")
p.rw("I10", 21.50, 8.99, 21.65, 11.05)                      # WE 2 Flur / Wohnen
p.op("T_W2", "I10", "door", 9.30, 0.885, "end", "left")
p.rw("I11", 23.15, 7.92, 26.36, 8.07)                       # WE 2 Wohnen / Schlafen
p.op("T_S2", "I11", "door", 24.11, 0.885, "start", "right")
p.rw("I12", 23.15, 5.45, 23.30, 7.92)                       # WE 2 Küche / Schlafen

# ---------------- Neubau (EG offen: Stellplatzanlage), Maße 1999
p.rw("N1a", 0, 0.02, 6.405, 0.32, "exterior")
p.op("F_N1", "N1a", "window", 2.25, 1.00)                   # Öffnung Südwand (2010 abgegriffen)
p.rw("N1b", 9.415, 0.02, 12.39, 0.32, "exterior")
p.rw("N2", 0, 0.32, 0.24, 7.79, "exterior")
p.rw("N3", 12.15, 0.32, 12.39, 7.79, "exterior")
p.rw("N4", 9.95, 0.32, 10.07, 3.20)                         # AR-Westwand
for i, (y0, y1) in enumerate([(0.32, 1.16), (1.26, 2.10), (2.20, 3.04)]):
    p.op(f"T_AR{9+i}", "N4", "door", y0 + 0.04, 0.76, "end", "right")
p.rw("N5", 10.07, 1.16, 12.15, 1.26); p.rw("N6", 10.07, 2.10, 12.15, 2.20); p.rw("N7", 10.07, 3.04, 12.15, 3.20)

# ---------------- Räume
p.room("WE 1 – Küche", [(12.96, 2.96), (14.93, 2.96), (14.93, 5.21), (12.96, 5.21)], 4.40)
p.room("WE 1 – Wohn-/Esszimmer", [(12.96, 0.55), (18.84, 0.55), (18.84, 5.21), (15.04, 5.21), (15.04, 2.96), (12.96, 2.96)], 23.35,
       label_pos=[15.9, 1.6])
p.room("WE 1 – Gast/Büro", [(18.99, 0.55), (21.34, 0.55), (21.34, 3.80), (18.99, 3.80)], 7.75)
p.room("WE 1 – Flur", [(18.99, 3.90), (22.42, 3.90), (22.42, 5.21), (18.99, 5.21)], 4.55)
bad = [(21.54, 0.55), (23.44, 0.55), (23.82, 1.08), ZB[2], ZB[1], ZB[0], (21.54, 3.80)]
p.room("WE 1 – Bad/WC", bad, 6.35, label_pos=[22.05, 2.6])
# Schlafzimmer: Innenkanten (Fassade 0,55; Abschrägung innen; KFS innen 26,36; Nordwand 5,21)
ch_in = offset_poly([(24.76, 0), (26.91, 2.15)], T)   # Innenkante Abschrägung
s1 = intersect(ch_in[0], ch_in[1], (0, 0.55), (1, 0.55))
s2 = intersect(ch_in[0], ch_in[1], (26.36, 0), (26.36, 1))
k0 = intersect(*ZS[0], (22.62, 0), (22.62, 1))
k1 = intersect(*ZS[0], *ZS[1]); k2 = intersect(*ZS[1], *ZS[2])
k3 = intersect(*ZS[2], (0, 0.55), (1, 0.55))
szp = [(22.62, 5.21), k0, k1, k2, k3, s1, s2, (26.36, 5.21)]
p.room("WE 1 – Schlafzimmer", szp, 13.00, label_pos=[24.9, 3.3])
p.room("WE 2 – Bad", [(16.98, 8.99), (19.64, 8.99), (19.64, 11.05), (16.98, 11.05)], 5.60)
p.room("WE 2 – Flur", [(19.81, 8.99), (21.50, 8.99), (21.50, 11.05), (19.81, 11.05)], 3.50)
p.room("WE 2 – Wohnen", [(21.65, 7.92), (23.15, 7.92), (23.15, 8.07), (26.36, 8.07), (26.36, 11.05), (21.65, 11.05)], 15.05,
       label_pos=[24.2, 9.6])
p.room("WE 2 – Kochen", [(21.65, 5.45), (23.15, 5.45), (23.15, 7.92), (21.65, 7.92)], 3.80)
p.room("WE 2 – Schlafen", [(23.30, 5.45), (26.36, 5.45), (26.36, 7.92), (23.30, 7.92)], 7.25)
p.room("AR", [(14.43, 5.78), (16.12, 5.78), (16.12, 7.15), (14.43, 7.15)], 2.30)
p.room("Fahrradabstellraum", [(16.98, 11.50), (26.36, 11.50), (26.36, 13.40), (16.98, 13.40)], 17.80)
p.room("Treppenhaus", [(16.26, 5.78), (21.35, 5.78), (21.35, 8.68), (16.26, 8.68)], show_area=False, label_pos=[17.0, 6.6])
p.room("Treppe", [(17.75, 5.78), (20.15, 5.78), (20.15, 8.68), (17.75, 8.68)], outline=True, show_area=False,
       subtitle="KG ↓ / OG ↑")
for i, (y0, y1) in enumerate([(0.32, 1.16), (1.26, 2.10), (2.20, 3.04)]):
    p.room(f"AR {9+i}", [(10.07, y0), (12.15, y0), (12.15, y1), (10.07, y1)], 1.75)
p.room("Stellplatzanlage", [(0.24, 0.32), (9.95, 0.32), (9.95, 3.20), (12.15, 3.20), (12.15, 7.79), (0.24, 7.79)],
       show_area=False, label_pos=[7.6, 5.0], subtitle="offen, Neubau darüber")
for i, (y0, y1) in enumerate([(0.32, 2.80), (2.80, 5.29), (5.29, 7.79)]):
    p.room(f"Stellplatz {i + 1}", [(0.24, y0), (5.54, y0), (5.54, y1), (0.24, y1)],
           outline=True, show_area=False, subtitle="Parklift")

# ---------------- Bemaßung
p.chain([0, 12.39, 12.41, 26.91], "x", 0, -1.2)
p.dim((0, 0), (26.91, 0), -2.2)
p.chain([12.41, 13.51, 14.41, 15.61, 16.51, 17.46, 18.36, 19.31, 20.21, 22.56, 23.46, 24.76], "x", 0, -0.6)
p.chain([0, 2.15, 14.05], "y", 26.91, -1.2)
p.chain([2.15, 3.50, 4.40, 6.75, 7.65, 8.55, 9.45, 10.25, 11.15, 11.75, 13.30, 14.05], "y", 26.91, -0.6)
p.dim((0, 0.02), (0, 7.79), 1.0)
p.chain([16.42, 26.91], "x", 14.05, 0.8)

# ---------------- Hinweise
p.note((14.6, 10.8), "Hof", size=3)
p.note((19.5, -3.2), "Raimundstraße", size=3)
p.note((29.6, 7.0), "Karl-Ferlemann-Straße", size=3)
p.note((6.2, 8.3), "Nordseite offen (Unterzug / Außenwand OG darüber)", size=2)
p.note((15.2, 12.6), "Durchgang 1,66", size=2)
p.note((12.80, 6.7), "Müll", size=2)

# ---------------- ungeprüft
p.unv((20.0, 5.5), "Nordwand WE 1: Innenkante 5,21 aus Plan 2010 abgegriffen; Bestandsplan 1999 und Plan 2026 zeigen 5,40", "Innenkante 5,21 (1999: 5,40)")
p.unv((23.4, 2.2), "Zickzackwand Bad/Schlafzimmer und Mauerpfeiler aus Plan 2026 (unbemaßt) übernommen, Maßstab über Fensterachsen 1999 (131,6 px/m), Lage ±10 cm. Bad damit 5,2 m² statt 6,35 m² (2010) bzw. ca. 6 m² (2026): Plan 2010 zeigt eine diagonal gestellte Wanne mit abweichender Wandführung, die im Scan nicht eindeutig lesbar ist", "Bad lt. 2026 – Fläche abw.")
p.unv((14.98, 4.6), "Küchenwand: im Plan 2026 als Wand, im Plan 2010 nur als Linie – Dicke 0,11 angenommen", "Dicke angenommen")
p.unv((20.5, 4.6), "Türbreiten (Rohbaurichtmaße) in den Scans unleserlich – Standardmaße 0,76/0,885/1,01 angenommen, Lage abgegriffen", "Türmaße angenommen")
p.unv((21.6, 13.75), "Nordwand: Innenkante 13,40 (2010 abgegriffen), 1999: 13,50; Außenkante 14,05 lt. 1999", "13,40 / 1999: 13,50")
p.unv((24.0, 11.28), "Wand WE 2/Fahrradraum: 11,05–11,50 aus 2010 abgegriffen, 1999: 11,25–11,55", "11,05–11,50 (1999 abw.)")
p.unv((24.2, 9.0), "WE 2 Wohnen/Schlafen: lt. Plan 15,05 / 7,25 m²; die im Plan 2010 gezeichnete Trennwand (7,92–8,07) ergibt 14,26 / 7,56 m². Summe beider Räume stimmt auf 2 % – Plan 2010 in sich widersprüchlich", "Flächen abw. (Plan 2010 widersprüchlich)")
p.unv((0.12, 4.0), "Neubau-Wanddicken lt. Bauantrag 1999 (0,24 / 0,30); Plan 2010 zeichnet ca. 0,36", "Wanddicke lt. 1999")
p.unv((16.7, 10.7), "Fenster Bad WE 2 zum Hof: Breite abgegriffen (ca. 0,64), Maßzahl unleserlich", "Breite abgegriffen")
p.unv((2.75, -0.35), "Öffnung in der Neubau-Südwand EG: Lage/Breite (ca. 1,00) aus Plan 2010 abgegriffen, Art (Fenster/Lüftung) unklar", "Öffnung abgegriffen")
p.unv((12.40, 3.0), "Fuge Neubau/Altbau 2 cm lt. 1999; Giebelwand Altbau 0,55 lt. 1999 (Plan 2026 zeichnet dünner)", "")
p.save('/home/user/hello-world/plans/KFS31/geometrie/EG.json')
for r in p.d["rooms"]:
    if r.get("area_stated"): print(f'{r["name"]:28s} {area(r["polygon"]):6.2f} / {r["area_stated"]}')
