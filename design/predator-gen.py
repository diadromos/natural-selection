import re
D='/workspace/natural-selection/design/'
def mark(paths,dots):
    # paths: list of d strings (stroked); dots: list of (cx,cy,r) filled eye dots
    d=' '.join(paths)
    halo=f"<g fill='none' stroke='#000' stroke-opacity='.55' stroke-width='6.5' stroke-linejoin='round' stroke-linecap='round'><path d='{d}'/>"+''.join(f"<circle cx='{x}' cy='{y}' r='{r+1.6}' fill='#000' fill-opacity='.55' stroke='none'/>" for x,y,r in dots)+"</g>"
    red=f"<g fill='none' stroke='#e00' stroke-width='3' stroke-linejoin='round' stroke-linecap='round'><path d='{d}'/>"+''.join(f"<circle cx='{x}' cy='{y}' r='{r}' fill='#e00' stroke='none'/>" for x,y,r in dots)+"</g>"
    return f"<svg viewBox='0 0 80 80' width='80' height='80'>{halo}{red}</svg>"
bird=mark([
 # body outline: beak base top -> crown -> nape -> back -> tail (notched) -> belly -> throat
 "M62 22 C58 13 46 13 43 22 C38 30 29 36 21 45 L7 54 L13 57 L8 63 L24 56 C33 62 49 61 57 50 C61 44 63 39 63 35",
 # conical finch beak + gape line
 "M62 22 L74 29 L63 35 M64 28.8 L71 29.2",
 # wing
 "M45 31 C37 34 29 42 25 51 C35 50 44 45 49 38",
 # legs + perch
 "M38 60 L36 69 M46 58 L46 69 M28 70 L56 70"],[(53.5,25,2)])
fish=mark([
 # body: snout -> back -> peduncle -> forked tail -> belly
 "M8 41 C13 30 26 24 40 24 C52 24 60 31 64 38 L75 28 L71 40.5 L75 53 L64 43 C59 50 48 56 36 56 C22 56 12 50 8 41",
 # mouth, gill line
 "M8 41 L14 42 M24 30 C28 36 28 45 24 51",
 # spiny first dorsal (zigzag) + soft second dorsal
 "M27 26 L29 15 L33 25 L36 13 L39 24 L42 14.5 L45 24.5 M48 25 C51 16 58 18 60 31",
 # pectoral, pelvic, anal fins
 "M30 43 C34 47 38 47 41 44 M30 55 L27 63 L36 56 M47 54 C49 61 55 61 59 49"],[(17,36,2)])
open(D+'predator-bird.svg','w').write(bird.replace("<svg ","<svg xmlns='http://www.w3.org/2000/svg' ",1))
open(D+'predator-fish.svg','w').write(fish.replace("<svg ","<svg xmlns='http://www.w3.org/2000/svg' ",1))
open('/tmp/pred/bird.txt','w').write(bird); open('/tmp/pred/fish.txt','w').write(fish)
# preview
bfly="<svg viewBox='0 0 100 80'><g fill='{f}' stroke='#0005' stroke-width='1.5'><path d='M50 39 C36 -6,-6 -4,2 26 C5 44,30 48,50 41Z'/><path d='M50 39 C64 -6,106 -4,98 26 C95 44,70 48,50 41Z'/><path d='M50 41 C28 38,2 52,12 70 C22 86,46 70,50 45Z'/><path d='M50 41 C72 38,98 52,88 70 C78 86,54 70,50 45Z'/></g><ellipse cx='50' cy='42' rx='3' ry='18' fill='#333'/><path d='M49 25 Q44 10 38 6 M51 25 Q56 10 62 6' stroke='#333' stroke-width='1.5' fill='none'/></svg>"
moth=open(D+'moth.svg').read()
moth=re.sub(r"<svg[^>]*>","<svg viewBox='0 0 100 80'>",moth,1).replace("fill='#888'","fill='{f}'",1)
sq=open('/workspace/natural-selection/squirt.svg').read()
sq=re.sub(r"<svg[^>]*>","<svg viewBox='0 0 80 100' style='color:{f}'>",sq,1)
bgs=[('#ffffff','#c9b26a'),('#888888','#5a7fa8'),('#000000','#9a4fd0'),('#e00000','#e83a1a'),('#2a9a2a','#3cb84a')]
css="""<style>body{margin:0;background:#1b1d22;color:#ccc;font:13px system-ui;padding:16px}
.row{display:flex;gap:12px;margin:6px 0 14px;align-items:flex-end}.c{text-align:center}
.org{width:90px;height:90px;position:relative;display:flex;align-items:center;justify-content:center;border-radius:6px}
.org>svg{width:86px;height:72px}.org.sq>svg{width:70px;height:86px}.eaten>svg{opacity:.8}
.mark{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;pointer-events:none;filter:drop-shadow(0 0 3px #000)}</style>"""
def cells(creature,mk,cls=''):
    return ''.join(f"<div class='c'><div class='org eaten {cls}' style='background:{bg}'>{creature.replace('{f}',f)}<div class='mark'>{mk}</div></div><small>{bg}</small></div>" for bg,f in bgs)
def big(mk,bg,cr,f):
    cr2=cr.replace('{f}',f).replace('<svg ','<svg style="width:258px;height:216px" ',1)
    mk2=mk.replace("width='80' height='80'","width='240' height='240'")
    return "<div class='org eaten' style='width:270px;height:270px;background:"+bg+"'>"+cr2+"<div class='mark'>"+mk2+"</div></div>"
html=f"""<html><body>{css}
<div>Bird mark over butterflies (index):</div><div class='row'>{cells(bfly,bird)}</div>
<div>Bird mark over moths (mono/spots):</div><div class='row'>{cells(moth,bird)}</div>
<div>Fish mark over squirts (squirts):</div><div class='row'>{cells(sq,fish,'sq')}</div>
<div>3x:</div><div class='row'>{big(bird,'#888888',moth,'#d8d8d8')}{big(fish,'#2a9a2a',sq.replace("style='color:{f}'","style='color:{f};width:210px;height:258px'"),'#e8a020')}</div>
</body></html>"""
open('/tmp/pred/preview.html','w').write(html)
