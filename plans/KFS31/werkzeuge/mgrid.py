import sys, json
from PIL import Image, ImageDraw, ImageFont
# mgrid.py KEY out X0 Y0 X1 Y1 step sc   (Gebäudekoordinaten in m)
CAL=json.load(open('/tmp/kfs31/cal.json'))
key,out=sys.argv[1],sys.argv[2]
X0,Y0,X1,Y1,step,sc=map(float,sys.argv[3:9])
c=CAL[key]; src=c['src']; ox,oy,s=c['ox'],c['oy'],c['s']; sy=c.get('sy',s)
px=lambda X: ox+X*s; py=lambda Y: oy-Y*sy
im=Image.open(src).convert('RGB')
box=(int(px(X0)),int(py(Y1)),int(px(X1)),int(py(Y0)))
im=im.crop(box); im=im.resize((int(im.width*sc),int(im.height*sc)),Image.LANCZOS)
d=ImageDraw.Draw(im); f=ImageFont.load_default()
import math
k=math.ceil(X0/step)
while k*step<=X1:
    X=k*step; u=(px(X)-box[0])*sc
    major=abs(X-round(X))<1e-6
    d.line([(u,0),(u,im.height)],fill=(255,0,0) if major else (255,180,180),width=1)
    if major: d.text((u+2,2),f"{X:.0f}",fill=(200,0,0),font=f); d.text((u+2,im.height-12),f"{X:.0f}",fill=(200,0,0),font=f)
    elif abs(X*2-round(X*2))<1e-6: d.line([(u,0),(u,im.height)],fill=(255,120,120),width=1)
    k+=1
k=math.ceil(Y0/step)
while k*step<=Y1:
    Y=k*step; v=(py(Y)-box[1])*sc
    major=abs(Y-round(Y))<1e-6
    d.line([(0,v),(im.width,v)],fill=(0,0,255) if major else (180,180,255),width=1)
    if major: d.text((2,v+2),f"{Y:.0f}",fill=(0,0,200),font=f); d.text((im.width-20,v+2),f"{Y:.0f}",fill=(0,0,200),font=f)
    elif abs(Y*2-round(Y*2))<1e-6: d.line([(0,v),(im.width,v)],fill=(120,120,255),width=1)
    k+=1
im.save(out); print(im.size)
