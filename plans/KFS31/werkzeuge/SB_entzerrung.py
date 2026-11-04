"""Entzerrung Spitzboden 1999 S. 12/13 und Overlay der Neuzeichnung (Stand 04.11.2026).

Vorbereitung:  pdftoppm -r 200 -f 12 -l 13 -png quelle/19990111-Grundrisse-Karl_Ferlemann_Str_31.pdf $WORK/p
Aufruf:        python3 SB_entzerrung.py            -> $WORK/mos.png (50 px/m, x -1…29, y -7,5…15,5)
               python3 SB_entzerrung.py overlay geometrie/SB.json out.png
WORK = /tmp/kfs31sb (anpassen).

S. 12: Linien je Höhe mit eigener Steigung (Blattverzug), Steigung linear über v interpoliert, Scherung der
Senkrechten 0,012; Bezug x über die Maßkettenticks 0 (u = 355,5) und 12,86, Bezug y über die Lage der
Maßkette 14,05/26,91 (y = −5,16 bzw. −6,89), die auf S. 13 aus der Maßkette 14,05 bestimmt wurde.
"""
import sys, json
import numpy as np
from PIL import Image, ImageDraw

WORK = '/tmp/kfs31sb'
V = np.array([1618.6, 1712, 1366.5, 1129.1, 977.6, 896.6, 588.5])           # Linien bei u = 355 (S. 12)
Mm = np.array([-0.0278, -0.0275, -0.0253, -0.0220, -0.0229, -0.0228, -0.0206])  # gemessene Steigungen
PM = np.polyfit(V, Mm, 1)
S = 53.55
# S. 13: Achsrichtungen aus Waagerechten (−0,0381) und Maßkette 14,05 (dx/dy 0,0441)
EX = 53.6 * np.array([1, -0.0381]) / np.hypot(1, 0.0381)
EY = (751.6 / 14.05) * np.array([-0.0441, -1]) / np.hypot(1, 0.0441)
O13 = np.array([480.6, 1376.3]) - (26.91 + 4.4593) * EX


def plan2px12(X, Y):
    v355 = 1618.6 - S * (Y + 5.16); m = np.polyval(PM, v355)
    u = 355.5 + 53.6 * X
    for _ in range(3):
        v = v355 + m * (u - 355.5)
        u = 355.5 + 53.6 * X + 0.012 * (v - 1618.8)
    return u, v


def samp(im, PX, PY):
    H, W = im.shape; ok = (PX >= 0) & (PX < W - 1) & (PY >= 0) & (PY < H - 1)
    x0 = np.clip(np.floor(PX).astype(int), 0, W - 2); y0 = np.clip(np.floor(PY).astype(int), 0, H - 2)
    fx = PX - x0; fy = PY - y0
    out = im[y0, x0]*(1-fx)*(1-fy) + im[y0, x0+1]*fx*(1-fy) + im[y0+1, x0]*(1-fx)*fy + im[y0+1, x0+1]*fx*fy
    return np.where(ok, out, 255.0), ok


R, X0, Y0, X1, Y1 = 50.0, -1.0, -7.5, 29.0, 15.5


def mosaic():
    w = int((X1 - X0) * R); h = int((Y1 - Y0) * R)
    uu, vv = np.meshgrid(np.arange(w), np.arange(h)); X = X0 + uu / R; Y = Y1 - vv / R
    a12 = np.array(Image.open(f'{WORK}/p-12.png').convert('L')).astype(float)
    a13 = np.array(Image.open(f'{WORK}/p-13.png').convert('L')).astype(float)
    P12 = plan2px12(X, Y); o12, ok12 = samp(a12, *P12); ok12 &= P12[0] < 1600   # Blattrand S. 12
    U13 = O13[0] + X * EX[0] + Y * EY[0]; V13 = O13[1] + X * EX[1] + Y * EY[1]
    o13, ok13 = samp(a13, U13, V13); ok13 &= U13 > 25
    Image.fromarray(np.where(ok12, o12, np.where(ok13, o13, 255)).astype(np.uint8)).save(f'{WORK}/mos.png')


def overlay(pj, out):
    sys.path.insert(0, '/home/user/hello-world/tools')
    from render_plan import build
    im = Image.open(f'{WORK}/mos.png').convert('RGB')
    plan = json.load(open(pj)); geo = build(plan)
    ov = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    P = lambda p: (-X0 * R + p[0] * R, Y1 * R - p[1] * R)
    for _, poly in geo['walls']:
        d.polygon([P(q) for q in poly], fill=(255, 0, 0, 90), outline=(220, 0, 0, 255))
    for r in plan['rooms']:
        d.polygon([P(q) for q in r['polygon']], outline=(0, 0, 255, 255))
    for sy in plan.get('symbols', []):
        for a, b in sy.get('lines', []):
            d.line([P(a), P(b)], fill=(0, 170, 0, 255))
        for pg in sy.get('polygons', []):
            d.polygon([P(q) for q in pg['points']], outline=(0, 170, 0, 255))
    Image.alpha_composite(im.convert('RGBA'), ov).convert('RGB').save(out)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'overlay':
        overlay(sys.argv[2], sys.argv[3])
    else:
        mosaic()
