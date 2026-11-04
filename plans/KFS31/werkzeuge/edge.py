import sys, numpy as np
from PIL import Image
# edge.py src axis pos lo hi   -> Profil: dunkle Pixel entlang einer Spalte (axis=v: x=pos, y in lo..hi) bzw. Zeile
src,axis,pos,lo,hi=sys.argv[1],sys.argv[2],int(sys.argv[3]),int(sys.argv[4]),int(sys.argv[5])
im=np.array(Image.open(src).convert('L')).astype(float)
if axis=='v': prof=im[lo:hi,pos-2:pos+3].mean(axis=1)
else: prof=im[pos-2:pos+3,lo:hi].mean(axis=0)
dark=prof<150
runs=[];st=None
for i,v in enumerate(list(dark)+[False]):
    if v and st is None: st=i
    if not v and st is not None: runs.append((lo+st,lo+i-1,int(prof[st:i].min())));st=None
print(runs)
