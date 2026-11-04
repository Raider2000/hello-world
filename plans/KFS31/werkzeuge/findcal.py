import sys, numpy as np
from PIL import Image
# Sucht in einem 2010-Blatt: lange horizontale Linien (Fassade, Maßketten) und vertikale Gebäudekanten
src=sys.argv[1]
im=np.array(Image.open(src).convert('L'))<140
H,W=im.shape
# horizontale Läufe > 600 px
rows=[]
for j in range(H):
    r=im[j]; 
    if r.sum()<600: continue
    # längster Lauf
    d=np.diff(np.concatenate([[0],r.astype(int),[0]])); s=np.where(d==1)[0]; e=np.where(d==-1)[0]
    L=(e-s); k=L.argmax()
    if L[k]>600: rows.append((j,s[k],e[k]))
prev=-10
for j,a,b in rows:
    if j-prev>2: print('H',j,a,b)
    prev=j
