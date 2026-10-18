import math, random, json
O='/workspace/ns-animate/design/stamp/'
INK='#111'
def circ(cx,cy,rx,ry=None,n=28,a0=0):
    ry=ry or rx; return [(cx+rx*math.cos(a0+2*math.pi*i/n),cy+ry*math.sin(a0+2*math.pi*i/n)) for i in range(n)]
def cubic(p0,p1,p2,p3,n=8): return [tuple((1-t)**3*a+3*(1-t)**2*t*b+3*(1-t)*t*t*c+t**3*d for a,b,c,d in zip(p0,p1,p2,p3)) for t in [i/n for i in range(1,n+1)]]
# skull outline
S=[(40,12)]
for seg in [((27,12),(19,21),(19,32)),((19,40),(23,44),(27,46)),((27,49),(27,52),(27,53)),((27,55),(29,56),(31,56))]:
    S+=cubic(S[-1],*seg)
S+=[(49,56)]
for seg in [((51,56),(53,55),(53,53)),((53,52),(53,49),(53,46)),((57,44),(61,40),(61,32)),((61,21),(53,12),(40,12))]:
    S+=cubic(S[-1],*seg)
S=S[:-1]
EYEL=circ(31.5,32.5,5.6,5.2,a0=.3); EYER=circ(48.5,32.5,5.6,5.2,a0=.9)
NOSE=[(40,38.5),(36.8,45),(43.2,45)]
TEETH=[[(x,49),(x+2.2,49),(x+2.2,56.5),(x,56.5)] for x in (33.9,38.9,43.9)]
def bone(a,b):
    L=math.hypot(b[0]-a[0],b[1]-a[1]);ux,uy=(b[0]-a[0])/L,(b[1]-a[1])/L;vx,vy=-uy,ux;h=L/2-3
    loc=[(-h,-2.6),(h,-2.6)]
    for cy,a0,a1 in ((-3.3,-160,70),(3.3,-70,160)):
        loc+=[(h+2.2+3.4*math.cos(math.radians(t)),cy+3.4*math.sin(math.radians(t))) for t in range(a0,a1+1,15)]
    loc+=[(h,2.6),(-h,2.6)]
    for cy,a0,a1 in ((3.3,20,250),(-3.3,110,340)):
        loc+=[(-h-2.2+3.4*math.cos(math.radians(t)),cy+3.4*math.sin(math.radians(t))) for t in range(a0,a1+1,15)]
    mx,my=(a[0]+b[0])/2,(a[1]+b[1])/2
    return [(mx+u*ux+v*vx,my+u*uy+v*vy) for u,v in loc]
B1=bone((19,58),(61,72)); B2=bone((61,58),(19,72))
RING_O=circ(40,40,37,n=60); RING_I=circ(40,40,33.2,n=60,a0=.05)
def jit(poly,amt,seed,sub=2.0):
    r=random.Random(seed);out=[]
    for i in range(len(poly)):
        a=poly[i];b=poly[(i+1)%len(poly)];d=math.hypot(b[0]-a[0],b[1]-a[1]);n=max(1,int(d/sub))
        for k in range(n):
            t=k/n;x=a[0]+(b[0]-a[0])*t;y=a[1]+(b[1]-a[1])*t
            out.append((x+r.uniform(-amt,amt),y+r.uniform(-amt,amt)))
    return out
P=lambda poly:'M'+' L'.join('%.1f %.1f'%p for p in poly)+'Z'
def shapes(rough=0,seed=1):
    j=(lambda p,s: jit(p,rough,seed*100+s)) if rough else (lambda p,s:p)
    ring=P(j(RING_O,1))+P(j(RING_I,2))
    skull=P(j(S,3))+''.join(P(j(h,4+i)) for i,h in enumerate([EYEL,EYER,NOSE]+TEETH))
    bones=P(j(B1,10))+P(j(B2,11))
    return ring,skull,bones
def ink_group(ring,skull,bones,mask_id):
    # bones get a 2.4px gap around the skull via a mask
    return (f"<mask id='{mask_id}' maskUnits='userSpaceOnUse' x='0' y='0' width='80' height='80'><rect width='80' height='80' fill='#fff'/>"
            f"<path d='{P(S)}' fill='#000' stroke='#000' stroke-width='4.2' stroke-linejoin='round'/></mask>"
            f"<g fill='{INK}'><path d='{ring}' fill-rule='evenodd'/><path d='{bones}' mask='url(#{mask_id})'/><path d='{skull}' fill-rule='evenodd'/></g>")
def textured(ID,seed):
    ring,skull,bones=shapes()
    f=(f"<filter id='sf{ID}' x='-8%' y='-8%' width='116%' height='116%' color-interpolation-filters='sRGB'>"
       f"<feTurbulence type='fractalNoise' baseFrequency='.09' numOctaves='2' seed='{seed}' result='n'/>"
       f"<feDisplacementMap in='SourceGraphic' in2='n' scale='2.4' xChannelSelector='R' yChannelSelector='G' result='d0'/>"
       f"<feTurbulence type='fractalNoise' baseFrequency='.8' numOctaves='1' seed='{seed}' result='g'/>"
       f"<feDisplacementMap in='d0' in2='g' scale='1.3' xChannelSelector='R' yChannelSelector='G' result='d'/>"
       f"<feTurbulence type='fractalNoise' baseFrequency='.07' numOctaves='3' seed='{seed+11}' result='p'/>"
       f"<feColorMatrix in='p' type='matrix' values='0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 -5 0 0 0 3.55' result='pm'/>"
       f"<feTurbulence type='fractalNoise' baseFrequency='.6' numOctaves='2' seed='{seed+23}' result='s'/>"
       f"<feColorMatrix in='s' type='matrix' values='0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 -22 0 0 14.5' result='sm'/>"
       f"<feComposite in='pm' in2='sm' operator='arithmetic' k1='1' result='m'/>"
       f"<feComposite in='d' in2='m' operator='in' result='ink'/>"
       f"<feMorphology in='d' operator='dilate' radius='1.1' result='hd0'/>"
       f"<feComponentTransfer in='hd0' result='hd'><feFuncA type='linear' slope='4' intercept='-1.5'/></feComponentTransfer>"
       f"<feComposite in='hd' in2='d' operator='out' result='ring'/>"
       f"<feFlood flood-color='#fff' flood-opacity='1'/><feComposite in2='ring' operator='in' result='halo'/>"
       f"<feMerge><feMergeNode in='halo'/><feMergeNode in='ink'/></feMerge></filter>")
    return (f"<svg viewBox='0 0 80 80' width='80' height='80'><defs>{f}</defs>"
            f"<g filter='url(#sf{ID})'>{ink_group(ring,skull,bones,'sm'+str(ID))}</g></svg>")
def static():
    ring,skull,bones=shapes(rough=.45,seed=5)
    r=random.Random(42); voids=''
    # fixed irregular ink voids (paper showing through) + a lighter patch
    spots=[(24,20,2.2),(57,24,1.6),(66,52,2.0),(14,44,1.8),(44,18,1.4),(35,27,1.0),(52,47,1.2),(26,64,1.5),(56,68,1.3),(40,74,1.8),(30,50,0.9),(47,60,1.0),(62,36,1.1),(19,32,1.0),(34,15,0.9)]
    for x,y,s in spots:
        n=7;voids+=P([(x+s*(0.6+0.5*r.random())*math.cos(2*math.pi*k/n),y+s*(0.6+0.5*r.random())*math.sin(2*math.pi*k/n)) for k in range(n)])
    pin=''.join(P(circ(r.uniform(6,74),r.uniform(6,74),r.uniform(.35,.6),n=5)) for _ in range(40))
    ids='stS'
    halo=(f"<g fill='none' stroke='#fff' stroke-width='2.3' stroke-linejoin='round' stroke-linecap='round'><path d='{ring}'/><path d='{skull}'/><path d='{bones}'/></g>")
    return (f"<svg viewBox='0 0 80 80' width='80' height='80'><defs><mask id='{ids}v' maskUnits='userSpaceOnUse' x='0' y='0' width='80' height='80'>"
            f"<rect width='80' height='80' fill='#fff'/><path d='{voids}{pin}' fill='#000'/><ellipse cx='56' cy='22' rx='13' ry='8' fill='#000' fill-opacity='.22' transform='rotate(-25 56 22)'/><ellipse cx='22' cy='58' rx='9' ry='6' fill='#000' fill-opacity='.18'/></mask></defs>"
            f"{halo}<g mask='url(#{ids}v)'>{ink_group(ring,skull,bones,ids+'b')}</g></svg>")
X="<svg xmlns='http://www.w3.org/2000/svg' "
open(O+'stamp.svg','w').write(textured('STAMP_ID',3).replace('<svg ',X,1))
st=static(); open(O+'stamp-static.svg','w').write(st.replace('<svg ',X,1))
SEEDS=[3,17,41,88]
tpl=textured('@@ID@@',999)
a,b=tpl.split('@@ID@@',1)[0],None
# build JS with + concatenation; ids = 'sf'+i, seeds by i%4
parts=tpl.replace("seed='999'","seed='@@S0@@'").replace("seed='1010'","seed='@@S1@@'").replace("seed='1022'","seed='@@S2@@'")
js=json.dumps(parts).replace("'","'")
js=js.replace('@@ID@@','"+i+"').replace('@@S0@@','"+s+"').replace('@@S1@@','"+(s+11)+"').replace('@@S2@@','"+(s+23)+"')
open(O+'stamp-svgs.js','w').write(
"// Generated by stamp-gen.py. Single-quoted SVG strings (no backticks / ${ inside).\n"
"// STAMP_SVG(i): textured rubber stamp for cell i; filter/mask ids are unique per i, feTurbulence seed varies with i (4 variants).\n"
"(function(){\n  var SEEDS="+json.dumps(SEEDS)+";\n  window.STAMP_SVG=function(i){var s=SEEDS[i%SEEDS.length];return "+js+";};\n"
"  // Filter-free fallback (fixed mask ids 'stSv'/'stSb'; identical copies on the page are harmless).\n  window.STAMP_STATIC="+json.dumps(st)+";\n})();\n")
open('/tmp/pred/stamp_variants.json','w').write(json.dumps([textured(f'v{k}',s) for k,s in enumerate(SEEDS)]+[st]))
