#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Abstrahierter Grundriss 1.OG als HA-Dashboard-Hintergrund (SVG). v3"""
import math

S = 59.0
OX, OY = 277.0, 55.0
def X(x): return OX + x * S
def Y(y): return OY + y * S
def W(m): return m * S

GREY = "#8f8f8f"

svg = []
svg.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 800" '
           'font-family="system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif">')
svg.append(f'<g fill="{GREY}" stroke="none">')

# ---------- Umgebung ----------
env = []
env.append(f'<rect x="40" y="30" width="66" height="740" fill="{GREY}" fill-opacity="0.06" rx="2"/>')
env.append(f'<line x1="73" y1="45" x2="73" y2="755" stroke="{GREY}" stroke-opacity="0.22" stroke-width="2" stroke-dasharray="14 12"/>')
env.append(f'<text x="73" y="400" transform="rotate(-90 73 400)" text-anchor="middle" font-size="13" fill="{GREY}" fill-opacity="0.75" letter-spacing="2">STRASSE</text>')
# Vorgarten mittig vor dem Balkon zur Strasse
vgx, vgy = 157, (Y(7.76)+Y(11.675))/2
env.append(f'<text x="{vgx}" y="{vgy:.0f}" transform="rotate(-90 {vgx} {vgy:.0f})" text-anchor="middle" font-size="11" fill="{GREY}" fill-opacity="0.5" letter-spacing="2">VORGARTEN</text>')
gx = X(13.58) + 18
env.append(f'<rect x="{gx:.0f}" y="30" width="{1280-40-gx:.0f}" height="740" fill="{GREY}" fill-opacity="0.05" rx="2"/>')
env.append(f'<text x="{gx+95:.0f}" y="400" transform="rotate(-90 {gx+95:.0f} 400)" text-anchor="middle" font-size="13" fill="{GREY}" fill-opacity="0.75" letter-spacing="2">GARTEN</text>')

# ---------- Raumflaechen ----------
fills = []
def frect(x0, y0, x1, y1):
    fills.append(f'<rect x="{X(x0):.1f}" y="{Y(y0):.1f}" width="{W(x1-x0):.1f}" height="{W(y1-y0):.1f}" fill="{GREY}" fill-opacity="0.045"/>')
frect(0.365, 0.365, 2.845, 4.845)      # Treppenhaus
frect(2.96, 0.365, 4.38, 3.76)        # Garderobe (offen zum Flur)
frect(4.495, 1.905, 5.615, 3.645)     # Toilette (tiefer, nach Norden verlaengert)
# Bad inkl. Dusche als L-Polygon (Rechteck minus WC)
fills.append(f'<path d="M {X(4.495):.1f} {Y(0.365):.1f} H {X(8.195):.1f} V {Y(3.645):.1f} H {X(5.73):.1f} '
             f'V {Y(1.905):.1f} H {X(4.495):.1f} Z" fill="{GREY}" fill-opacity="0.045"/>')
frect(8.31, 0.365, 11.595, 5.285)     # Schlafzimmer
frect(2.96, 3.76, 8.195, 4.845)       # Flur Korridor
frect(5.965, 4.845, 8.195, 7.645)     # Flur Stich
frect(0.365, 4.96, 5.85, 7.645)       # Kueche (offen)
frect(1.365, 7.645, 5.965, 7.76)      # offener Uebergang Kueche/Essbereich
frect(8.31, 5.40, 11.595, 7.645)      # Buero
frect(1.365, 7.76, 7.025, 11.31)      # Wohnen (Essbereich+Couch)
frect(7.14, 7.76, 11.595, 11.31)      # Kinderzimmer

# ---------- Balkone ----------
balc = []
balc.append(f'<rect x="{X(-1.17):.1f}" y="{Y(7.76):.1f}" width="{W(2.17):.1f}" height="{W(3.915):.1f}" fill="{GREY}" fill-opacity="0.10"/>')
balc.append(f'<path d="M {X(0):.1f} {Y(7.76):.1f} L {X(-1.17):.1f} {Y(7.76):.1f} L {X(-1.17):.1f} {Y(11.675):.1f} L {X(1.0):.1f} {Y(11.675):.1f}" '
            f'fill="none" stroke="{GREY}" stroke-width="2.5" stroke-opacity="0.8"/>')
balc.append(f'<rect x="{X(11.96):.1f}" y="{Y(5.5):.1f}" width="{W(1.52):.1f}" height="{W(11.675-5.5):.1f}" fill="{GREY}" fill-opacity="0.10"/>')
balc.append(f'<path d="M {X(11.96):.1f} {Y(5.5):.1f} H {X(13.48):.1f} V {Y(11.675):.1f} H {X(11.96):.1f}" '
            f'fill="none" stroke="{GREY}" stroke-width="2.5" stroke-opacity="0.8"/>')

# ---------- Waende (Gruppen-Opacity -> keine dunklen Ueberlagerungen) ----------
def seg_h(y0, y1, x0, x1, gaps):
    out, cur = [], x0
    for g0, g1 in sorted(gaps):
        if g0 > cur: out.append((cur, g0))
        cur = max(cur, g1)
    if cur < x1: out.append((cur, x1))
    return [f'<rect x="{X(a):.1f}" y="{Y(y0):.1f}" width="{W(b-a):.1f}" height="{W(y1-y0):.1f}"/>' for a, b in out]

def seg_v(x0, x1, y0, y1, gaps):
    out, cur = [], y0
    for g0, g1 in sorted(gaps):
        if g0 > cur: out.append((cur, g0))
        cur = max(cur, g1)
    if cur < y1: out.append((cur, y1))
    return [f'<rect x="{X(x0):.1f}" y="{Y(a):.1f}" width="{W(x1-x0):.1f}" height="{W(b-a):.1f}"/>' for a, b in out]

ext = []
ext += seg_h(0, 0.365, 0, 11.96, [(3.28, 4.18), (6.48, 7.68)])                       # Nord
ext += seg_h(11.31, 11.675, 1.00, 11.96, [(3.96, 5.76), (8.47, 10.27)])              # Sued
ext += seg_v(0, 0.365, 0, 7.76, [(3.80, 4.80), (5.66, 6.86)])                        # West (Kuechenfenster 70cm unter Nordwand)
ext += seg_v(11.595, 11.96, 0, 11.675, [(1.675, 3.475), (6.0, 7.2), (8.4, 10.2)])    # Ost
ext += seg_h(7.645, 7.76, 0, 1.365, [])                                              # Kueche-Sued gegen Loggia

itn = []
itn += seg_v(2.845, 2.96, 0.365, 4.845, [(3.85, 4.75)])                 # TRH-Ost, Wohnungstuer
itn += seg_v(4.38, 4.495, 0.365, 3.645, [])                            # Garderobe/WC
itn += seg_v(5.615, 5.73, 1.705, 3.645, [])                           # WC-Ost inkl. Eckabschluss
itn += seg_h(1.79, 1.905, 4.495, 5.615, [])                           # WC-Nord (zur Dusche)
itn += seg_v(8.195, 8.31, 0.365, 7.645, [(3.80, 4.685), (6.08, 6.965)])  # Schlaf-/Buerotueren
itn += seg_v(5.85, 5.965, 4.96, 7.76, [])                              # Kueche-Ost, bis zur Couch-Tuer
itn += seg_h(3.645, 3.76, 4.38, 8.195, [(4.6, 5.36), (6.7, 7.59)])     # WC-/Bad-Sued
itn += seg_h(4.845, 4.96, 0.365, 5.965, [(4.365, 5.25)])               # Kueche Nord, Tuer
itn += seg_h(5.285, 5.40, 8.31, 11.595, [])                            # Schlaf Sued (nach S verschoben)
itn += seg_h(7.645, 7.76, 7.14, 11.595, [(7.31, 8.195)])               # Kind Nord, Tuer
itn += seg_v(7.025, 7.14, 7.645, 11.31, [])                            # Wohnen/Kind
itn += seg_h(7.645, 7.76, 6.85, 7.14, [])                              # Ostzarge Couch-Tuer
itn += seg_v(1.00, 1.365, 7.76, 11.31, [(8.7, 10.5)])                  # Loggia-Tuer
itn.append(f'<rect x="{X(5.45):.1f}" y="{Y(4.96):.1f}" width="{W(0.40):.1f}" height="{W(0.70):.1f}"/>')  # Kamin

walls = [f'<g fill="{GREY}" opacity="0.85">'] + ext + ['</g>'] + [f'<g fill="{GREY}" opacity="0.45">'] + itn + ['</g>']

# Dusche: kleine gestrichelte Abtrennung
walls.append(f'<line x1="{X(5.6725):.1f}" y1="{Y(0.365):.1f}" x2="{X(5.6725):.1f}" y2="{Y(1.79):.1f}" '
             f'stroke="{GREY}" stroke-width="1.5" stroke-opacity="0.4" stroke-dasharray="4 4"/>')

# ---------- Fenster ----------
def win_h(y0, y1, x0, x1):
    ym = (Y(y0) + Y(y1)) / 2
    return (f'<line x1="{X(x0):.1f}" y1="{ym:.1f}" x2="{X(x1):.1f}" y2="{ym:.1f}" stroke="{GREY}" stroke-width="2" stroke-opacity="0.9"/>'
            f'<line x1="{X(x0):.1f}" y1="{Y(y0):.1f}" x2="{X(x0):.1f}" y2="{Y(y1):.1f}" stroke="{GREY}" stroke-width="1" stroke-opacity="0.6"/>'
            f'<line x1="{X(x1):.1f}" y1="{Y(y0):.1f}" x2="{X(x1):.1f}" y2="{Y(y1):.1f}" stroke="{GREY}" stroke-width="1" stroke-opacity="0.6"/>')

def win_v(x0, x1, y0, y1):
    xm = (X(x0) + X(x1)) / 2
    return (f'<line x1="{xm:.1f}" y1="{Y(y0):.1f}" x2="{xm:.1f}" y2="{Y(y1):.1f}" stroke="{GREY}" stroke-width="2" stroke-opacity="0.9"/>'
            f'<line x1="{X(x0):.1f}" y1="{Y(y0):.1f}" x2="{X(x1):.1f}" y2="{Y(y0):.1f}" stroke="{GREY}" stroke-width="1" stroke-opacity="0.6"/>'
            f'<line x1="{X(x0):.1f}" y1="{Y(y1):.1f}" x2="{X(x1):.1f}" y2="{Y(y1):.1f}" stroke="{GREY}" stroke-width="1" stroke-opacity="0.6"/>')

wins = [
    win_h(0, 0.365, 3.28, 4.18),
    win_h(0, 0.365, 6.48, 7.68),
    win_h(11.31, 11.675, 3.96, 5.76),
    win_h(11.31, 11.675, 8.47, 10.27),
    win_v(0, 0.365, 3.80, 4.80),
    win_v(0, 0.365, 5.66, 6.86),
    win_v(11.595, 11.96, 1.675, 3.475),
    win_v(11.595, 11.96, 6.0, 7.2),
]

# ---------- Tueren: einheitlich geschlossen gezeichnet ----------
def door(hx, hy, closed, opened, wd):
    r = W(wd); x0, y0 = X(hx), Y(hy)
    a0, a1 = math.radians(closed), math.radians(opened)
    xa, ya = x0 + r*math.cos(a0), y0 + r*math.sin(a0)   # Blatt geschlossen
    xb, yb = x0 + r*math.cos(a1), y0 + r*math.sin(a1)
    sweep = 1 if ((opened - closed) % 360) < 180 else 0
    return (f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{xa:.1f}" y2="{ya:.1f}" stroke="{GREY}" stroke-width="1.6" stroke-opacity="0.65"/>'
            f'<path d="M {xa:.1f} {ya:.1f} A {r:.1f} {r:.1f} 0 0 {sweep} {xb:.1f} {yb:.1f}" fill="none" stroke="{GREY}" stroke-width="1" stroke-opacity="0.4" stroke-dasharray="3 3"/>')

doors = [
    door(2.96, 4.75, -90, 0, 0.90),        # Wohnungstuer -> innen, gegen Suedwand
    door(4.6, 3.76, 0, 90, 0.76),          # Toilette -> oeffnet in den Flur
    door(6.7, 3.76, 0, 90, 0.885),         # Bad -> in Flur, Angel West
    door(8.31, 4.685, -90, 0, 0.885),      # Schlafzimmer -> in Raum (60cm Wand suedlich)
    door(8.31, 6.08, 90, 0, 0.885),        # Buero -> in Buero, mittig
    door(7.31, 7.76, 0, 90, 0.885),        # Kinderzimmer -> in Raum
    door(5.25, 4.96, 180, 90, 0.885),      # Kueche -> in Kueche
    door(6.85, 7.76, 180, 90, 0.885),      # Couch/Wohnen: Blatt schlaegt an Trennwand zum Kind
    door(11.595, 8.4, 90, 180, 0.90),      # Kind Balkon-Doppeltuer N
    door(11.595, 10.2, -90, 180, 0.90),    # Kind Balkon-Doppeltuer S
    door(1.365, 8.7, 90, 0, 0.90),         # Loggia N
    door(1.365, 10.5, -90, 0, 0.90),       # Loggia S
]

# ---------- Labels ----------
def label(x, y, text, size=13, op=0.8, anchor="start", rot=None):
    t = f'font-size="{size}" fill="{GREY}" fill-opacity="{op}" text-anchor="{anchor}"'
    if rot:
        return f'<text x="{X(x):.1f}" y="{Y(y):.1f}" {t} transform="rotate({rot} {X(x):.1f} {Y(y):.1f})">{text}</text>'
    return f'<text x="{X(x):.1f}" y="{Y(y):.1f}" {t}>{text}</text>'

labels = [
    label(0.55, 4.62, "Treppenhaus", size=12, op=0.5),
    label(3.08, 0.75, "Garderobe", size=11, rot=90, op=0.7),
    label(4.62, 3.45, "Toilette", size=11, op=0.7),
    label(5.99, 0.72, "Badezimmer"),
    label(8.55, 0.72, "Schlafzimmer"),
    label(6.1, 5.25, "Flur"),
    label(0.55, 5.42, "Küche"),
    label(8.55, 5.82, "Büro"),
    label(1.55, 8.20, "Essbereich"),
    label(4.75, 8.90, "Couch"),
    label(7.35, 9.10, "Kinderzimmer"),
    label(-0.85, 11.35, "Balkon zur Straße", size=11, rot=-90, op=0.75),
    label(13.40, 11.35, "Balkon zum Garten", size=11, rot=-90, op=0.75),
]

svg += env + fills + balc + walls + wins + doors + labels
svg.append('</g></svg>')
open('/home/claude/grundriss_dashboard.svg', 'w').write("\n".join(svg))
print("written")
