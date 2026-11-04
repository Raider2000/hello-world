import sys, json, numpy as np
from PIL import Image
# rectify.py KEY  -> liest ctrl.json[KEY], schreibt /tmp/kfs31/r_KEY.png und cal.json[KEY]
key=sys.argv[1]
C=json.load(open('/tmp/kfs31/ctrl.json'))[key]
src=C['src']; S=76.0; X0,Y0,X1,Y1=C.get('box',[-1.5,-3.0,28.5,15.5])
def feats(px,py,terms):
    px=np.asarray(px,float)/1000; py=np.asarray(py,float)/1000
    f={'1':np.ones_like(px),'x':px,'y':py,'xx':px*px,'xy':px*py,'yy':py*py,'xxy':px*px*py,'xyy':px*py*py,'xxx':px**3,'yyy':py**3}
    return np.stack([f[t] for t in terms],axis=1)
TX=C.get('tx',['1','x','y','xx','xy','yy']); TY=C.get('ty',['1','x','y','xx','xy'])
xs=np.array(C['X']); ys=np.array(C['Y'])
ax,res,_,_=np.linalg.lstsq(feats(xs[:,0],xs[:,1],TX),xs[:,2],rcond=None)
ay,res2,_,_=np.linalg.lstsq(feats(ys[:,0],ys[:,1],TY),ys[:,2],rcond=None)
rx=feats(xs[:,0],xs[:,1],TX)@ax-xs[:,2]; ry=feats(ys[:,0],ys[:,1],TY)@ay-ys[:,2]
print('Residuen X (cm):',np.round(rx*100,1)); print('Residuen Y (cm):',np.round(ry*100,1))
im=np.array(Image.open(src).convert('L')); H,W=im.shape
# inverse: Gitter im Bild -> (X,Y), dann Polynom (X,Y)->(px,py) Grad 3
gx,gy=np.meshgrid(np.linspace(0,W,60),np.linspace(0,H,80)); gx=gx.ravel(); gy=gy.ravel()
GX=feats(gx,gy,TX)@ax; GY=feats(gx,gy,TY)@ay
T3=['1','x','y','xx','xy','yy','xxx','xxy','xyy','yyy']
bx=np.linalg.lstsq(feats(GX*1000,GY*1000,T3),gx,rcond=None)[0]
by=np.linalg.lstsq(feats(GX*1000,GY*1000,T3),gy,rcond=None)[0]
w=int((X1-X0)*S); h=int((Y1-Y0)*S)
u,v=np.meshgrid(np.arange(w),np.arange(h))
X=X0+u/S; Y=Y1-v/S
F=feats(X.ravel()*1000,Y.ravel()*1000,T3)
PX=(F@bx).reshape(h,w); PY=(F@by).reshape(h,w)
ok=(PX>=0)&(PX<W-1)&(PY>=0)&(PY<H-1)
# bilinear
x0=np.clip(np.floor(PX).astype(int),0,W-2); y0=np.clip(np.floor(PY).astype(int),0,H-2)
fx=PX-x0; fy=PY-y0
I=im.astype(float)
out=(I[y0,x0]*(1-fx)*(1-fy)+I[y0,x0+1]*fx*(1-fy)+I[y0+1,x0]*(1-fx)*fy+I[y0+1,x0+1]*fx*fy)
out[~ok]=255
Image.fromarray(out.astype(np.uint8)).save(f'/tmp/kfs31/r_{key}.png')
cal=json.load(open('/tmp/kfs31/cal.json'))
cal[key]={"src":f"/tmp/kfs31/r_{key}.png","ox":-X0*S,"oy":Y1*S,"s":S}
json.dump(cal,open('/tmp/kfs31/cal.json','w'),indent=1)
print('ok',w,h)
