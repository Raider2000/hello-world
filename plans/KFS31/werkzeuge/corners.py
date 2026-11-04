import sys
from PIL import Image, ImageDraw, ImageFont
# corners.py src out cx,cy cx,cy ...  (je 160x160 px Ausschnitt, 3-fach, Raster 10 px)
src,out=sys.argv[1],sys.argv[2]; pts=[tuple(map(int,p.split(','))) for p in sys.argv[3:]]
im=Image.open(src).convert('RGB'); f=ImageFont.load_default()
tiles=[]
for cx,cy in pts:
    x0,y0=cx-80,cy-80; c=im.crop((x0,y0,x0+160,y0+160)).resize((480,480),Image.NEAREST)
    d=ImageDraw.Draw(c)
    for k in range(0,161,10):
        col=(255,0,0) if (x0+k)%50==0 else (255,190,190)
        d.line([(k*3,0),(k*3,480)],fill=col)
        if (x0+k)%50==0: d.text((k*3+2,2),str(x0+k),fill=(200,0,0),font=f)
        col=(0,0,255) if (y0+k)%50==0 else (190,190,255)
        d.line([(0,k*3),(480,k*3)],fill=col)
        if (y0+k)%50==0: d.text((2,k*3+2),str(y0+k),fill=(0,0,200),font=f)
    tiles.append(c)
S=Image.new('RGB',(490*len(tiles),480),'white')
for i,t in enumerate(tiles): S.paste(t,(i*490,0))
S.save(out)
