"""Editable WE05 plan. Geometry unit = mm at full size; print scale 1:50.
Sources and uncertainty are documented in Begleittext.md. No raster tracing embedded.
Only Python standard library and reportlab required. Run beside the output files.
"""
from pathlib import Path
import math, json, xml.etree.ElementTree as ET
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

BASE = Path(__file__).resolve().parent
OUT = BASE.parent if BASE.name == 'bearbeitung' else BASE
SVG = 'http://www.w3.org/2000/svg'
INK = 'http://www.inkscape.org/namespaces/inkscape'
ET.register_namespace('', SVG)
ET.register_namespace('inkscape', INK)
S = 72 / 25.4 / 50
W, H = 14850, 21000
root = ET.Element(f'{{{SVG}}}svg', {'width':'297mm','height':'420mm','viewBox':f'0 0 {W} {H}','version':'1.1'})
ET.SubElement(root, f'{{{SVG}}}title').text = 'WE05 - Reichenbachstraße 25 - rekonstruierter Istzustand'
ET.SubElement(root, f'{{{SVG}}}desc').text = 'Gruppierte Vektorzeichnung. 1 Geometrieeinheit = 1 mm real. A3, Maßstab 1:50. Maße mit ca. sind aus Plänen abgeleitet. Begleittext beachten.'
pdfmetrics.registerFont(TTFont('Plan', 'C:/Windows/Fonts/arial.ttf'))
pdfmetrics.registerFont(TTFont('PlanBold', 'C:/Windows/Fonts/arialbd.ttf'))
c = canvas.Canvas(str(OUT/'WE05_Grundriss_A3_1-50.pdf'), pagesize=(W*S,H*S))
c.setTitle('WE05 | Grundriss nach Sanierung | A3 1:50')
c.setAuthor('Nexus Habitat eGBR')
current=root
wall='#626262'
ink='#202020'

def layer(id,label,plan=True):
    global current
    attrs={'id':id, f'{{{INK}}}groupmode':'layer', f'{{{INK}}}label':label}
    ox,oy=(3300,5500) if plan else (0,0)
    if plan: attrs['transform']=f'translate({ox} {oy})'
    current=ET.SubElement(root,f'{{{SVG}}}g',attrs)
    c.resetTransforms()
    c.transform(S,0,0,-S,ox*S,H*S-oy*S)

def group(id,label):
    global current
    parent=current
    current=ET.SubElement(parent,f'{{{SVG}}}g',{'id':id,f'{{{INK}}}label':label})
    return parent

def style(fill,stroke,width):
    if fill!='none': c.setFillColor(fill)
    if stroke!='none': c.setStrokeColor(stroke)
    c.setLineWidth(width)
    c.setLineJoin(0)
    return int(stroke!='none'), int(fill!='none')

def rect(id,x,y,w,h,fill='none',stroke=ink,sw=14,rx=0):
    if fill == wall: stroke='none'
    a={'id':id,'x':str(x),'y':str(y),'width':str(w),'height':str(h),'fill':fill,'stroke':stroke,'stroke-width':str(sw)}
    if rx:a['rx']=str(rx)
    ET.SubElement(current,f'{{{SVG}}}rect',a)
    st,fi=style(fill,stroke,sw)
    if rx:c.roundRect(x,y,w,h,rx,stroke=st,fill=fi)
    else:c.rect(x,y,w,h,stroke=st,fill=fi)

def path(id,cmds,fill='none',stroke=ink,sw=14):
    d=' '.join(op+' '+' '.join(f'{v:.3f}' for v in vals) for op,*vals in cmds)
    ET.SubElement(current,f'{{{SVG}}}path',{'id':id,'d':d,'fill':fill,'stroke':stroke,'stroke-width':str(sw)})
    p=c.beginPath()
    for op,*a in cmds:
        if op=='M':p.moveTo(*a)
        elif op=='L':p.lineTo(*a)
        elif op=='C':p.curveTo(*a)
        elif op=='Z':p.close()
    st,fi=style(fill,stroke,sw);c.drawPath(p,stroke=st,fill=fi)

def poly(id,pts,fill=wall,stroke='none',sw=16):
    path(id,[('M',*pts[0])]+[('L',*p) for p in pts[1:]]+[('Z',)],fill,stroke,sw)

def line(id,x1,y1,x2,y2,sw=12,stroke=ink):
    path(id,[('M',x1,y1),('L',x2,y2)],stroke=stroke,sw=sw)

def ellipse(id,x,y,rx,ry,fill='white',sw=14):
    ET.SubElement(current,f'{{{SVG}}}ellipse',{'id':id,'cx':str(x),'cy':str(y),'rx':str(rx),'ry':str(ry),'fill':fill,'stroke':ink,'stroke-width':str(sw)})
    st,fi=style(fill,ink,sw);c.ellipse(x-rx,y-ry,x+rx,y+ry,stroke=st,fill=fi)

def text(id,x,y,value,size=165,bold=False,anchor='middle',rotate=0,color=ink):
    a={'id':id,'x':str(x),'y':str(y),'font-family':'Arial, sans-serif','font-size':str(size),'font-weight':'700' if bold else '400','text-anchor':anchor,'fill':color}
    if rotate:a['transform']=f'rotate({rotate} {x} {y})'
    ET.SubElement(current,f'{{{SVG}}}text',a).text=value
    c.saveState();c.translate(x,y);c.rotate(rotate);c.scale(1,-1);c.setFillColor(color);c.setFont('PlanBold' if bold else 'Plan',size)
    {'middle':c.drawCentredString,'start':c.drawString,'end':c.drawRightString}[anchor](0,0,value)
    c.restoreState()

def dh(id,x1,x2,y,witness,label):
    parent=group(id,label)
    for i,x in enumerate((x1,x2)):
        line(f'{id}-hilf-{i}',x,witness,x,y+(90 if y>witness else -90),7,'#6b6b6b')
        line(f'{id}-strich-{i}',x-55,y+85,x+55,y-85,12)
    line(id+'-masslinie',x1,y,x2,y,8)
    tw=len(label)*76
    rect(id+'-textfeld',(x1+x2-tw)/2,y-175,tw,190,'white','none',0)
    text(id+'-wert',(x1+x2)/2,y-35,label,145)
    globals()['current']=parent

def dv(id,y1,y2,x,witness,label):
    parent=group(id,label)
    for i,y in enumerate((y1,y2)):
        line(f'{id}-hilf-{i}',witness,y,x+(90 if x>witness else -90),y,7,'#6b6b6b')
        line(f'{id}-strich-{i}',x-75,y+55,x+75,y-55,12)
    line(id+'-masslinie',x,y1,x,y2,8)
    text(id+'-wert',x-65,(y1+y2)/2,label,145,rotate=-90)
    globals()['current']=parent

layer('00-papier','00 | Papier und Plankopf',False)
rect('papier',0,0,W,H,'white','none')
text('objekt',1000,1040,'REICHENBACHSTRASSE 25 · AUGSBURG',155,True,'start')
text('titel',1000,1520,'WE05  /  Grundriss nach Sanierung',310,True,'start')
text('untertitel',1000,1870,'2. Obergeschoss · Rekonstruktion aus Bestandsunterlagen',155,anchor='start',color='#626262')
text('massstab',13850,1450,'1:50',280,True,'end')
text('blattformat',13850,1780,'A3 · 297 × 420 mm',140,anchor='end')
line('kopf-linie',1000,2120,13850,2120,12)

layer('01-balkon','01 | Balkon - Metallkonstruktion')
parent=group('balkon','Balkon mit schematischem Metallgeländer')
rect('balkon-platte',200,-2500,3000,2500,'#fafafa',ink,16)
path('gelaender-aussen',[('M',200,0),('L',200,-2500),('L',3200,-2500),('L',3200,0)],sw=22)
path('gelaender-innen',[('M',260,0),('L',260,-2440),('L',3140,-2440),('L',3140,0)],sw=10)
for i,(x,y) in enumerate([(200,-2500),(3200,-2500),(200,-80),(3200,-80)]):
    rect(f'balkon-pfosten-{i}',x-35,y-35,70,70,'white',ink,12)
current=parent

layer('02-aussenwaende','02 | Außen- und Wohnungstrennwände')
poly('fassade-links', [(-135,0),(1275,0),(1275,310),(1245,580),(0,580),(0,9270),(1225,9270),(1255,9530),(1255,9840),(-135,9840)])
poly('fassade-oben-mitte',[(2475,0),(3770,0),(3770,190),(3695,580),(2505,580),(2475,310)])
poly('fassade-oben-zwischen-fenstern',[(4265,0),(5340,0),(5340,310),(5310,580),(4330,580),(4265,190)])
poly('fassade-oben-rechts',[(6540,0),(8100,0),(8100,4290),(6180,4290),(6180,4020),(7830,4020),(7830,580),(6570,580),(6540,310)])
poly('fassade-unten-mitte',[(2485,9270),(4380,9270),(4410,9530),(4410,9840),(2455,9840),(2455,9530)])
poly('trennwand-treppenhaus-unten',[(5640,9270),(6610,9270),(6610,5330),(6850,5330),(6850,9840),(5610,9840),(5610,9530)])
rect('eingang-oberer-anschlag',6610,4290,240,140,wall)

layer('03-innenwaende','03 | Erhaltene Innenwände und Wandreste')
rect('wohnen-essen-rest-links',0,4020,500,270,wall)
poly('wohnen-essen-rest-rechts',[(2750,4020),(3250,4020),(3250,3660),(3400,3660),(3400,4430),(3250,4430),(3250,4290),(2750,4290)])
rect('kueche-essen-rest-oben',3250,580,150,750,wall)
rect('wohnen-schlafen-trennwand',3250,5330,150,3940,wall)
rect('schlafen-flur-links',3400,5445,1080,175,wall)
rect('schlafen-flur-rechts',5380,5445,1230,175,wall)
rect('kueche-flur-bestand',4220,4020,1010,270,wall)
rect('kueche-schacht-bestand',4405,580,300,150,wall)

layer('04-neue-waende','04 | Neue Wände und geschlossene Öffnung')
poly('badtrennwand-neu',[(4705,580),(5230,580),(5230,4020),(5055,4020),(5055,730),(4705,730)])
rect('kuechentuer-zugemauert',3400,4020,820,270,wall)
rect('bad-installation-rechts',7680,580,150,3440,wall)
rect('bad-installation-dusche',6630,3060,1050,105,wall)

layer('05-fenster','05 | Fenster und Balkonverglasung')
for id,x1,x2,y in [('kueche',3770,4265,190),('bad',5340,6540,310),('wohnen',1255,2455,9530),('schlafen',4410,5610,9530),('balkon',1275,2475,310)]:
    parent=group('fenster-'+id,'Fenster / Verglasung '+id)
    rect(id+'-rahmen',x1,y-45,x2-x1,90,'white',ink,12)
    line(id+'-glas',x1,y,x2,y,8)
    for ix,x in enumerate([x1,x2]):rect('fenster-'+id+'-pfosten-'+str(ix),x,y-45,30,90,'white',ink,8)
    current=parent
line('kuechenfenster-aussenbank',3770,20,4265,20,8)
line('badfenster-aussenbank',5340,20,6540,20,8)

layer('06-tueren','06 | Türen mit Öffnungsbögen')
k=.5522847498
# Each retained door is independently grouped, with leaf and cubic quarter circle.
parent=group('tuer-balkon','Balkontür - Anschlag gemäß Quelle')
line('balkontuer-blatt',2445,355,2445,1465,20)
path('balkontuer-bogen',[('M',1335,355),('C',1335,355+1110*k,2445-1110*k,1465,2445,1465)],sw=10)
current=parent
parent=group('tuer-bad','Badtür')
line('badtuer-blatt',5230,4290,5230,3340,20)
path('badtuer-bogen',[('M',6180,4290),('C',6180,4290-950*k,5230+950*k,3340,5230,3340)],sw=10)
current=parent
parent=group('tuer-wohnen','Tür zwischen Flur und Wohnen')
line('wohntuer-blatt',3400,4430,2500,4430,20)
path('wohntuer-bogen',[('M',2500,4430),('C',2500,4430+900*k,3400-900*k,5330,3400,5330)],sw=10)
current=parent
parent=group('tuer-schlafen','Schlafzimmertür')
line('schlaftuer-blatt',4480,5445,4480,6345,20)
path('schlaftuer-bogen',[('M',5380,5445),('C',5380,5445+900*k,4480+900*k,6345,4480,6345)],sw=10)
current=parent
parent=group('wohnungseingang','Wohnungseingangstür')
line('eingang-blatt',6610,4430,5710,4430,22)
path('eingang-bogen',[('M',5710,4430),('C',5710,4430+900*k,6610-900*k,5330,6610,5330)],sw=10)
current=parent

layer('07-sanitaer','07 | Sanitär und Waschmaschine - schematisch')
rect('kueche-bestandskontur-oben',3400,580,1005,150,'white',ink,10)
rect('bad-vorwand-links',5230,720,150,2220,'white',ink,10)
parent=group('wc','WC')
rect('wc-anschluss',5380,880,140,330,'white')
ellipse('wc-aussen',5580,1045,275,165)
ellipse('wc-innen',5615,1045,170,112,sw=10)
current=parent
parent=group('waschtisch','Waschtisch')
ellipse('waschtisch-aussen',5580,2180,245,330)
ellipse('waschtisch-becken',5600,2180,170,245,sw=10)
line('waschtisch-armatur',5380,2180,5500,2180,14)
current=parent
parent=group('badewanne','Badewanne')
rect('wanne-aussen',6930,1450,750,1550,'white',ink,16)
rect('wanne-innen',6990,1510,630,1430,'white',ink,12,rx=250)
ellipse('wannenablauf',7305,2820,30,30,sw=9)
current=parent
parent=group('dusche','Dusche')
rect('duschwanne',6630,3165,1050,855,'white',ink,14)
line('duschglas',6630,3170,6630,4020,18)
line('dusche-brause',7470,3290,7470,3550,10)
ellipse('dusche-kopf',7470,3290,40,40,sw=10)
line('dusche-diagonale',6810,3820,7350,3420,10)
current=parent
parent=group('waschmaschine','Waschmaschinenstellplatz gemäß Quelle')
rect('wm-umriss',7080,620,600,650,'white',ink,14)
text('wm-text',7380,1010,'WM',145)
current=parent

layer('08-beschriftung','08 | Räume und Zugang')
for id,x,y,t in [('essen',1600,2400,'Essen'),('kochen',4210,1560,'Kochen'),('wohnen',1600,7230,'Wohnen'),('schlafen',5000,7570,'Schlafen'),('flur',4850,4900,'Flur'),('bad',6370,2380,'Bad'),('balkon-label',1700,-1300,'Balkon')]:
    text(id,x,y,t,215)
text('balkon-art',1700,-1000,'Metallkonstruktion',135,color='#626262')
text('eingang-label',7120,4830,'WE05',160,True,anchor='start')
line('eingang-richtung',7340,5000,6950,5000,12)
path('eingang-pfeil',[('M',7030,4950),('L',6950,5000),('L',7030,5050)],sw=12)

layer('09-bemassung','09 | Bemaßung - Maße in m; ca. = abgeleitet')
dh('breite-wohnen',0,3250,10450,9840,'3,25')
dh('breite-schlafen',3400,6610,10450,9840,'3,21')
dh('gesamtbreite-unten',0,6850,11050,9840,'6,85')
text('zwischenwand-mass',3325,10830,'0,15',125)
text('trennwand-mass',6730,10830,'0,24',125)
dh('breite-kueche',3400,5055,2170,1600,'ca. 1,66')
dh('breite-bad-licht',5380,7680,1370,1290,'ca. 2,30')
dh('durchgang-wohnen-essen',500,2750,3570,4020,'ca. 2,25')
dh('balkon-breite',200,3200,-2920,-2500,'ca. 3,00')
dv('balkon-tiefe',-2500,0,-350,200,'ca. 2,50')
dv('gebaeude-tiefe',0,9840,-1550,-135,'9,84')
dv('raumtiefe-oben',580,4020,-750,0,'ca. 3,44')
dv('raumtiefe-wohnen',4290,9270,-750,0,'ca. 4,98')
dv('raumtiefe-schlafen',5620,9270,7430,6850,'ca. 3,65')
dv('bad-tiefe',580,4020,8710,8100,'ca. 3,44')

layer('10-planhinweise','10 | Maßstabsleiste und Hinweise',False)
line('fuss-linie',1000,17650,13850,17650,12)
text('fuss-titel',1000,18120,'PLANBASIS & MASSSTAB',150,True,anchor='start')
text('fuss-text-1',1000,18450,'Maße in m. „ca.“ = aus Planunterlagen abgeleitet; keine Vor-Ort-Messung.',140,anchor='start')
text('fuss-text-2',1000,18720,'Istzustand gemäß Auskunft des Eigentümers: Gelb entfernt, Rot als Bestand übernommen.',140,anchor='start')
text('fuss-text-3',1000,18990,'Balkon, Öffnungen, Vorwände und nicht bemaßte Bauteile: siehe Begleittext.',140,anchor='start')
text('fuss-text-4',1000,19260,'Keine Raumflächen übernommen. Druck: A3, 100 %, ohne Seitenanpassung.',140,anchor='start')
text('stand',13850,18120,'Stand: 12.09.2026',140,anchor='end')
text('version',13850,18450,'WE05-GR-01 · v1',140,anchor='end')
for i in range(4):
    rect('massstab-block-'+str(i),1000+i*500,19800,500,100,ink if i%2==0 else 'white',ink,8)
for x,t in [(1000,'0'),(2000,'1'),(3000,'2 m')]:text('massstab-'+t,x,20150,t,130)
text('svg-hinweis',13850,20150,'SVG: getrennte, benannte Ebenen und Einzelobjekte',130,anchor='end',color='#626262')

c.showPage();c.save()
ET.indent(root,space='  ')
ET.ElementTree(root).write(OUT/'WE05_Grundriss_editierbar.svg',encoding='utf-8',xml_declaration=True)
print('Created SVG and PDF in',OUT)
