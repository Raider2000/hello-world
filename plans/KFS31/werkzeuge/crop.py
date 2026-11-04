import sys
from PIL import Image
# crop.py src out rot x0 y0 x1 y1 [maxw]  (Koordinaten in Bruchteilen 0..1 nach Rotation)
src,out,rot=sys.argv[1],sys.argv[2],int(sys.argv[3])
x0,y0,x1,y1=map(float,sys.argv[4:8]); mw=int(sys.argv[8]) if len(sys.argv)>8 else 1600
im=Image.open(src).convert('L')
if rot: im=im.rotate(rot,expand=True)
W,H=im.size
c=im.crop((int(x0*W),int(y0*H),int(x1*W),int(y1*H)))
if c.width>mw: c=c.resize((mw,int(c.height*mw/c.width)),Image.LANCZOS)
elif c.width<mw//2: c=c.resize((c.width*2,c.height*2),Image.LANCZOS)
c.save(out); print(c.size, (W,H))
