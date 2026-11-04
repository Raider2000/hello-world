import sys, json
import numpy as np
from PIL import Image
# lines.py KEY X0 Y0 X1 Y1 minlen_m  -> horizontale/vertikale Linien in m
CAL=json.load(open('/tmp/kfs31/cal.json'))
key=sys.argv[1]; X0,Y0,X1,Y1,minlen=map(float,sys.argv[2:7])
c=CAL[key]; ox,oy,s=c['ox'],c['oy'],c['s']; sy=c.get('sy',s)
im=np.array(Image.open(c['src']).convert('L'))
x0,x1=int(ox+X0*s),int(ox+X1*s); y0,y1=int(oy-Y1*sy),int(oy-Y0*sy)
A=im[y0:y1,x0:x1]<140
def runs(row):
    r=[];st=None
    for i,v in enumerate(np.append(row,False)):
        if v and st is None: st=i
        if not v and st is not None:
            r.append((st,i));st=None
    return r
def merge(segs,gap):
    # segs: list of (pos, a, b) ; merge same pos lines (pos within 2px)
    out=[]
    for p,a,b in sorted(segs):
        for o in out:
            if abs(o[0]-p)<=2.5 and a<=o[2]+gap and b>=o[1]-gap:
                o[0]=(o[0]*o[3]+p)/(o[3]+1);o[3]+=1;o[1]=min(o[1],a);o[2]=max(o[2],b);break
        else: out.append([p,a,b,1])
    return out
ml=minlen*s
H=[]
for j in range(A.shape[0]):
    for a,b in runs(A[j]):
        if b-a>=ml: H.append((j,a,b))
V=[]
for i in range(A.shape[1]):
    for a,b in runs(A[:,i]):
        if b-a>=ml: V.append((i,a,b))
Hm=merge(H,3); Vm=merge(V,3)
print("HORIZONTAL (y: x_von..x_bis)")
for p,a,b,n in sorted(Hm,key=lambda t:-t[0]):
    if n<2: continue
    Y=(oy-(y0+p))/sy; print(f"  y={Y:6.2f}  x {(x0+a-ox)/s:6.2f}..{(x0+b-ox)/s:6.2f}  (n={n})")
print("VERTIKAL (x: y_von..y_bis)")
for p,a,b,n in sorted(Vm):
    if n<2: continue
    X=(x0+p-ox)/s; print(f"  x={X:6.2f}  y {(oy-(y0+b))/sy:6.2f}..{(oy-(y0+a))/sy:6.2f}  (n={n})")
