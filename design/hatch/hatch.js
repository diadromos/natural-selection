/* Hatch step (breeding-hearts branch), runs after the hearts and eggs (design/hearts/hearts.js).
   1. Each parent's egg wobbles, cracks and pops (SFX 'hatch').
   2. Two babies leave each egg: every child starts from one parent of its pair (children 4k and 4k+2 = child(a,b)
      start from a; 4k+1 and 4k+3 = child(b,a) start from b), tinted with the child's own gene color, and
      inch (caterpillar) or swim (baby squid) to the child's actual new cell (SFX 'inch' / 'swim').
   3. On arrival the baby swells and fades while the adult, rendered as normal by the page's render(), scales up
      in that cell (SFX 'grow').
   Everything lives in one absolutely positioned layer INSIDE #grid (grid-relative px from offsetLeft/Top, like
   the predator layer), so it scrolls with the grid. Reduced motion: no travel; the old grid cross-fades to the
   new adults. Never recolors creatures: babies use the page's gene color, adults are the page's own markup. */
(function(){
const H={hold:400,eggStagger:40,wobble:150,crack:70,pop:230,second:140,minTravel:700,maxTravel:1500,perPx:1.0,
 grow:550,ghostFade:450,stride:{caterpillar:320,squid:300},size:.46,reducedFade:400};
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const css=`
#grid .hatch-layer{position:absolute;inset:0;pointer-events:none;z-index:40;overflow:visible}
#grid .hatch-layer .ghost{position:absolute}
#grid .hatch-layer .ghost>.org{margin:0}
#grid .hatch-layer .baby{position:absolute;left:0;top:0;transform-origin:50% 50%;will-change:transform}
#grid .hatch-layer .baby>.body{display:block}
#grid .hatch-layer .baby svg{display:block;width:100%;height:100%;overflow:visible;filter:drop-shadow(0 1px 1.5px rgba(0,0,0,.45))}
#grid .hatch-layer .crack{position:absolute;inset:0;width:100%;height:100%;opacity:0}
#grid .org[data-unborn]>*{opacity:0}
@keyframes inchLoop{0%,100%{transform:scaleX(1) scaleY(1)}50%{transform:scaleX(.72) scaleY(1.25)}}
@keyframes jetLoop{0%,100%{transform:scaleY(1) scaleX(1)}30%{transform:scaleY(.78) scaleX(1.14)}60%{transform:scaleY(1.12) scaleX(.9)}}
#grid .hatch-layer .baby.caterpillar>.body{transform-origin:0% 60%;animation:inchLoop ${H.stride.caterpillar}ms ease-in-out infinite}
#grid .hatch-layer .baby.squid>.body{transform-origin:50% 30%;animation:jetLoop ${H.stride.squid}ms ease-out infinite}
`;
const st=document.createElement('style');st.id='hatch-css';st.textContent=css;document.head.appendChild(st);
const CRACK=`<svg class='crack' viewBox='0 0 20 26' aria-hidden='true'><path d='M2.5 13 L6 10.5 L8.5 14 L11.5 10 L14 13.5 L17.5 11' fill='none' stroke='#5b4a2e' stroke-width='1.4' stroke-linejoin='round' stroke-linecap='round'/></svg>`;
// grid-local box (origin = the grid's padding box, where the absolute layer sits); works for HTML and SVG elements
function rect(el,grid){const G=grid.getBoundingClientRect(),r=el.getBoundingClientRect();return{x:r.left-G.left-grid.clientLeft,y:r.top-G.top-grid.clientTop,w:r.width,h:r.height}}
function sounds(list){if(!window.SFX||!SFX.play)return;list.sort((a,b)=>a.t-b.t).forEach(s=>SFX.play(s.name,{delay:s.t}))}
/* opts: {order, pairs, kind:'caterpillar'|'squid', tint:(gene)=>({body,spots?}), next, reduced, hold, commit:()=>void}
   order[j] = index into next of the child shown in cell j (the page's shuffle of the new generation);
   pairs = survivor indices in pairing order (pair k = pairs[2k], pairs[2k+1]); commit() sets pop + gen and calls render(). */
window.hatchPhase=async function(grid,o){
 const rm=!!o.reduced,log={kind:o.kind,moves:[],t0:performance.now()};window.__lastHatch=log;
 await sleep(o.hold!==undefined?o.hold:H.hold);
 let committed=false;const commit=()=>{if(!committed){committed=true;o.commit()}};
 try{
 if(getComputedStyle(grid).position==='static')grid.style.position='relative';
 // snapshot the old grid (parents with hearts+eggs, eaten and stamped cells)
 const live=[...grid.querySelectorAll(':scope > .org')];
 const old=live.map(c=>{const node=c.cloneNode(true);node.querySelectorAll('.breed').forEach(b=>b.classList.remove('anim'));return{r:rect(c,grid),node}});
 const eggPos={};live.forEach((c,i)=>{const e=c.querySelector('.breed .egg')||c.querySelector('.breed');if(e){const br=rect(e,grid);eggPos[i]={x:br.x+br.w/2,y:br.y+br.h/2}}});
 commit();
 const cells=[...grid.querySelectorAll(':scope > .org')];cells.forEach(c=>c.setAttribute('data-unborn',''));
 const layer=document.createElement('div');layer.className='hatch-layer';grid.appendChild(layer);
 const ghosts=old.map(c=>{const g=document.createElement('div');g.className='ghost';const r=c.r;g.style.cssText=`left:${r.x}px;top:${r.y}px;width:${r.w}px;height:${r.h}px`;
  c.node.removeAttribute('title');g.appendChild(c.node);layer.appendChild(g);return g});
 const childToCell={};o.order.forEach((ci,j)=>childToCell[ci]=j);
 if(rm){
  cells.forEach(c=>c.removeAttribute('data-unborn'));
  const fades=cells.map(c=>c.animate([{opacity:0},{opacity:1}],{duration:H.reducedFade,easing:'ease-out'}).finished);
  ghosts.forEach(g=>g.animate([{opacity:1},{opacity:0}],{duration:H.reducedFade,fill:'forwards'}));
  for(let ci=0;ci<o.next.length;ci++){const k=ci>>2,from=o.pairs[2*k+(ci%2)];log.moves.push({child:ci,pair:k,from,to:childToCell[ci],color:o.tint(o.next[ci]).body,reduced:true})}
  await Promise.all(fades);layer.remove();log.end=performance.now();return}
 const B=window.BABY_SVGS[o.kind],snd=[],jobs=[];
 // non-egg content of the old cells fades out as the eggs start to hatch
 ghosts.forEach(g=>[...g.firstChild.children].forEach(ch=>{if(!ch.classList.contains('breed'))ch.animate([{opacity:getComputedStyle(ch).opacity},{opacity:0}],{duration:H.ghostFade,fill:'forwards'})}));
 const parents=[...new Set(o.pairs)].filter(i=>eggPos[i]);
 parents.forEach((p,k)=>{const t=k*H.eggStagger,b=ghosts[p].querySelector('.breed'),egg=b.querySelector('.egg');
  egg.insertAdjacentHTML('beforeend',CRACK);const cr=egg.querySelector('.crack');
  egg.getAnimations().forEach(a=>a.cancel());
  egg.animate([{transform:'rotate(0)'},{transform:'rotate(-14deg)'},{transform:'rotate(12deg)'},{transform:'rotate(0)'}],{duration:H.wobble,delay:t});
  cr.animate([{opacity:0},{opacity:1}],{duration:60,delay:t+H.crack,fill:'forwards'});
  egg.animate([{transform:'scale(1)',opacity:1},{transform:'scale(1.5)',opacity:0}],{duration:160,delay:t+H.pop-60,fill:'forwards',easing:'ease-out'});
  b.querySelector('.heart').animate([{opacity:1},{opacity:0}],{duration:250,delay:t+H.pop,fill:'forwards'});
  snd.push({name:'hatch',t})});
 const pk={};parents.forEach((p,k)=>pk[p]=k);
 const seen={};
 for(let ci=0;ci<o.next.length;ci++){
  const k=ci>>2,from=o.pairs[2*k+(ci%2)],to=childToCell[ci],nth=seen[from]=(seen[from]||0)+1;
  const start=(pk[from]||0)*H.eggStagger+H.pop+(nth-1)*H.second;
  const cell=cells[to],cr=rect(cell,grid),svg=cell.querySelector(':scope > svg'),sr=svg?rect(svg,grid):cr;
  const A=eggPos[from]||{x:old[from].r.x+old[from].r.w/2,y:old[from].r.y+old[from].r.h/2},Z={x:sr.x+sr.w/2,y:sr.y+sr.h/2};
  const tint=o.tint(o.next[ci]),w=Math.max(18,cr.w*H.size),h=w*B.aspect;
  const el=document.createElement('div');el.className='baby '+o.kind;el.dataset.child=ci;el.dataset.to=to;el.dataset.from=from;el.dataset.color=tint.body;
  el.style.width=w+'px';el.style.height=h+'px';el.style.opacity='0';
  el.innerHTML=`<div class='body' style='width:100%;height:100%'>${B.svg(tint)}</div>`;layer.appendChild(el);
  const dx=Z.x-A.x,dy=Z.y-A.y,d=Math.hypot(dx,dy),ang=Math.atan2(dy,dx)*180/Math.PI-B.heading;
  const flip=o.kind==='caterpillar'&&Math.abs(Math.atan2(dy,dx))>Math.PI/2?' scaleY(-1)':'';
  const dur=Math.round(Math.min(H.maxTravel,Math.max(H.minTravel,600+d*H.perPx))),stride=H.stride[o.kind],n=Math.max(2,Math.round(dur/stride));
  const at=(f)=>`translate(${(A.x+dx*f-w/2).toFixed(1)}px,${(A.y+dy*f-h/2).toFixed(1)}px) rotate(${ang.toFixed(1)}deg)${flip}`;
  // one surge per stride: the caterpillar inches, the squid jets (ease-out per segment)
  const kf=[];for(let i=0;i<=n;i++)kf.push({transform:at(i/n),offset:i/n,easing:o.kind==='squid'?'cubic-bezier(.2,.8,.4,1)':'ease-in-out'});
  kf.unshift({transform:at(0)+' scale(.3)',opacity:0,offset:0});kf[1]={...kf[1],offset:Math.min(.12,1/n/2),opacity:1};
  for(let i=2;i<kf.length;i++)kf[i].opacity=1;
  const mv={child:ci,pair:k,from,to,color:tint.body,start,travel:dur};log.moves.push(mv);
  snd.push({name:o.kind==='squid'?'swim':'inch',t:start},{name:'grow',t:start+dur});
  jobs.push((async()=>{
   const a=el.animate(kf,{duration:dur,delay:start,fill:'forwards'});await a.finished;
   const end=at(1);
   el.animate([{transform:end,opacity:1},{transform:end+' scale(1.9)',opacity:0}],{duration:H.grow,fill:'forwards',easing:'ease-in'});
   cell.removeAttribute('data-unborn');
   const g=[];[...cell.children].forEach(ch=>{if(ch.tagName.toLowerCase()==='svg')g.push(ch.animate([{transform:'scale(.3)',opacity:0},{transform:'scale(1)',opacity:1}],{duration:H.grow,easing:'cubic-bezier(.3,1.4,.6,1)'}).finished);
    else g.push(ch.animate([{opacity:0},{opacity:1}],{duration:H.grow}).finished)});
   await Promise.all(g);mv.arrived=performance.now()-log.t0})());
 }
 sounds(snd);
 await Promise.all(jobs);
 layer.remove();
 }catch(e){console.error(e);commit()}
 finally{grid.querySelectorAll('.org[data-unborn]').forEach(c=>c.removeAttribute('data-unborn'));const l=grid.querySelector('.hatch-layer');if(l)l.remove();log.end=performance.now()}
};
window.HATCH=H;
})();
