"""Regelgeschosse OG1 / OG2 / DG (Stand 2010 S. 5/6/7, Maße 1999 S. 6–11)."""
import sys; sys.path.insert(0, '/tmp/kfs31/build')
from common import *

FLOORS = {
 "OG1": dict(name="1. Obergeschoss", page=5, p99="S. 6/7", we=("WE 3", "WE 4", "WE 5"),
   S={"Kochen": 4.00, "Wohnen/Essen": 25.40, "Flur": 4.90, "Kind": 8.00, "Bad": 6.65, "Schlafen": 13.95},
   N={"Wohnen": 21.00, "Schlafen": 17.00, "Flur": 6.60, "Kochen": 6.00, "Bad": 7.50, "Balkon": 6.30},
   W={"Kind": 15.45, "Schlafen": 11.50, "Flur": 2.85, "Bad": 5.90, "Wohnen": 28.30, "Garderobe": 0.90,
      "Du/WC": 3.00, "Flur 2": 3.75, "Kochen": 8.75, "Balkon": 3.76}),
 "OG2": dict(name="2. Obergeschoss", page=6, p99="S. 8/9", we=("WE 6", "WE 7", "WE 8"),
   S={"Kochen": 4.00, "Wohnen/Essen": 25.40, "Flur": 4.90, "Kind": 8.00, "Bad": 6.65, "Schlafen": 13.95},
   N={"Wohnen": 21.00, "Schlafen": 17.00, "Flur": 6.60, "Kochen": 6.00, "Bad": 7.50, "Balkon": 6.30},
   W={"Kind": 15.45, "Schlafen": 11.50, "Flur": 2.65, "Bad": 5.90, "Wohnen": 28.30, "Garderobe": 0.90,
      "Du/WC": 3.00, "Flur 2": 3.75, "Kochen": 8.75, "Balkon": 3.76}),
 "DG": dict(name="Dachgeschoss", page=7, p99="S. 10/11", we=("WE 9", "WE 10", "WE 11"),
   S={"Kochen": 4.00, "Wohnen/Essen": 25.40, "Flur": 4.90, "Kind": 8.00, "Bad": 6.85, "Schlafen": 13.95},
   N={"Wohnen": 21.00, "Schlafen": 17.00, "Flur": 6.80, "Kochen": 6.00, "Bad": 7.50, "Balkon": 6.30},
   W={"Kind": 15.45, "Schlafen": 11.15, "Flur": 2.65, "Bad": 3.55, "Wohnen": 28.30, "Garderobe": 0.90,
      "Du/WC": 3.00, "Flur 2": 3.75, "Kochen": 6.80, "Balkon": 3.76}),
}

def build(fl):
    F = FLOORS[fl]; wS, wN, wW = F["we"]
    SRC = {"file": f"20101111-Grundrisse-Karl_Ferlemann_Str_31.pdf S. {F['page']} (Raum/WE) · 19990111-…pdf {F['p99']} (Maße)",
           "date": "2010-11-11 / 1999-01-11", "version": "Aufteilungsplan WE 1–11"}
    p = Plan(fl, F["name"], SRC)
    T = 0.45  # Außenwand Altbau OG (1999: 0,45)
    # ---------- Altbau Außenwände
    p.aw("A1", (12.41, 0), (24.76, 0), T)
    for i, x in enumerate([13.51, 15.61, 17.46, 19.31, 22.56], 1):
        p.op(f"F_S{i}", "A1", "window", x, 0.90)
    p.aw("A2", (24.76, 0), (26.91, 2.15), T)
    p.op("F_E1", "A2", "window", (math.hypot(2.15, 2.15) - 0.90) / 2, 0.90, absolute=False)
    p.aw("A3", (26.91, 2.15), (26.91, 14.05), T)
    for i, y in enumerate([3.50, 6.75, 8.55, 10.25, 12.05], 1):
        p.op(f"F_O{i}", "A3", "window", y, 0.90)
    p.aw("A4", (26.91, 14.05), (16.44, 14.05), T)
    p.aw("A5", (16.44, 14.05), (16.44, 9.00), T)
    p.op("T_BK", "A5", "door", 10.20, 0.885, "start", "left")       # Balkontür WE N
    p.rw("A6", 15.71, 7.56, 16.18, 9.00, "exterior")                  # Treppenhaus Nordwest
    p.rw("A7", 12.41, 7.56, 15.71, 7.75, "exterior")                  # Treppe/Laubengang Nordwand
    p.rw("A8", 12.41, 0.45, 12.87, 5.85, "exterior")                  # Giebel zum Neubau
    p.rw("A9", 12.41, 5.85, 13.86, 6.12, "exterior")                  # Laubengang Brüstung Süd
    # ---------- tragende Innenwände
    p.rw("L1", 12.87, 5.38, 21.35, 5.85, "load-bearing")
    p.op("T_WES", "L1", "door", 20.25, 1.01, "start", "right")        # Wohnungstür Süd
    p.rw("L2", 21.35, 5.38, 26.46, 5.62, "load-bearing")
    p.rw("L3", 21.35, 5.62, 21.65, 8.71, "load-bearing")
    p.op("T_WEN", "L3", "door", 6.76, 0.885, "start", "right")        # Wohnungstür Nord
    p.rw("L4", 16.18, 8.71, 21.65, 9.00, "load-bearing")              # Treppenhaus / Wohnen N
    # ---------- Wohnung Süd (wie EG WE 1)
    p.rw("I2", 14.93, 2.99, 15.07, 5.38)
    p.rw("I3", 18.83, 0.45, 19.00, 5.38)
    p.op("T_WZ", "I3", "door", 4.30, 0.885, "end", "left")
    p.rw("I4", 19.00, 3.88, 21.34, 4.01)
    p.op("T_KI", "I4", "door", 19.06, 0.885, "start", "right")
    p.rw("I5", 21.34, 0.45, 21.52, 4.01)
    p.rw("I6", 21.52, 3.88, 22.52, 4.01)
    p.op("T_BD", "I6", "door", 21.60, 0.76, "start", "right")
    p.rw("I7", 22.52, 3.88, 22.62, 5.38)
    p.op("T_SZ", "I7", "door", 4.30, 0.885, "end", "right")
    ZB = [(22.435, 3.88), (23.27, 3.04), (22.61, 2.38), (24.535, 0.45)]
    ZT = [0.19, 0.32, 0.18]
    for i, (a, b) in enumerate(zip(ZB, ZB[1:]), 1):
        p.aw(f"I8{i}", a, b, ZT[i - 1], "left", "interior")
    p.aw("I84", (23.44, 0.45), (23.86, 1.04), 0.74, "right", "interior")
    ZS = [offset_poly([a, b], t) for (a, b), t in zip(zip(ZB, ZB[1:]), ZT)]
    # ---------- Wohnung Nord
    p.rw("I10", 23.12, 5.62, 23.27, 7.95)
    p.op("T_B2", "I10", "door", 6.40, 0.76, "start", "right")
    p.rw("I11", 22.85, 7.95, 26.46, 8.11)
    p.rw("I12", 22.85, 8.11, 23.00, 9.89)
    p.op("T_K2", "I12", "door", 9.05, 0.76, "end", "right")
    p.rw("I13", 21.65, 9.89, 26.46, 10.00)
    p.op("T_S2", "I13", "door", 21.75, 0.885, "start", "left")
    p.rw("I14", 21.49, 10.00, 21.65, 13.60)
    # ---------- Neubau (Wohnung West)
    p.rw("N1", 0, 0.02, 12.39, 0.32, "exterior")
    nsw = [(2.09, 1.01), (3.26, 1.01), (6.805, 1.01), (7.975, 1.01), (10.14, 1.01)] if fl == "DG" else \
          [(1.74, 1.01), (3.615, 1.01), (6.765, 2.26), (10.14, 1.01)]
    for i, (x, w) in enumerate(nsw, 1):
        p.op(f"F_NS{i}", "N1", "window", x, w)
    p.rw("N2", 0, 7.49, 12.39, 7.79, "exterior")
    p.op("F_NN1", "N2", "window", 3.365, 1.01)
    p.op("T_NBK", "N2", "door", 7.70, 1.01, "end", "right")          # Balkontür
    p.op("F_NN2", "N2", "window", 10.90, 0.75)                        # Rundfenster Ø 0,75
    p.rw("N3", 0, 0.32, 0.24, 7.49, "exterior")
    p.rw("N4", 12.15, 0.32, 12.39, 7.49, "exterior")
    p.op("T_WEW", "N4", "door", 6.12, 1.01, "end", "left")            # Wohnungstür vom Laubengang
    p.rw("N5", 2.95, 0.32, 3.07, 4.70)
    p.op("T_NSZ", "N5", "door", 3.04, 0.885, "end", "right")
    p.rw("N6", 0.24, 4.56, 2.95, 4.70)
    p.rw("N7", 3.07, 4.12, 5.36, 4.21)
    p.op("T_NKI", "N7", "door", 3.40, 0.885, "end", "left")
    p.rw("N8", 3.07, 2.87, 5.36, 2.97)
    p.op("T_NBD", "N8", "door", 3.45, 0.76, "end", "right")
    p.rw("N9", 5.36, 0.32, 5.59, 2.97, "load-bearing")
    p.rw("N10", 5.36, 4.12, 5.59, 7.49, "load-bearing")
    p.rw("N11", 9.55, 0.32, 9.66, 7.49)
    p.op("T_NKU", "N11", "door", 1.76, 0.80, "start", "right")
    p.op("T_NFL", "N11", "door", 5.99, 0.80, "end", "left")
    p.rw("N12", 10.53, 3.81, 12.15, 3.95)
    p.rw("N13", 10.53, 3.95, 10.63, 5.98)
    p.rw("N14", 10.63, 5.90, 12.15, 5.98)
    p.op("T_NDU", "N14", "door", 10.70, 0.76, "start", "right")
    p.rw("N15", 9.66, 4.82, 10.53, 4.95)
    # ---------- Räume Süd
    S, N, W = F["S"], F["N"], F["W"]
    p.room(f"{wS} – Kochen", [(12.87, 3.47), (14.93, 3.47), (14.93, 5.38), (12.87, 5.38)], S["Kochen"])
    p.room(f"{wS} – Wohnen/Essen", [(12.87, 0.45), (18.83, 0.45), (18.83, 5.38), (15.07, 5.38), (15.07, 2.99),
           (14.93, 2.99), (14.93, 3.47), (12.87, 3.47)], S["Wohnen/Essen"], label_pos=[15.9, 1.6])
    p.room(f"{wS} – Kind", [(19.00, 0.45), (21.34, 0.45), (21.34, 3.88), (19.00, 3.88)], S["Kind"])
    p.room(f"{wS} – Flur", [(19.00, 4.01), (22.52, 4.01), (22.52, 5.38), (19.00, 5.38)], S["Flur"])
    p.room(f"{wS} – Bad", [(21.52, 0.45), (23.44, 0.45), (23.86, 1.04), ZB[2], ZB[1], ZB[0], (21.52, 3.88)], S["Bad"],
           label_pos=[22.05, 2.6])
    ch = offset_poly([(24.76, 0), (26.91, 2.15)], T)
    s1 = intersect(*ch, (0, T), (1, T)); s2 = intersect(*ch, (26.46, 0), (26.46, 1))
    k0 = intersect(*ZS[0], (22.62, 0), (22.62, 1)); k1 = intersect(*ZS[0], *ZS[1]); k2 = intersect(*ZS[1], *ZS[2])
    k3 = intersect(*ZS[2], (0, T), (1, T))
    p.room(f"{wS} – Schlafen", [(22.62, 5.38), k0, k1, k2, k3, s1, s2, (26.46, 5.38)], S["Schlafen"], label_pos=[24.9, 3.3])
    # ---------- Räume Nord
    p.room(f"{wN} – Wohnen", [(16.89, 9.00), (20.75, 9.00), (20.75, 10.00), (21.49, 10.00), (21.49, 13.60), (16.89, 13.60)], N["Wohnen"])
    p.room(f"{wN} – Schlafen", [(21.65, 10.00), (26.46, 10.00), (26.46, 13.60), (21.65, 13.60)], N["Schlafen"])
    p.room(f"{wN} – Flur", [(21.65, 5.62), (23.12, 5.62), (23.12, 7.95), (22.85, 7.95), (22.85, 9.89), (21.65, 9.89), (21.65, 10.00), (20.75, 10.00), (20.75, 9.00), (21.65, 9.00)],
           N["Flur"], label_pos=[22.2, 8.9])
    p.room(f"{wN} – Kochen", [(23.00, 8.11), (26.46, 8.11), (26.46, 9.89), (23.00, 9.89)], N["Kochen"])
    p.room(f"{wN} – Bad", [(23.27, 5.62), (26.46, 5.62), (26.46, 7.95), (23.27, 7.95)], N["Bad"])
    p.room(f"{wN} – Balkon", [(14.96, 9.38), (16.44, 9.38), (16.44, 13.60), (14.96, 13.60)], N["Balkon"], outline=True)
    # ---------- Räume Neubau
    p.room(f"{wW} – Kind", [(0.24, 4.70), (3.07, 4.70), (3.07, 4.21), (5.36, 4.21), (5.36, 7.49), (0.24, 7.49)], W["Kind"])
    p.room(f"{wW} – Schlafen", [(0.24, 0.32), (2.95, 0.32), (2.95, 4.56), (0.24, 4.56)], W["Schlafen"])
    p.room(f"{wW} – Flur", [(3.07, 2.97), (5.59, 2.97), (5.59, 4.12), (3.07, 4.12)], W["Flur"])
    p.room(f"{wW} – Bad", [(3.07, 0.32), (5.36, 0.32), (5.36, 2.87), (3.07, 2.87)], W["Bad"])
    p.room(f"{wW} – Wohnen", [(5.59, 0.32), (9.55, 0.32), (9.55, 7.49), (5.59, 7.49)], W["Wohnen"])
    p.room(f"{wW} – Kochen", [(9.66, 0.32), (12.15, 0.32), (12.15, 3.81), (9.66, 3.81)], W["Kochen"])
    p.room(f"{wW} – Garderobe", [(9.66, 4.95), (10.53, 4.95), (10.53, 5.98), (9.66, 5.98)], W["Garderobe"], show_area=False)
    p.room(f"{wW} – Du/WC", [(10.63, 3.95), (12.15, 3.95), (12.15, 5.90), (10.63, 5.90)], W["Du/WC"])
    p.room(f"{wW} – Flur 2", [(9.66, 5.98), (12.15, 5.98), (12.15, 7.49), (9.66, 7.49)], W["Flur 2"])
    p.room(f"{wW} – Balkon", [(7.03, 7.79), (9.54, 7.79), (9.54, 9.29), (7.03, 9.29)], W["Balkon"], outline=True,
           subtitle="3,76 m² (Fläche zur Hälfte)")
    # ---------- Treppenhaus
    p.room("Treppenhaus", [(13.86, 5.85), (21.35, 5.85), (21.35, 8.71), (16.18, 8.71), (16.18, 7.56), (13.86, 7.56)],
           show_area=False, label_pos=[20.5, 7.4])
    p.room("Treppe", [(17.60, 5.85), (19.95, 5.85), (19.95, 8.71), (17.60, 8.71)], outline=True, show_area=False,
           subtitle="↓ / ↑")
    p.room("Lauf", [(13.86, 6.50), (16.18, 6.50), (16.18, 7.56), (13.86, 7.56)], outline=True, show_area=False,
           subtitle="Halbgeschoss Neubau")
    p.room("Laubengang", [(12.41, 6.12), (13.86, 6.12), (13.86, 7.56), (12.41, 7.56)], show_area=False, label_pos=[13.1, 6.7])
    # ---------- Bemaßung
    p.chain([0, 12.39, 12.41, 26.91], "x", 0, -1.2)
    p.dim((0, 0), (26.91, 0), -2.2)
    p.chain([12.41, 13.51, 14.41, 15.61, 16.51, 17.46, 18.36, 19.31, 20.21, 22.56, 23.46, 24.76], "x", 0, -0.6)
    pts = [0] + [v for x, w in nsw for v in (x, x + w)] + [12.39]
    p.chain(pts, "x", 0.02, -0.6)
    p.chain([0, 2.15, 14.05], "y", 26.91, -1.2)
    p.chain([2.15, 3.50, 4.40, 6.75, 7.65, 8.55, 9.45, 10.25, 11.15, 12.05, 12.95, 14.05], "y", 26.91, -0.6)
    p.dim((0, 0.02), (0, 7.79), 1.0)
    p.chain([0, 3.365, 4.375, 7.03, 9.54, 10.90, 11.65, 12.39], "x", 7.79, 0.8)
    p.chain([16.44, 26.91], "x", 14.05, 0.8)
    p.note((14.0, 10.8), "Hof", size=3)
    p.note((19.5, -3.2), "Raimundstraße", size=3)
    p.note((29.6, 7.0), "Karl-Ferlemann-Straße", size=3)
    # ---------- ungeprüft
    p.unv((6.0, 8.6), f"WE-Nummern {wS}/{wN}/{wW} angenommen (Stempel im Scan 2010 unleserlich); Zählung wie EG: Altbau Süd, Altbau Nord, Neubau",
          "WE-Nr. angenommen")
    p.unv((23.2, 2.3), "Zickzackwand Bad/Schlafen wie EG (Stand 2026 WE 1) übernommen; Plan 2010 zeigt hier dieselbe Wandführung, Lage ±10 cm",
          "Lage wie EG")
    p.unv((20.6, 4.7), "Türbreiten/Aufschläge unleserlich – Standardmaße angenommen, Lage abgegriffen", "Türmaße angenommen")
    p.unv((5.0, 0.0), "Fenster Neubau Süd lt. Maßkette 1999; Plan 2010 zeigt sie ca. 0,24 m weiter westlich und das Wohnzimmerfenster zweiteilig",
          "Fenster lt. 1999")
    p.unv((21.0, 9.5), "Flur WE Nord: offener Übergang zum Wohnen; Raumgrenze bei x = 20,75 so angenommen, dass beide Flächen lt. Plan passen",
          "Flur-Abgrenzung")
    p.unv((13.1, 7.2), "Laubengang/Treppe West: Wandführung im Scan 2010 nur schematisch, Brüstungen angenommen", "angenommen")
    p.unv((8.3, 9.3), "Balkon Neubau: Tiefe 1,50 aus Plan 2010 abgegriffen, Breite 2,51 lt. 1999", "Tiefe abgegriffen")
    if fl == "DG":
        p.room("Dachschräge", [(0.24, 0.32), (12.15, 0.32), (12.15, 0.99), (0.24, 0.99)], outline=True, show_area=False,
               subtitle="gestrichelte Linie lt. Plan 2010", label_pos=[7.6, 0.55])
        p.unv((4.2, 1.4), "DG Neubau: gestrichelte Linie y ≈ 0,99 (Dachschräge, Höhe nicht angegeben). Flächen lt. Plan 2010 (Schlafen 11,15, Bad 3,55, Kochen 6,80) "
              "sind kleiner als die Grundfläche – vermutlich Abzug nach WoFlV und/oder abweichende Trennwände; DG-Schnitt 1999 (S. 11) prüfen",
              "Dachschräge – Flächen abw.")
    if fl == "DG":
        p.unv((18.0, -0.35), "DG Altbau: Fenster wie OG übernommen (Plan 2010 zeigt sie an gleicher Stelle); Bauantrag 1999 S. 10/11 bemaßt im DG abweichende Öffnungen (Gauben?) – prüfen",
              "Fenster wie OG")
    if fl in ("OG2", "DG"):
        p.unv((4.3, 3.6), "Flur Neubau: Plan 2010 schreibt 2,65 m² (OG1: 2,85 m²) bei identischer Zeichnung – Lesefehler oder Planfehler",
              "2,65 lt. Plan?")
    return p

if __name__ == "__main__":
    for fl in sys.argv[1:]:
        p = build(fl)
        p.save(f'/home/user/hello-world/plans/KFS31/geometrie/{fl}.json')
