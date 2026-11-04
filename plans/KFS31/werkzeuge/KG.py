import sys; sys.path.insert(0, '/tmp/kfs31/build')
from common import *
SRC = {"file": "20101111-Grundrisse-Karl_Ferlemann_Str_31.pdf S. 3 (Raumaufteilung) · 19990111-…pdf S. 2/3 (Maße)",
       "date": "2010-11-11 / 1999-01-11", "version": "Aufteilungsplan, Kellergeschoss"}
p = Plan("KG", "Kellergeschoss", SRC)
X1, Y1, C = 27.01, 14.10, 2.185          # Außenmaße KG lt. 1999 (14,60 x 14,10), Abschrägung 2,185
# ---------- Außenwände
p.aw("A1", (12.41, 0), (X1 - C, 0), 0.75)
for i, x in enumerate([13.66, 15.51, 17.61, 19.46, 22.71], 1):
    p.op(f"F_S{i}", "A1", "window", x, 0.70)
p.aw("A2", (X1 - C, 0), (X1, C), 0.75)
p.op("F_E1", "A2", "window", (math.hypot(C, C) - 0.70) / 2, 0.70, absolute=False)
p.aw("A3", (X1, C), (X1, Y1), 0.75)
for i, y in enumerate([3.65, 6.90, 8.70, 10.40], 1):
    p.op(f"F_O{i}", "A3", "window", y, 0.70)
p.aw("A4", (X1, Y1), (16.46, Y1), 0.70)
p.rw("A5", 16.46, 8.59, 17.11, 13.40, "exterior")      # Nordflügel West (Hof)
p.rw("A6", 15.75, 8.59, 16.46, 9.24, "exterior")
p.rw("A7", 15.75, 5.89, 16.30, 8.59, "exterior")       # AR West (Hof)
p.rw("A8", 13.06, 5.33, 15.75, 5.89, "exterior")       # Hofwand über Kellerflur
p.rw("A9", 12.41, 0.75, 13.06, 5.89, "exterior")       # Giebel West (Neubau nicht unterkellert)
# ---------- tragende Innenwände
p.rw("L1", 16.30, 5.41, 21.20, 5.87, "load-bearing")   # Kellerflur / AR, Treppe
p.rw("L2", 21.20, 0.78, 21.65, 3.00, "load-bearing")
p.rw("L2b", 21.20, 4.05, 21.65, 6.54, "load-bearing")
p.rw("L3", 21.06, 8.59, 21.40, 11.14, "load-bearing")  # Keller 8,10 / Keller 6,85
p.rw("L4", 17.11, 11.14, 26.26, 11.60, "load-bearing")
p.rw("L5", 16.30, 8.59, 21.06, 9.03, "load-bearing")   # Treppe / Keller 8,10
p.rw("L6", 22.97, 2.95, 23.79, 3.01)
p.rw("L7", 23.79, 2.59, 26.26, 2.65)
p.rw("L8", 22.97, 3.01, 23.03, 5.45)
p.op("T_K77", "L8", "door", 3.40, 0.80, "end", "left")
p.rw("L9", 23.03, 5.41, 26.26, 5.77, "load-bearing")
p.rw("L10", 23.07, 5.77, 23.55, 7.80, "load-bearing")
p.op("T_HR", "L10", "door", 6.06, 0.87, "start", "right")
p.rw("L11", 22.84, 7.80, 24.26, 8.20, "load-bearing")   # Wandstummel mit Kamin
p.rw("L12", 23.22, 8.20, 23.41, 11.14)
p.rw("L13", 23.41, 9.57, 26.26, 9.92)
# ---------- Kellerverschläge (Süd), Flurwand mit Türen
p.rw("V1", 14.74, 0.78, 14.97, 4.14)
p.rw("V2", 16.58, 0.78, 16.65, 3.64)
p.rw("V3", 18.92, 0.78, 18.99, 3.64)
p.rw("V4", 14.97, 3.64, 21.20, 4.09)
p.op("T_K2", "V4", "door", 15.07, 0.88, "start", "right")
p.op("T_K3", "V4", "door", 17.34, 0.84, "start", "right")
p.op("T_K4", "V4", "door", 19.74, 0.84, "end", "right")
p.rw("V5", 14.74, 5.17, 14.97, 5.33)
p.rw("V6", 21.65, 2.95, 22.97, 3.01)
# ---------- Räume
ch = offset_poly([(X1 - C, 0), (X1, C)], 0.75)
s1 = intersect(*ch, (0, 0.78), (1, 0.78)); s2 = intersect(*ch, (0, 2.59), (1, 2.59))
p.room("Keller (1)", [(13.06, 0.78), (14.74, 0.78), (14.74, 5.33), (13.06, 5.33)], 7.70)
p.room("Keller (2)", [(14.97, 0.78), (16.58, 0.78), (16.58, 3.64), (14.97, 3.64)], 5.10)
p.room("Keller (3)", [(16.65, 0.78), (18.92, 0.78), (18.92, 3.64), (16.65, 3.64)], 6.80)
p.room("Keller (4)", [(18.99, 0.78), (21.20, 0.78), (21.20, 3.64), (18.99, 3.64)], 7.50)
p.room("Keller (5)", [(21.65, 0.78), s1, s2, (23.79, 2.59), (23.79, 2.95), (21.65, 2.95)], 8.20, label_pos=[23.0, 1.7])
p.room("Keller (6)", [(23.03, 3.01), (23.79, 3.01), (23.79, 2.65), (26.26, 2.65), (26.26, 5.41), (23.03, 5.41)], 7.70)
p.room("HR/Technik", [(23.55, 5.77), (26.26, 5.77), (26.26, 9.57), (23.41, 9.57), (23.41, 8.20), (24.26, 8.20), (24.26, 7.80), (23.55, 7.80)], 9.85, label_pos=[25.0, 6.8])
p.room("Keller (7)", [(21.40, 8.20), (23.22, 8.20), (23.22, 11.14), (21.40, 11.14)], 6.85)
p.room("ELT", [(23.41, 9.92), (26.26, 9.92), (26.26, 11.14), (23.41, 11.14)], 3.80)
p.room("Keller (8)", [(17.11, 9.03), (21.06, 9.03), (21.06, 11.14), (17.11, 11.14)], 8.10)
p.room("AR", [(16.30, 5.87), (17.92, 5.87), (17.92, 8.59), (16.30, 8.59)], 5.85)
p.room("Treppe", [(17.92, 5.87), (20.05, 5.87), (20.05, 8.59), (17.92, 8.59)], outline=True, show_area=False, subtitle="↑ EG")
p.room("Kellerflur", [(14.97, 4.09), (21.20, 4.09), (21.20, 5.41), (14.97, 5.41)], show_area=False)
p.room("Flur", [(21.65, 3.01), (22.97, 3.01), (22.97, 5.45), (23.03, 5.45), (23.03, 5.77), (23.07, 5.77),
                (23.07, 7.80), (22.84, 7.80), (22.84, 8.20), (21.40, 8.20),
                (21.40, 8.59), (21.20, 8.59), (21.20, 6.54), (21.65, 6.54)], show_area=False, label_pos=[22.2, 6.8])
p.room("Raum ohne Bezeichnung", [(17.11, 11.60), (26.26, 11.60), (26.26, 13.40), (17.11, 13.40)], show_area=False)
p.room("Schacht/Hof (nicht unterkellert)", [(13.06, 5.89), (15.75, 5.89), (15.75, 7.72), (13.91, 7.72), (13.91, 5.89)],
       outline=True, show_area=False, label_pos=[14.8, 6.8])
# ---------- Bemaßung
p.chain([12.41, X1], "x", 0, -2.0)
p.chain([12.41, 13.66, 14.36, 15.51, 16.21, 17.61, 18.31, 19.46, 20.16, 22.71, 23.41, X1 - C], "x", 0, -1.2)
p.chain([12.41, 13.06, 16.31, 16.76, 18.86, 19.21, 21.26, 21.71, 26.26, X1], "x", 0.78, -0.4)
p.chain([0, C, Y1], "y", X1, -2.0)
p.chain([C, 3.65, 4.35, 6.90, 7.60, 8.70, 9.40, 10.40, 11.10, Y1], "y", X1, -1.2)
p.chain([0, 0.75, 5.45, 5.80, 7.80, 8.20, 11.30, 11.75, 13.40, Y1], "y", 26.26, -0.4)
p.note((12.3, 3.0), "← Neubau nicht unterkellert (Grube Parklift)", size=2.2, anchor="end")
p.note((19.5, -3.4), "Raimundstraße", size=3)
p.note((30.0, 7.0), "Karl-Ferlemann-Straße", size=3)
# ---------- ungeprüft
p.unv((17.0, 2.2), "Kellerverschläge: Zuordnung zu den WE in 2010 unleserlich (1999: W 3, W 4, W 6, W 9–W 11 …); Trennwände als Lattenverschläge ca. 0,07, Lage aus Plan 2010 abgegriffen, Flächen nur näherungsweise",
      "Verschläge schematisch")
p.unv((21.4, 13.6), "Innenwände/Innenkanten aus Plan 2010 abgegriffen (±5 cm); Maßketten 1999 weichen teils ab (z. B. tragende Wand 21,26–21,71 statt 21,20–21,65)", "Innenmaße abgegriffen")
p.unv((14.8, 6.3), "Bereich Hof/Schacht zwischen Kellerflur und AR: im Plan 2010 nur Umriss mit Quadrat (Schacht?), nicht bezeichnet", "Schacht?")
p.unv((17.1, 7.2), "AR 5,85 m² lt. Plan, gezeichnete Abgrenzung zur Treppe ergibt 4,41 m² – Treppenbreite/Lage unsicher", "Fläche abw.")
p.unv((22.3, 9.4), "Keller 6,85: Begrenzung im Scan unklar (Wandstummel, Tür bei y 9,93); als 21,40–23,22 × 8,20–11,14 angenommen", "Begrenzung angenommen")
p.unv((21.7, 12.5), "Nördlicher Raum 17,11–26,26 × 11,60–13,40 ohne Bezeichnung und Flächenangabe (evtl. nicht nutzbar/verfüllt)", "ohne Bez.")
p.save('/home/user/hello-world/plans/KFS31/geometrie/KG.json')
