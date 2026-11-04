import sys
from PIL import Image, ImageDraw, ImageFont
# grid.py src out x0 y0 x1 y1 step [scale]  (Pixelkoordinaten Original)
src,out=sys.argv[1],sys.argv[2]
x0,y0,x1,y1,step=map(int,sys.argv[3:8]); sc=float(sys.argv[8]) if len(sys.argv)>8 else 1.0
im=Image.open(src).convert('RGB').crop((x0,y0,x1,y1))
im=im.resize((int(im.width*sc),int(im.height*sc)),Image.LANCZOS)
d=ImageDraw.Draw(im)
f=ImageFont.load_default()
for gx in range((x0//step+1)*step,x1,step):
    X=(gx-x0)*sc; d.line([(X,0),(X,im.height)],fill=(255,0,0) if gx%(step*5)==0 else (255,170,170),width=1)
    d.text((X+2,2),str(gx),fill=(200,0,0),font=f)
for gy in range((y0//step+1)*step,y1,step):
    Y=(gy-y0)*sc; d.line([(0,Y),(im.width,Y)],fill=(0,0,255) if gy%(step*5)==0 else (170,170,255),width=1)
    d.text((2,Y+2),str(gy),fill=(0,0,200),font=f)
im.save(out); print(im.size)
