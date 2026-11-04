import sys, json
import sys; sys.dont_write_bytecode = True
sys.path.insert(0, '/home/user/hello-world/tools')
from render_plan import build
from PIL import Image, ImageDraw
# overlay.py KEY plan.json out [X0 Y0 X1 Y1 sc]
CAL = json.load(open('/tmp/kfs31/cal.json'))
key, pj, out = sys.argv[1:4]
X0, Y0, X1, Y1, sc = (list(map(float, sys.argv[4:9])) + [None]*5)[:5] if len(sys.argv) > 4 else (-0.5, -0.5, 27.5, 14.6, 0.6)
c = CAL[key]; ox, oy, s = c['ox'], c['oy'], c['s']; sy = c.get('sy', s)
im = Image.open(c['src']).convert('RGB')
plan = json.load(open(pj)); geo = build(plan)
ov = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
P = lambda p: (ox + p[0]*s, oy - p[1]*sy)
for lay, poly in geo['walls']:
    d.polygon([P(q) for q in poly], fill=(255, 0, 0, 90), outline=(220, 0, 0, 255))
for lay, (a, b) in geo['lines']:
    d.line([P(a), P(b)], fill=(0, 160, 0, 255), width=2)
for r in plan['rooms']:
    d.polygon([P(q) for q in r['polygon']], outline=(0, 0, 255, 200))
im = Image.alpha_composite(im.convert('RGBA'), ov).convert('RGB')
box = (int(ox + X0*s), int(oy - Y1*sy), int(ox + X1*s), int(oy - Y0*sy))
im = im.crop(box); im = im.resize((int(im.width*sc), int(im.height*sc)), Image.LANCZOS)
im.save(out); print(im.size)
