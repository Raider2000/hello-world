# Geschoss-Konfiguration für build.py (Koordinaten im gemeinsamen System, Meter)
SRC_AP = 'plans/RBS25/quelle/20140801-Aufteilungsplan_Grundrisse_RB25.pdf'
SRC_BEM = 'plans/RBS25/quelle/Grundriss_WE05_urspruenglich_bemasst.pdf'


def trafo(fl, ox, oy, extra=''):
    return (f'Quelle: Vektor-PDF {SRC_AP.split("/")[-1]} (1 Seite, 2965 x 1701 pt, M 1:100, y nach unten), '
            f'Ausschnitt {fl}. Gemeinsames System aller Geschosse: Meter, y nach oben, Ursprung = linke untere '
            f'Rohbau-Außenecke des Hauptbaukörpers (Brandwand zu Haus Nr. 23 / Straßenfassade). '
            f'x_m = (x_pt - {ox}) / 28.3465, y_m = ({oy} - y_pt) / 28.3465 (1 m = 28,3465 pt bei 1:100), '
            f'gerundet auf mm. Wandflächen = graue (Bestand) und rote (Neubau 2014) Füllungen des Plans, '
            f'gelbe Füllungen (Abbruch 2014) entfallen. Türen aus den Aufschlagbögen, Fenster aus den Lücken '
            f'der Außenwände, Räume = Freiflächen zwischen den Wänden.' + extra)


def chain(pts, labels, at, offset, horizontal=True):
    """Maßkette über Punkte (x bei horizontal, sonst y) auf Linie 'at'."""
    out = []
    for i, (p, q) in enumerate(zip(pts, pts[1:])):
        a, b = ([p, at], [q, at]) if horizontal else ([at, p], [at, q])
        d = {'a': a, 'b': b, 'offset': offset}
        if labels and labels[i] is not None:
            d['label'] = labels[i]
        out.append(d)
    return out


TRAGEND_UNV = ('Wandtyp „tragend“ (load-bearing) nicht belegt: Wände, die im Aufteilungsplan 2014 in KG, EG, 1. OG '
               'und 2. OG übereinanderstehen (Überdeckung ≥ 60 %, Toleranz 6 cm), sind als tragend gezeichnet – '
               'plausibel, aber ohne Statik/Aufmaß nicht geprüft.')
ZIEL_UNV = ('Darstellung = Zielzustand des Aufteilungsplans 2014: rote Wände (Neubau 2014) schraffiert als „neu“, '
            'gelbe Wände (Abbruch 2014) weggelassen, gestrichelte Türen (geplant/entfallend) nicht gezeichnet. '
            'Ob die Maßnahmen ausgeführt wurden, ist außer für WE05 (Sanierung 2026) nicht belegt.')


STD_CHAINS = [
    dict(axis='x', at=1.0, base=0.0, offset=-0.61),
    dict(axis='y', at=0.3, base=0.0, offset=1.0),
    dict(axis='y', at=15.5, base=16.548, offset=-2.95),
    dict(axis='x', at=9.0, base=9.83, offset=2.95, total=False),
]

CFG = {}

# ------------------------------------------------------------------ OG2
CFG['OG2'] = dict(
    floor_name='2. Obergeschoss – gesamte Etage (WE5 nach Sanierung, WE6, Treppenhaus)',
    margin=3.4,
    source={
        'file': SRC_AP,
        'date': '2014-08-01 / 2026-09-12',
        'version': 'Aufteilungsplan 2014 (Etage) + WE05-GR-01 v1 (WE05 nach Sanierung, neueste Fassung)',
        'transformation': trafo('2. OG', 1192.44, 494.16,
            ' WE05 (Zustand nach Sanierung) aus der bisherigen OG2.json (git a72cce5) übernommen: '
            'x_neu = x_alt - 0.010, y_neu = y_alt. Die Brandwand links ist damit 0,125 m stark '
            '(16,515 - Summe der Kette 16,39 m), ihre Außenkante bleibt bei x = 0. Die 6,85-m-Kette liegt '
            'bei x = 0,125 ... 6,975 m. WE05-Bereich (x < 6,99 m bzw. x < 8,235 m oberhalb y = 5,50 m) '
            'ersetzt den Aufteilungsplan.'),
        'reference': [SRC_BEM, 'plans/RBS25/quelle/vorgaenger_WE05/build_plan.py',
                      'plans/RBS25/quelle/OG2_WE05_bestand_vektoren.json',
                      'plans/RBS25/quelle/vorgaenger_WE05/Pruefprotokoll.json'],
    },
    we05_region=[(-4, -4), (6.975, -4), (6.975, 5.50), (8.225, 5.50), (8.225, 14), (-4, 14)],
    we05_load_bearing=['W-wohnen-schlafen', 'W-schlafen-flur-links', 'W-schlafen-flur-rechts',
                       'W-kueche-flur', 'W-wohnen-essen-rest-links', 'wohnen-essen-rest-rechts'],
    we05_drop_dims=['3,25', ' ', '3,21', '6,85', '9,84', 'ca. 3,00', 'ca. 2,50'],
    we05_drop_notes=['0,15', '0,24', '← Zugang WE05 (Treppenhaus)'],
    we05_drop_unverified=[
        'ca. 3,00 m Balkonbreite: im Vorgänger nur abgeleitet',
        'ca. 2,50 m Balkontiefe: im Vorgänger nur abgeleitet',
        'Balkon (Metallkonstruktion): Geometrie 3,00 x 2,50 m = 7,5 m2 aus Vorgänger widerspricht 3,75 m2 laut Gesamtplan (4 Balkone übereinander); Geländer nicht gezeichnet',
        'Essen: keine gesicherte Fläche, berechnet (Fertigmaß-Polygon aus Vorgänger)',
        'Kochen: keine gesicherte Fläche, berechnet',
        'Bad: keine gesicherte Fläche (5,58 m2 gehört zum Vorzustand), berechnet aus ca.-Lichtmaßen',
    ],
    we05_dim_patch={'ca. 3,44@8.235': {'offset': 0.6}, 'ca. 3,65@6.985': {'offset': 0.35}},
    we05_unv_patch={'ca. 3,44 m Bad-Tiefe': {'pos': [7.55, 7.54]}, 'ca. 3,65 m Raumtiefe Schlafen': {'pos': [6.4, 2.395]}},
    we05_room_patch={
        'Balkon': {'subtitle': '½ 3,75 m² (Mietfläche)', 'show_area': False, 'name_size': 2.2},
        'Essen': {'subtitle': '11,18 m² (berechnet)'},
        'Kochen': {'subtitle': '5,69 m² (berechnet)'},
        'Bad': {'subtitle': '7,91 m² (berechnet)'},
    },
    rooms=[
        dict(name='WE6 – Kind', pos=[9.78, 7.40], area_stated=11.49),
        dict(name='WE6 – WC', pos=[12.29, 7.85], label=[12.29, 8.45], name_size=1.6),
        dict(name='WE6 – Bad', pos=[13.69, 9.95], label=[14.4, 10.15], area_stated=5.92),
        dict(name='WE6 – Kochen', pos=[14.84, 7.00]),
        dict(name='WE6 – Flur', pos=[11.30, 4.90], area_stated=5.34),
        dict(name='WE6 – Schlafen', pos=[10.98, 2.30], area_stated=11.72),
        dict(name='WE6 – Wohnen/Essen', pos=[14.42, 2.30], area_stated=15.66),
        dict(name='Treppenhaus', pos=[8.08, 2.60], label=[8.08, 1.0], show_area=False, name_size=2.0),
    ],
    balconies=[dict(name='WE6 – Balkon', label=[17.54, 4.40], subtitle='½ 3,75 m² (bemaßt)')],
    stairs=[(6.80, 0.58, 9.40, 5.42)],
    north=(17.2, 0.0, 19.4, 2.6),
    notes=[
        {'pos': [7.49, 4.88], 'text': 'WE 5', 'size': 1.6},
        {'pos': [8.71, 4.88], 'text': 'WE 6', 'size': 1.6},
        {'pos': [-0.25, 5.2], 'text': 'Nachbarhaus Nr. 23', 'size': 2.0, 'anchor': 'end'},
        {'pos': [14.3, 12.3], 'text': 'Nachbarhaus Nr. 45', 'size': 2.0},
        {'pos': [8.15, 4.35], 'text': '+5,50', 'size': 1.5},
        {'pos': [8.08, 0.62], 'text': '2 × 8 Stg. 30/17,2', 'size': 1.4},
        {'pos': [3.45, -0.94], 'text': '0,15', 'size': 1.6},
        {'pos': [6.855, -0.94], 'text': '0,24', 'size': 1.6},
        {'pos': [9.297, -0.94], 'text': '0,24', 'size': 1.6},
        {'pos': [12.712, -0.94], 'text': '0,15', 'size': 1.6},
        {'pos': [19.83, 5.65], 'text': '0,27', 'size': 1.6, 'anchor': 'start'},
        {'pos': [19.83, 9.16], 'text': '0,30', 'size': 1.6, 'anchor': 'start'},
        {'pos': [19.83, 11.29], 'text': '0,22⁵', 'size': 1.6, 'anchor': 'start'},
    ],
    barriers=[[[13.2, 5.535], [15.6, 5.535]], [[13.2, 5.765], [15.6, 5.765]], [[12.70, 9.20], [14.05, 9.20]]],
    dimensions=(
        chain([0.0, 0.125, 3.375, 3.525, 6.735, 6.975, 9.178, 9.419, 12.636, 12.789, 15.957, 16.527],
              [' ', '3,25', ' ', '3,21', ' ', '2,20', ' ', '3,22', ' ', '3,16', '0,57'], 0.0, -0.61)
        + [{'a': [0.0, 0.0], 'b': [16.527, 0.0], 'offset': -1.41, 'label': '16,51⁵'}]
        + chain([0.0, 0.572, 5.512, 5.783, 9.013, 9.313, 11.172, 11.405],
                ['0,57', '4,94', ' ', '3,23', ' ', '1,86', ' '], 16.548, -2.95, horizontal=False)
        + [{'a': [16.548, 0.0], 'b': [16.548, 11.405], 'offset': -4.3, 'label': '11,39⁵'},
           {'a': [0.0, 0.0], 'b': [0.0, 9.84], 'offset': 1.415, 'label': '9,84'},
           {'a': [0.0, 9.84], 'b': [12.167, 9.84], 'offset': 2.95, 'label': '12,15'}]
    ),
    unverified=[
        {'pos': [16.9, -1.41], 'short': '', 'text': 'Kontrollmaß Gesamtbreite: bemaßter Plan 16,51⁵ m, Aufteilungsplan (M 1:100) 16,527 m an der Unterkante; Differenz 1,2 cm in der rechten Außenwand (PDF 0,57–0,59 m). Geometrie nach Aufteilungsplan, Kette nach bemaßtem Plan beschriftet.'},
        {'pos': [20.85, 11.405], 'short': '', 'text': 'Kontrollmaß rechte Seite: bemaßt 11,39⁵ m, Aufteilungsplan 11,405 m (Δ +1,0 cm). Gebäudetiefe links: WE05 9,84 m, Aufteilungsplan 9,83 m.'},
        {'pos': [12.29, 7.55], 'short': '', 'text': 'WE6 – WC: im Aufteilungsplan 2014 „WC 6“ mit Vorraum zum Bad (2,63 m² berechnet); der bemaßte Plan zeigt hier „Flur 2“ mit 2,92 m² (anderer Zustand, Wand WC/Vorraum ohne Abschluss). Keine Planfläche übernommen.'},
        {'pos': [14.84, 6.65], 'short': '', 'text': 'WE6 – Kochen: berechnet 8,57 m², bemaßter Plan 9,12 m² (Zustand vor dem 2014 geplanten Wandschluss an der alten Küchentür, rot schraffiert). Keine Planfläche übernommen.'},
        {'pos': [14.4, 5.65], 'short': '', 'text': 'Wand Kochen/Wohnen WE6 (2,17 m) im Aufteilungsplan 2014 gelb = Abbruch; als offen gezeichnet, Raumgrenze bei y = 5,51/5,78 m nach Wand. Ausführung nicht belegt.'},
        {'pos': [13.25, 9.30], 'short': '', 'text': 'Bad WE6: Türöffnung zum Vorraum im Aufteilungsplan gelb/gestrichelt (geplant); Türblatt nicht gezeichnet, Raumgrenze an der Wandflucht.'},
        {'pos': [10.0, 3.3], 'short': '', 'text': ZIEL_UNV},
        {'pos': [12.71, 2.3], 'short': '', 'text': TRAGEND_UNV},
        {'pos': [3.45, 3.0], 'short': '', 'text': 'WE05 Wand Wohnen/Schlafen: laut Eigentümer wahrscheinlich tragend, als load-bearing gezeichnet; nicht belegt (steht in allen Geschossen übereinander).'},
        {'pos': [5.1, 4.31], 'short': '', 'text': 'WE05 Flurwände (Schlafen/Flur, Küche/Flur und deren Flucht Essen/Wohnen): laut Eigentümer wahrscheinlich tragend, als load-bearing gezeichnet; nicht belegt.'},
    ],
)

# ------------------------------------------------------------------ OG1
CFG['OG1'] = dict(
    floor_name='1. Obergeschoss – gesamte Etage (WE3, WE4, Treppenhaus)',
    margin=3.4,
    source={
        'file': SRC_AP,
        'date': '2014-08-01',
        'version': 'Aufteilungsplan 2014, Ausschnitt 1. OG (Zielzustand 2014)',
        'transformation': trafo('1. OG', 241.2, 491.88),
        'reference': [SRC_BEM + ' (2. OG, Achsen übereinander)'],
    },
    rooms=[
        dict(name='WE3 – Essen', pos=[1.64, 7.40]),
        dict(name='WE3 – Kochen', pos=[4.34, 8.10]),
        dict(name='WE3 – Bad', pos=[6.50, 7.40]),
        dict(name='WE3 – Flur', pos=[4.69, 4.95]),
        dict(name='WE3 – Wohnen', pos=[1.87, 2.30]),
        dict(name='WE3 – Schlafen', pos=[5.15, 2.30]),
        dict(name='WE4 – Kind', pos=[9.77, 7.40]),
        dict(name='WE4 – WC', pos=[12.29, 7.85], label=[12.29, 8.45], name_size=1.6),
        dict(name='WE4 – Bad', pos=[13.38, 9.95], label=[14.4, 10.15]),
        dict(name='WE4 – Kochen', pos=[14.84, 7.00]),
        dict(name='WE4 – Flur', pos=[11.34, 4.90]),
        dict(name='WE4 – Schlafen', pos=[10.98, 2.30]),
        dict(name='WE4 – Wohnen/Essen', pos=[14.42, 2.30]),
        dict(name='Treppenhaus', pos=[8.08, 2.60], label=[8.08, 1.0], show_area=False, name_size=2.0),
    ],
    balconies=[dict(name='WE3 – Balkon', label=[1.63, 11.2]), dict(name='WE4 – Balkon', label=[17.54, 4.40])],
    stairs=[(6.70, 0.58, 9.45, 5.42)],
    north=(17.2, 0.0, 19.4, 2.6),
    notes=[
        {'pos': [7.49, 4.88], 'text': 'WE 3', 'size': 1.6},
        {'pos': [8.71, 4.88], 'text': 'WE 4', 'size': 1.6},
        {'pos': [8.15, 4.35], 'text': '+2,75', 'size': 1.5},
        {'pos': [-0.25, 5.2], 'text': 'Nachbarhaus Nr. 23', 'size': 2.0, 'anchor': 'end'},
        {'pos': [14.3, 12.3], 'text': 'Nachbarhaus Nr. 45', 'size': 2.0},
    ],
    barriers=[[[0.5, 5.57], [3.0, 5.57]], [[0.5, 5.80], [3.0, 5.80]], [[3.40, 5.82], [3.40, 8.6]], [[3.52, 5.82], [3.52, 8.6]], [[13.2, 5.535], [15.6, 5.535]], [[13.2, 5.765], [15.6, 5.765]], [[12.70, 9.20], [14.05, 9.20]]],
    auto_chains=STD_CHAINS,
    unverified=[
        {'pos': [10.0, 3.3], 'short': '', 'text': ZIEL_UNV},
        {'pos': [12.71, 2.3], 'short': '', 'text': TRAGEND_UNV},
        {'pos': [1.7, 5.68], 'short': '', 'text': 'WE3: Wände Essen/Wohnen (2,25 m) und Essen/Kochen im Aufteilungsplan 2014 gelb = Abbruch; offen gezeichnet, Raumgrenzen in der Wandflucht. Ausführung nicht belegt.'},
        {'pos': [14.4, 5.65], 'short': '', 'text': 'WE4: Wand Kochen/Wohnen (2,17 m) gelb = Abbruch 2014; offen gezeichnet, Raumgrenze in der Wandflucht. Bad-Türöffnung zum Vorraum gelb/gestrichelt, ohne Türblatt.'},
        {'pos': [1.63, 10.6], 'short': '', 'text': 'Balkone WE3/WE4: Fläche aus der Geometrie (3,00 x 2,50 m); Mietflächenanteil (½ wie bei WE05/WE06) nicht belegt.'},
        {'pos': [12.29, 7.55], 'short': '', 'text': 'WE4 – WC einschließlich Vorraum zum Bad (Grenze WC/Vorraum im Plan offen).'},
        {'pos': [8.08, 1.6], 'short': '', 'text': 'Kein bemaßter Plan für das 1. OG: alle Maße aus dem Aufteilungsplan (M 1:100) abgegriffen, Flächen berechnet (keine Planflächen vorhanden).'},
    ],
)

# ------------------------------------------------------------------ EG
CFG['EG'] = dict(
    floor_name='Erdgeschoss – gesamte Etage (WE1, WE2, Treppenhaus mit Hauseingang)',
    margin=3.4,
    source={
        'file': SRC_AP,
        'date': '2014-08-01',
        'version': 'Aufteilungsplan 2014, Ausschnitt Erdgeschoss mit Außenanlagen (nur Gebäude übernommen, Zielzustand 2014)',
        'transformation': trafo('Erdgeschoss', 271.8, 1318.56),
        'reference': [SRC_BEM + ' (2. OG, Achsen übereinander)'],
    },
    rooms=[
        dict(name='WE1 – Essen', pos=[1.79, 7.40]),
        dict(name='WE1 – Kochen', pos=[4.38, 8.10]),
        dict(name='WE1 – Bad', pos=[6.50, 7.40]),
        dict(name='WE1 – Flur', pos=[4.69, 4.95]),
        dict(name='WE1 – Wohnen', pos=[1.92, 2.30]),
        dict(name='WE1 – Schlafen', pos=[5.11, 2.30]),
        dict(name='WE2 – Kind', pos=[9.63, 7.40]),
        dict(name='WE2 – WC', pos=[12.29, 8.40], label=[12.29, 8.45], name_size=1.6),
        dict(name='WE2 – Bad', pos=[13.38, 9.95], label=[14.4, 10.15]),
        dict(name='WE2 – Kochen', pos=[14.67, 7.00]),
        dict(name='WE2 – Flur', pos=[11.34, 4.90]),
        dict(name='WE2 – Schlafen', pos=[11.11, 2.30]),
        dict(name='WE2 – Wohnen/Essen', pos=[14.38, 2.30]),
        dict(name='Treppenhaus', pos=[8.08, 2.60], label=[8.08, 3.2], show_area=False, name_size=2.0),
    ],
    balconies=[dict(name='WE1 – Balkon', label=[1.63, 11.2]), dict(name='WE2 – Balkon', label=[17.54, 4.40])],
    stairs=[(6.70, 0.58, 9.45, 5.42)],
    umgebung_boxes=[(-1.3, -0.2, 0.0, 12.6), (12.0, 9.8, 16.6, 12.6)],
    notes=[
        {'pos': [7.49, 4.88], 'text': 'WE 1', 'size': 1.6},
        {'pos': [8.71, 4.88], 'text': 'WE 2', 'size': 1.6},
        {'pos': [8.18, 4.20], 'text': '± 0,00', 'size': 1.5},
        {'pos': [7.77, 1.50], 'text': '−1,02', 'size': 1.5},
        {'pos': [8.08, -2.15], 'text': 'Eingang Haus 25 (−1,00)', 'size': 1.8},
        {'pos': [-0.25, 5.2], 'text': 'Nachbarhaus Nr. 23', 'size': 2.0, 'anchor': 'end'},
        {'pos': [14.3, 12.3], 'text': 'Nachbarhaus Nr. 45', 'size': 2.0},
    ],
    barriers=[[[0.5, 5.57], [3.0, 5.57]], [[0.5, 5.80], [3.0, 5.80]], [[3.40, 5.82], [3.40, 8.6]], [[3.52, 5.82], [3.52, 8.6]],
              [[13.2, 5.535], [15.6, 5.535]], [[13.2, 5.765], [15.6, 5.765]], [[12.70, 9.20], [14.05, 9.20]]],
    auto_chains=STD_CHAINS,
    unverified=[
        {'pos': [10.0, 3.3], 'short': '', 'text': ZIEL_UNV},
        {'pos': [12.71, 2.3], 'short': '', 'text': TRAGEND_UNV},
        {'pos': [8.08, 1.6], 'short': '', 'text': 'Kein bemaßter Plan für das Erdgeschoss: alle Maße aus dem Aufteilungsplan (M 1:100) abgegriffen, Flächen berechnet. Außenanlagen (Stellplätze, Zaun, Müll, Flurstücksgrenzen) nicht übernommen.'},
        {'pos': [1.63, 10.6], 'short': '', 'text': 'Balkone WE1/WE2 (EG, mit Außentreppe): Fläche aus der Geometrie; Mietflächenanteil nicht belegt.'},
    ],
)

# ------------------------------------------------------------------ KG
CFG['KG'] = dict(
    floor_name='Kellergeschoss (Kellerabteile K1–K8, Flure, Fahrradraum)',
    margin=3.4,
    source={
        'file': SRC_AP,
        'date': '2014-08-01',
        'version': 'Aufteilungsplan 2014, Ausschnitt Kellergeschoss',
        'transformation': trafo('Kellergeschoss', 1521.06, 1318.56,
            ' x-Ursprung über die Treppenhausachse an OG2 angeglichen (Mitte der Treppenhauswände).'),
        'reference': [],
    },
    rooms=[
        dict(name='Keller K8', pos=[2.13, 7.40]),
        dict(name='Keller K1', pos=[5.80, 7.40]),
        dict(name='Keller K2', pos=[1.78, 2.20]),
        dict(name='Keller K3', pos=[4.82, 2.20]),
        dict(name='Keller K4', pos=[11.24, 2.00]),
        dict(name='Keller K5', pos=[14.00, 2.00]),
        dict(name='Keller K6', pos=[14.31, 6.90]),
        dict(name='Keller K7', pos=[14.12, 9.70]),
        dict(name='Flur 1', pos=[4.27, 4.91]),
        dict(name='Flur 2', pos=[8.05, 7.16]),
        dict(name='Fahrräder/Kinderwägen', pos=[9.95, 7.37], name_size=1.7),
        dict(name='Flur 3', pos=[12.08, 5.04]),
        dict(name='Treppenhaus', pos=[7.4, 1.5], label=[8.05, 1.0], show_area=False, name_size=2.0),
    ],
    fp_boxes=[(-1, -1, 12.1, 9.9), (12.1, -1, 17.5, 11.6)],
    barriers=[[[3.9, 4.15], [5.7, 4.15]], [[7.2, 5.80], [8.95, 5.80]], [[12.757, 4.20], [12.757, 5.78]], [[12.9, 8.187], [16.0, 8.187]]],
    skip_doors=[[0.392, 5.482]],
    extra_walls=[{'id': 'K6-K7-trennung', 'a': [12.79, 8.187], 'b': [15.96, 8.187], 'thickness': 0.04, 'align': 'center', 'type': 'interior'}],
    extra_doors=[dict(a=[0.392, 5.482], b=[1.166, 5.482], side='right', name='Tür Keller K8')],
    stairs=[(6.9, 0.4, 9.3, 5.4)],
    north=(18.6, -0.6, 20.5, 2.6),
    notes=[
        {'pos': [8.04, 4.70], 'text': '−2,50', 'size': 1.5},
        {'pos': [-0.25, 5.2], 'text': 'Nachbarhaus Nr. 23', 'size': 2.0, 'anchor': 'end'},
    ],
    auto_chains=STD_CHAINS,
    unverified=[
        {'pos': [12.71, 2.3], 'short': '', 'text': TRAGEND_UNV},
        {'pos': [8.05, 1.6], 'short': '', 'text': 'Kein bemaßter Plan für das Kellergeschoss: Maße aus dem Aufteilungsplan (M 1:100), Flächen berechnet. Die Außenwände des KG liegen im Plan 5–10 cm innerhalb der Obergeschoss-Fassaden (Zeichenungenauigkeit oder dickere Kellerwände); unverändert übernommen.'},
        {'pos': [2.13, 6.9], 'short': '', 'text': 'Zuordnung der Kellerabteile K1–K8 zu den Wohnungen ist im Aufteilungsplan nicht angegeben.'},
        {'pos': [14.4, 8.187], 'short': '', 'text': 'Trennung Keller K6/K7 im Plan nur als Linie (Lattenverschlag o. ä.), hier als 4-cm-Wand gezeichnet; Art und Stärke unbekannt.'},
        {'pos': [0.75, 5.0], 'short': '', 'text': 'Vorraum vor Keller K8 ohne Bezeichnung, Flur 1 zugeschlagen. Kellerzugang außen (−1,70, Außentreppe) nur als Umriss.'},
        {'pos': [4.8, 4.15], 'short': '', 'text': 'Keller K3: Tür im Plan gestrichelt, Öffnung ohne Türblatt; Raumgrenze in der Wandflucht.'},
        {'pos': [14.3, 5.0], 'short': '', 'text': 'Keller K5: Zugang über die Tür an der Flucht x = 12,76 m; Öffnung (1,18 m) breiter als das Türblatt (0,90 m).'},
    ],
)

# ------------------------------------------------------------------ DG
KN = 0.051  # Kniestock-/Abseitenwand: Doppellinie im Plan, 5 cm
CFG['DG'] = dict(
    floor_name='Dachgeschoss – Wohnung WE7 (Ausbau laut Aufteilungsplan 2014)',
    margin=3.4,
    source={
        'file': SRC_AP,
        'date': '2014-08-01',
        'version': 'Aufteilungsplan 2014, Ausschnitt Dachgeschoss (DG-Ausbau, Zielzustand 2014)',
        'transformation': trafo('Dachgeschoss', 2104.44, 495.0,
            ' Ursprung an der Außenkante der Giebelwand (Brandwand Haus Nr. 23) und an der Traufkante unten. '
            'Kniestock-/Abseitenwände sind im Plan nur als Doppellinie (5 cm) gezeichnet und hier als 0,051 m starke Wände übernommen.'),
        'reference': [],
    },
    footprint_add=[[(0, -0.15), (16.83, -0.15), (16.83, 11.53), (0, 11.53)]],
    no_windows=True,
    type_override=[
        {'area': [(-0.5, -1), (0.4, -1), (0.4, 10.5), (-0.5, 10.5)], 'type': 'exterior'},
        {'area': [(12.0, 11.0), (17.5, 11.0), (17.5, 12.0), (12.0, 12.0)], 'type': 'exterior'},
        {'area': [(6.7, -1), (9.7, -1), (9.7, 4.47), (6.7, 4.47)], 'type': 'load-bearing'},
    ],
    extra_walls=[
        {'id': 'kniestock-unten-links', 'a': [0.199, 1.3165], 'b': [6.816, 1.3165], 'thickness': KN, 'align': 'center', 'type': 'interior'},
        {'id': 'kniestock-unten-rechts', 'a': [9.584, 1.3165], 'b': [15.778, 1.3165], 'thickness': KN, 'align': 'center', 'type': 'interior'},
        {'id': 'kniestock-rechts', 'a': [15.7525, 1.291], 'b': [15.7525, 8.543], 'thickness': KN, 'align': 'center', 'type': 'interior'},
        {'id': 'kniestock-oben', 'a': [3.107, 8.5175], 'b': [15.778, 8.5175], 'thickness': KN, 'align': 'center', 'type': 'interior'},
    ],
    rooms=[
        dict(name='WE7 – Wohnen/Essen/Kochen', pos=[2.74, 5.0], label=[3.3, 4.6]),
        dict(name='WE7 – Bad', pos=[8.12, 7.38]),
        dict(name='WE7 – Abst', pos=[11.2, 7.38], name_size=1.8),
        dict(name='WE7 – Diele', pos=[10.67, 5.8]),
        dict(name='WE7 – Zimmer', pos=[13.79, 7.0]),
        dict(name='WE7 – Schlafen', pos=[10.94, 3.0]),
        dict(name='Treppenhaus', pos=[7.6, 2.0], label=[8.2, 0.95], show_area=False, name_size=1.8),
    ],
    balconies=[dict(name='WE7 – Balkon', label=[1.86, 11.2])],
    barriers=[[[6.816, 5.2], [6.816, 6.42]], [[0.85, 9.62], [2.90, 9.62]], [[-0.1, 9.83], [3.4, 9.83]], [[9.44, 3.9], [9.44, 4.6]]],
    stairs=[(6.80, 0.0, 9.60, 5.30)],
    north=(17.2, -0.3, 19.2, 2.6),
    roof_box=(-0.3, -0.25, 16.9, 11.6),
    fixture_rooms=('Bad', 'Abst'),
    notes=[
        {'pos': [7.55, 4.05], 'text': '+8,25', 'size': 1.5},
        {'pos': [8.80, 4.55], 'text': 'WE 7', 'size': 1.6},
        {'pos': [8.80, 4.20], 'text': '+8,32', 'size': 1.5},
        {'pos': [5.2, 3.6], 'text': 'mögliche Raumspartreppe zur Galerie', 'size': 1.4},
        {'pos': [-0.25, 5.2], 'text': 'Nachbarhaus Nr. 23', 'size': 2.0, 'anchor': 'end'},
    ],
    auto_chains=[
        dict(axis='x', at=3.0, base=-0.148, offset=-0.61),
        dict(axis='y', at=4.0, base=0.0, offset=1.0, lo=-1, hi=12, total=False),
    ],
    unverified=[
        {'pos': [3.3, 2.0], 'short': '', 'text': ZIEL_UNV + ' Für das DG bedeutet das: Ausbau (rote Wände) laut Plan 2014; ob und wie ausgeführt, ist nicht belegt.'},
        {'pos': [8.2, 1.6], 'short': '', 'text': 'Treppenhauswände im DG-Ausschnitt ca. 0,08–0,10 m gegenüber den Obergeschossen nach rechts versetzt und 0,28 m stark (Zeichenungenauigkeit oder Bestand); unverändert übernommen. Als tragend gezeichnet (stehen in allen Geschossen übereinander).'},
        {'pos': [12.0, 1.0], 'short': '', 'text': 'Raumgrenzen an den Kniestock-/Abseitenwänden (Doppellinie 5 cm). Gepunktete Höhenlinien der Dachschräge, Dachflächenfenster und Kamine (gelb, Abbruch) nicht übernommen. Flächen = Grundfläche ohne Abzug nach WoFlV (Dachschräge).'},
        {'pos': [6.82, 5.8], 'short': '', 'text': 'Grenze Wohnen/Essen/Kochen zu Diele in der Flucht der Treppenhauswand angenommen; die Tür dort ist im Plan gestrichelt (geplant).'},
        {'pos': [15.75, 4.6], 'short': '', 'text': 'Rechte Abseitenwand im Bereich y 4,15–5,35 m im Plan gelb (Abbruch/Durchbruch?); als durchgehende Wand gezeichnet.'},
        {'pos': [1.86, 10.6], 'short': '', 'text': 'Balkon WE7: Fläche aus der Geometrie; Mietflächenanteil nicht belegt.'},
        {'pos': [9.44, 4.2], 'short': '', 'text': 'Treppenhauswand rechts bei y 4,04–4,40 m im Plan gelb (Abbruch) – Lücke zwischen Treppenhaus und Schlafen; Raumgrenze in der Wandflucht angenommen, Zweck unklar.'},
    ],
)
