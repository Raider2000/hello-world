"""Erzeugt geometrie/SB.json (Spitzboden) aus den am entzerrten Scan 1999 S. 12/13 abgegriffenen Werten.

Entzerrung: SB_entzerrung.py (Passpunkte: Maßkette Raimundstraße 0 / 12,15 / 12,40 / 12,86 und
26,91 sowie Maßkette 14,05 Karl-Ferlemann-Straße auf S. 13). Maßstab des Scans ca. 53,6 px/m bei 200 dpi.
"""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "geometrie" / "SB.json"
R = lambda v: round(v, 3)

# ---- abgegriffene / bemaßte Werte (m) -------------------------------------------------------
Y_S, Y_N = 3.97, 6.81          # Spitzbodenstreifen Süd (Neubau + Altbau Süd), Breite 2,84 lt. Plan
X_NB = 12.15                   # Neubau lichte Länge lt. Maßkette
X_BW0, X_BW1 = 12.41, 12.86    # Brandwand Altbau 0,45 lt. Maßkette
TW_T = 0.10                    # Trennwand („…KA F90“), Stärke abgegriffen
TW_X = 21.28                   # Achse senkrechter Teil
TW_TOP = (19.45, 7.58)         # oberer Knick (Diagonale 45°)
TW_K = (TW_X, 5.75)            # Knick Diagonale / senkrecht
TW_Y0 = 3.97                   # Süden Ende (Grenze lichte Höhe 1 m)
E_X0, E_X1 = 19.44, 22.94      # Spitzboden Ost, Breite 3,50 lt. Plan
E_Y0, E_Y1 = 4.00, 14.05       # Süd abgegriffen, Nord = Brandwand Nachbar

h = TW_T / 2
d = h * 2 ** 0.5               # Versatz der Wandflächen der 45°-Diagonale in x
c_axis = TW_TOP[0] + TW_TOP[1]  # Diagonale: x + y = c
c_w = c_axis - d                # Wandfläche SW
c_e = c_axis + d                # Wandfläche NO

def rect_sym(x0, y0, x1, y1, apex):
    """Bodentreppe: Rechteck mit Laufdreieck (Spitze an Seite 'apex')."""
    pts = [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]
    lines = []
    if apex == "W":
        lines = [[[x0, (y0 + y1) / 2], [x1, y1]], [[x0, (y0 + y1) / 2], [x1, y0]]]
    elif apex == "N":
        lines = [[[(x0 + x1) / 2, y1], [x0, y0]], [[(x0 + x1) / 2, y1], [x1, y0]]]
    rr = lambda p: [R(p[0]), R(p[1])]
    return {"polygons": [{"points": [rr(p) for p in pts]}], "lines": [[rr(a), rr(b)] for a, b in lines]}

# Bodentreppen (abgegriffen, nicht bemaßt)
BT = [
    ("BT_W11", 9.69, 6.08, 11.10, 6.80, "W"),
    ("BT_SUED", 15.28, 4.60, 16.56, 5.33, "W"),
    ("BT_OST", 21.73, 8.19, 22.45, 9.61, "N"),
]

plan = {
    "object": "KFS31",
    "floor": "SB",
    "floor_name": "Spitzboden",
    "source": {
        "file": "19990111-Grundrisse-Karl_Ferlemann_Str_31.pdf S. 12/13 (Grundriss Spitzboden -Gesamt-, M 1:100) · S. 18 (Schnitt A-A)",
        "date": "1999-01-11 (Plan 01.07.96 / 21.12.98)",
        "version": "Abgeschlossenheitsbescheinigung Reg.-Nr. 1999-009",
        "transformation": "Scan S. 12 über Maßkette Raimundstraße (0 / 12,15 / 12,40 / 12,86) und Kettenhöhe aus S. 13 "
                          "(Maßkette 14,05 Karl-Ferlemann-Straße, Endpunkt 26,91) entzerrt; Scherung/Verzug des Blatts "
                          "linear ausgeglichen (Restfehler ca. ±5 cm). Außenkontur aus DG.json übernommen.",
        "flaechen": "Plan nennt je Spitzboden F = halbe Grundfläche (anrechenbar, lichte Höhe 1–2 m) und in Klammern "
                    "die Grundfläche mit lichter Höhe ≥ 1 m; als area_stated dient der Klammerwert.",
    },
    "walls": [
        # Neubau Ostgiebel (0,24) und Altbau-Brandwand (0,45) an der Fuge, lt. Maßkette 12,15 / 24 / 2 / 45
        {"id": "G1", "a": [12.27, 0.02], "b": [12.27, 7.79], "thickness": 0.24, "align": "center", "type": "exterior"},
        {"id": "G2", "a": [R((X_BW0 + X_BW1) / 2), 0.0], "b": [R((X_BW0 + X_BW1) / 2), 7.79],
         "thickness": R(X_BW1 - X_BW0), "align": "center", "type": "exterior"},
        # Trennwand Spitzboden Altbau Süd / Ost
        {"id": "T1", "a": [R(TW_TOP[0]), R(TW_TOP[1])], "b": [R(TW_K[0]), R(TW_K[1])], "thickness": TW_T,
         "align": "center", "type": "interior"},
        {"id": "T2", "a": [R(TW_K[0]), R(TW_K[1])], "b": [R(TW_X), TW_Y0], "thickness": TW_T,
         "align": "center", "type": "interior"},
    ],
    "openings": [],
    "rooms": [
        {"name": "Spitzboden W11",
         "polygon": [[0.0, Y_S], [X_NB, Y_S], [X_NB, Y_N], [0.0, Y_N]],
         "area_stated": 34.51, "outline": True,
         "subtitle": "34,51 m² mit lichter Höhe ≥ 1 m (F = 17,26 m²)", "label_pos": [5.2, 5.6]},
        {"name": "Spitzboden W8 (Sondernutzung)",
         "polygon": [[X_BW1, Y_S], [R(TW_X - h), Y_S], [R(TW_X - h), R(c_w - (TW_X - h))],
                     [R(c_w - Y_N), Y_N], [X_BW1, Y_N]],
         "area_stated": 23.10, "outline": True, "name_size": 2.2,
         "subtitle": "23,10 m² mit lichter Höhe ≥ 1 m (A = 11,55 m²)", "label_pos": [16.6, 6.05]},
        {"name": "Spitzboden W7 (Sondernutzung)",
         "polygon": [[E_X0, E_Y1], [E_X1, E_Y1], [E_X1, E_Y0], [R(TW_X + h), E_Y0],
                     [R(TW_X + h), R(c_e - (TW_X + h))], [E_X0, R(c_e - E_X0)]],
         "area_stated": 30.52, "outline": True, "name_size": 2.0,
         "subtitle": "30,52 m² (≥ 1 m), F = 15,26 m²", "label_pos": [21.19, 11.6]},
    ],
    "symbols": [
        # Außenkante Rohbau lt. DG (im Spitzboden liegen hier Dachflächen/Traufen)
        {"id": "UMRISS", "layer": "A_SYMBOL", "lines": [
            [[0.0, 0.02], [12.39, 0.02]], [[12.39, 0.02], [12.39, 7.79]], [[12.39, 7.79], [0.0, 7.79]], [[0.0, 7.79], [0.0, 0.02]],
            [[12.41, 0.0], [24.76, 0.0]], [[24.76, 0.0], [26.91, 2.15]], [[26.91, 2.15], [26.91, 14.05]],
            [[26.91, 14.05], [16.44, 14.05]], [[16.44, 14.05], [16.44, 9.0]], [[16.44, 9.0], [15.71, 9.0]],
            [[15.71, 9.0], [15.71, 7.75]], [[15.71, 7.75], [12.41, 7.75]], [[12.41, 7.75], [12.41, 0.0]]]},
        # im Plan gestrichelt dargestellte Fortsetzung der Trennwand (unter der 1-m-Linie)
        {"id": "TW_GESTRICHELT", "layer": "A_SYMBOL", "lines": [
            [[R(TW_X - h), TW_Y0], [R(TW_X - h), 1.10]], [[R(TW_X + h), TW_Y0], [R(TW_X + h), 1.10]],
            [[R(TW_TOP[0]), R(TW_TOP[1])], [18.9, 8.07]], [[18.9, 8.07], [16.44, 8.07]]]},
    ] + [dict({"id": i, "layer": "A_TREPPE"}, **rect_sym(x0, y0, x1, y1, ap)) for i, x0, y0, x1, y1, ap in BT],
    "dimensions": [
        {"a": [0, 0], "b": [12.15, 0], "offset": -1.2},
        {"a": [12.15, 0], "b": [12.39, 0], "offset": -1.2, "label": " "},
        {"a": [12.39, 0], "b": [12.41, 0], "offset": -1.2, "label": " "},
        {"a": [12.41, 0], "b": [12.86, 0], "offset": -1.2, "label": " "},
        {"a": [12.15, 0], "b": [12.86, 0], "offset": -0.5, "label": "0,24 / 0,02 / 0,45"},
        {"a": [12.86, 0], "b": [26.91, 0], "offset": -1.2},
        {"a": [0, 0], "b": [26.91, 0], "offset": -2.2},
        {"a": [26.91, 0], "b": [26.91, 14.05], "offset": -1.4},
        {"a": [0, Y_S], "b": [0, Y_N], "offset": 1.0, "label": "2,84 lichte Höhe ≥ 1 m"},
        {"a": [E_X0, E_Y1], "b": [E_X1, E_Y1], "offset": 0.9, "label": "3,50 lichte Höhe ≥ 1 m"},
    ],
    "notes": [
        {"pos": [6.5, 10.5], "text": "Hof", "size": 3},
        {"pos": [13.5, -4.2], "text": "Raimundstraße", "size": 3},
        {"pos": [30.0, 7.0], "text": "Karl-Ferlemann-Straße", "size": 3},
        {"pos": [21.7, 14.4], "text": "vorhandene Nachbarbebauung", "size": 1.8, "anchor": "end"},
        {"pos": [-0.5, 9.2], "text": "vorh. Nachbarbebauung", "size": 1.8, "anchor": "start"},
        {"pos": [10.4, 5.75], "text": "Bodentreppe", "size": 1.6},
        {"pos": [15.92, 4.3], "text": "Bodentreppe", "size": 1.6},
        {"pos": [22.09, 7.85], "text": "Bodentreppe", "size": 1.6},
        {"pos": [13.35, 5.15], "text": "Höhenkote +13,22", "size": 1.6, "anchor": "start"},
        {"pos": [20.75, 6.95], "text": "Trennwand F 90", "size": 1.4, "anchor": "start"},
        {"pos": [6.1, 2.4], "text": "Dachfläche (lichte Höhe < 1 m)", "size": 1.8},
        {"pos": [6.1, 1.4], "text": "Neubau: Kehlbalken UK +12,94, First +15,22, Dachneigung 60°/20° (Schnitt A-A)", "size": 1.4},
        {"pos": [17.0, 2.4], "text": "Dachfläche (lichte Höhe < 1 m)", "size": 1.8},
        {"pos": [24.9, 11.0], "text": "Dachfläche", "size": 1.8},
    ],
    "unverified": [
        {"pos": [0.6, 6.3], "text": "Lage der Spitzbodenstreifen in y (3,97–6,81) aus dem entzerrten Scan abgegriffen (±5 cm); bemaßt ist nur die Breite 2,84 (lichte Höhe ≥ 1 m). Die Fläche 34,51 = 12,15 × 2,84 bestätigt Länge und Breite."},
        {"pos": [14.0, 4.4], "text": "Spitzboden Altbau Süd: Länge nicht bemaßt, Ostgrenze = Trennwand (x 21,23) abgegriffen; Fläche lt. Plan 23,10 m² stimmt mit der Zeichnung auf 0,4 % überein."},
        {"pos": [20.0, 13.5], "text": "Spitzboden Ost: x 19,44–22,94 abgegriffen (Breite 3,50 bemaßt), Südgrenze y 4,00 abgegriffen, Nordgrenze an der Brandwand y 14,05 angenommen."},
        {"pos": [20.2, 6.4], "text": "Trennwand zwischen den Altbau-Spitzböden: Beschriftung „…KA F90“ schlecht lesbar (F 90 oder F 30); Stärke 0,10 und Lage abgegriffen. Südlich der 1-m-Linie und nach Nordwesten bis zur Hoffassade im Plan nur gestrichelt (dünn dargestellt)."},
        {"pos": [18.0, 5.0], "text": "Zuordnung W7/W8: Kennzeichen im Süd-Spitzboden als „8“ gelesen, im Ost-Spitzboden unleserlich. Im DG-Plan 1999 (S. 10) liegt W8 im Südwestteil des Altbaus, W7 umfasste Nord- und Ostteil. Der Aufteilungsplan 2010 nummeriert W7 = Süd, W8 = Nord; ob die Sondernutzungsrechte durch die Nachträge 2010/2011 angepasst wurden, ist offen."},
        {"pos": [3.0, 4.4], "text": "W11: Teilungserklärung 1999 Nr. 1.2.11 nennt den über eine Bodentreppe erreichbaren Spitzboden „dazugehörend … ebenfalls mit W 11 bezeichnet“, anders als bei W7/W8 nicht ausdrücklich als Sondernutzungsrecht."},
        {"pos": [11.5, 6.3], "text": "Bodentreppen nicht bemaßt; Lage und Größe abgegriffen (ca. 1,41 × 0,72 / 1,28 × 0,73 / 0,72 × 1,42 m)."},
        {"pos": [12.64, 1.6], "text": "Brandwand/Giebel an der Fuge: Stärken lt. Maßkette (0,24 / 0,02 / 0,45); im Plan geschwärzt (über Dach) y 2,98–7,84, Umriss bis Traufe. Länge wie DG angenommen. Kamine sind im Plan nicht erkennbar."},
        {"pos": [26.0, 1.0], "text": "Außenkontur aus DG.json übernommen; der Spitzbodenplan zeigt Traufen mit Überstand (Süd ca. y −0,46, Ost ca. x 27,4). Dachgauben (Süd- und Ostseite) und Dachflächen sind nicht bemaßt und deshalb nicht gezeichnet."},
    ],
}

OUT.write_text(json.dumps(plan, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print("geschrieben:", OUT)
