import random, math
M=lambda p:(round(100-p[0],2),p[1])
def path(cmds,m=False):
    f=M if m else (lambda p:p); out=''
    for c,pts in cmds:
        out+=c+' '.join('%g %g'%f(p) for p in pts)+' '
    return out.strip()+'Z'
# left forewing: shoulder -> leading edge -> tip -> scalloped trailing edge -> inner corner -> up along abdomen
TE=[(3,58.6),(9,60.4),(15,59.3),(21,59.8),(27,58.9),(33,59.2),(39.3,57.2)]
fore=[('M',[(43,28)]),('C',[(33,32.5),(14,45),(4.3,54.8)]),('C',[(2.4,57.2),(2.2,58.4),TE[0]])]
for a,b in zip(TE,TE[1:]):
    mid=((a[0]+b[0])/2,max(a[1],b[1])+0.9)
    fore.append(('Q',[mid,b]))
fore.append(('C',[(41,51.5),(43.6,44),(45.3,37.5)]))
hind=[('M',[(45.6,35)]),('C',[(42,41),(37.2,50),(36.8,56)]),('C',[(36.6,60.4),(40.5,62.2),(44.6,61)]),('C',[(47.4,60),(48.6,57.5),(48.2,52)]),('C',[(47.8,46),(47.2,40),(46.6,35)])]
wings=' '.join("<path d='%s'/>"%path(s,m) for s in (hind,fore) for m in (0,1) )
# veins radiating from base (+ mirror)
base=(44,33)
ends=[(8,55),(16,57.5),(24,57.8),(31,58),(37,57.4),(42,55.5)]
veins=' '.join('M%g %g Q%g %g %g %g'%(base[0],base[1],(base[0]+e[0])/2+1,(base[1]+e[1])/2-2.5,e[0],e[1]) for e in ends)
veins+=' '+' '.join('M%g %g Q%g %g %g %g'%(100-base[0],base[1],100-((base[0]+e[0])/2+1),(base[1]+e[1])/2-2.5,100-e[0],e[1]) for e in ends)
# crossline (subtle postmedial)
cl=[(30,38),(29,44),(31,48),(30,54),(32,58)]
def pl(p,m=0): return 'M'+' L'.join('%g %g'%(M(q) if m else q) for q in p)
# speckles inside left forewing triangle approx: barycentric inside tri shoulder/tip/inner
random.seed(3); dots=[]
A,B,C=(43,31),(6,56.5),(44,56)
while len(dots)<34:
    u,v=random.random(),random.random()
    if u+v>1: u,v=1-u,1-v
    p=(A[0]+u*(B[0]-A[0])+v*(C[0]-A[0]),A[1]+u*(B[1]-A[1])+v*(C[1]-A[1]))
    if any(math.hypot(p[0]-q[0],p[1]-q[1])<2.6 for q,_ in dots): continue
    dots.append((p,random.choice([.4,.5,.6,.8])))
specks=''.join("<circle cx='%.1f' cy='%.1f' r='%.1f'/><circle cx='%.1f' cy='%.1f' r='%.1f'/>"%(x,y,r,100-x,y,r) for (x,y),r in dots)
# antennae bipectinate along front edge, V forward-outward
def ant(s):
    P0=(50+s*2.2,21.6);P1=(50+s*10,20.5);P2=(50+s*16.8,32)
    q=lambda t:((1-t)**2*P0[0]+2*(1-t)*t*P1[0]+t*t*P2[0],(1-t)**2*P0[1]+2*(1-t)*t*P1[1]+t*t*P2[1])
    out='M%g %g Q%g %g %g %g'%(*P0,*P1,*P2); n=13
    for i in range(1,n+1):
        t=i/(n+.4); px,py=q(t); a,b=q(t+.01); ux,uy=a-px,b-py; L=math.hypot(ux,uy); ux,uy=ux/L,uy/L
        l=2.6*(1-t)**0.7+0.35
        for side in (1,-1):
            nx,ny=-uy*side,ux*side
            vx,vy=nx*.85+ux*.55,ny*.85+uy*.55
            out+=' M%.2f %.2f l%.2f %.2f'%(px,py,vx*l,vy*l)
    return out
body=("<path d='M45.4 37 C45.2 45,47 52.5,50 57 C53 52.5,54.8 45,54.6 37Z'/>"
 "<circle cx='50' cy='21.2' r='2.2'/>"
 "<ellipse cx='50' cy='30.2' rx='8' ry='8.8'/>"
 "<path d='M46.2 41.5h7.6M46.6 45.5h6.8M47.3 49.5h5.4M48.3 53.5h3.4' fill='none' stroke-width='.8'/>")
def leg(pts,m=False):
    f=(lambda p:(round(100-p[0],2),p[1])) if m else (lambda p:p)
    return 'M'+' L'.join('%g %g'%f(p) for p in pts)
FRONT=[(53.5,23.5),(57.5,21.2),(60.5,17.2)]
MID=[(56.5,28.5),(63.5,27.6),(68.5,25.6)]
legs="<path class='legs' d='%s' stroke='#333' stroke-width='1' fill='none' stroke-linecap='round' stroke-linejoin='round'/>"%' '.join(leg(p,m) for p in (FRONT,MID) for m in (0,1))
antp="<path class='antennae' d='%s %s' stroke='#333' stroke-width='.7' fill='none' stroke-linecap='round'/>"%(ant(-1),ant(1))
svg=f"""<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 80'>
{legs}
{antp}
<g class='wings' fill='#888' stroke='#0005' stroke-width='1.5' stroke-linejoin='round'>{wings}{body}</g>
</svg>"""
open('/workspace/natural-selection/design/moth.svg','w').write(svg)
inner=svg.split('\n',1)[1].rsplit('</svg>',1)[0]
def m(fill,w=86,h=72,extra=''): return f"<svg viewBox='0 0 100 80' width='{w}' height='{h}' {extra}>"+inner.replace("fill='#888'",f"fill='{fill}'",1)+"</svg>"
fills=['#fff','#888','#222','#6a8f3c']
row=lambda pairs:''.join(f"<div class='c'><div class='cell' style='background:{bg}'>{m(f)}</div><small>{f} on {bg}</small></div>" for f,bg in pairs)
css="<style>body{margin:0;background:#d9d6cf;font:13px system-ui;padding:20px;color:#333}.row{display:flex;gap:18px;margin-bottom:12px}.c{text-align:center}.cell{width:90px;height:90px;display:flex;align-items:center;justify-content:center;border-radius:8px}</style>"
open('/tmp/mp.html','w').write(f"<html><body>{css}<h3 style='margin:0 0 8px'>Peppered moth - real size 86x72 in 90x90 cells</h3><div class='row'>{row([(f,'#b9b4a8') for f in fills])}</div><div class='row'>{row([(f,f) for f in fills])}</div><div>3x enlarged (fill #fff):</div><div style='background:#b9b4a8;display:inline-block;padding:10px;border-radius:12px'>{m('#fff',258,216)}</div></body></html>")
open('/tmp/vs.html','w').write(f"<html><body>{css}<div class='row' style='align-items:center'><div><img src='/tmp/ref.jpg' style='height:240px;border-radius:8px'><br>Reference photo</div><div><div style='background:#b9b4a8;padding:10px;border-radius:12px'>{m('#222',300,240)}</div>3x moth (fill #222)</div><div><div style='background:#b9b4a8;padding:10px;border-radius:12px'>{m('#fff',300,240)}</div>3x moth (fill #fff)</div></div></body></html>")
# trace overlay: 10px per unit; photo mapped x'=(x-513)*.1+50
open('/tmp/ov.html','w').write(f"<html><body style='margin:0;background:#fff'><div style='position:relative;width:1000px;height:800px'><img src='/tmp/ref.jpg' style='position:absolute;left:-13px;top:150px;width:1024px'>{m('#f00',1000,800,extra=chr(39)*0+'style=\"position:absolute;left:0;top:0;opacity:.45\"')}</div></body></html>")
